"""
CTF Agent - ReAct pattern implementation
Reasoning and Acting in cycles with focused memory
"""

import openai
import docker
import json
import re
import os
import sys
import yaml
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class CTFChallenge:
    """Represents a single CTF challenge"""
    task: str
    flag: str
    target: str
    vulnerability: str


class ReActCTFAgent:
    """
    CTF Agent using ReAct pattern: Reason -> Act -> Observe cycle
    """
    
    def __init__(self, 
                 api_key: str,
                 base_url: str,
                 model: str,
                 config_path: str = "/app/config.yaml",
                 output_dir: str = None):
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        
        self.docker_client = docker.from_env()
        kali_container = self.config['docker']['kali_container']
        self.kali = self.docker_client.containers.get(kali_container)
        
        self.memory_window = self.config['agent']['memory_window']
        self.full_history: List[Dict] = []
        
        self.command_history: List[Dict] = []
        self.flag_attempts: List[str] = []
        
        if output_dir is None:
            output_dir = self.config['output']['base_dir']
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.prompts = self.config['prompts']
        self.messages = self.config['messages']
        self.display = self.config['display']
    
    def execute_command(self, command: str) -> Tuple[str, int, Dict]:
        """Execute a command in Kali container"""
        print(f"\n{self.display['separator_main']}")
        print(self.messages['executing_command_header'])
        print(self.display['separator_main'])
        print(self.messages['command_info'].format(command=command))
        print(self.messages['container_info'].format(name=self.kali.name))
        print(self.messages['container_status'].format(status=self.kali.status))
        
        log_entry = {
            "command": command,
            "timestamp": datetime.now().isoformat(),
            "status": "failed"
        }
        
        try:
            self.kali.reload()
            if self.kali.status != 'running':
                error_msg = self.prompts['container_not_running'].format(status=self.kali.status)
                print(self.messages['error_label'].format(message=error_msg))
                log_entry["output"] = error_msg
                log_entry["exit_code"] = -1
                log_entry["error"] = error_msg
                self.command_history.append(log_entry)
                return error_msg, -1, log_entry
            
            # Use sh instead of bash for better compatibility
            result = self.kali.exec_run(
                cmd=['/bin/sh', '-c', command],
                demux=True,
                stdin=False,
                tty=False,
                stream=False
            )
            
            stdout = result.output[0].decode() if result.output[0] else ""
            stderr = result.output[1].decode() if result.output[1] else ""
            output = stdout + stderr
            
            log_entry["output"] = output
            log_entry["stdout"] = stdout
            log_entry["stderr"] = stderr
            log_entry["exit_code"] = result.exit_code
            log_entry["status"] = "success" if result.exit_code == 0 else "failed"
            
            print(self.messages['exit_code'].format(code=result.exit_code))
            print(self.messages['status'].format(status=log_entry['status']))
            if stdout:
                print(f"\n{self.messages['stdout_label']}\n{stdout}")
            if stderr:
                print(f"\n{self.messages['stderr_label']}\n{stderr}")
            if not stdout and not stderr:
                print(f"\n{self.messages['no_output']}")
            
            self.command_history.append(log_entry)
            return output, result.exit_code, log_entry
            
        except Exception as e:
            error_msg = self.prompts['docker_error'].format(error=str(e))
            log_entry["output"] = error_msg
            log_entry["exit_code"] = -1
            log_entry["error"] = str(e)
            
            print(self.messages['error_label'].format(message=error_msg))
            import traceback
            print(f"{self.messages['traceback_label']}\n{traceback.format_exc()}")
            
            self.command_history.append(log_entry)
            return error_msg, -1, log_entry
    
    def extract_command(self, text: str) -> Optional[str]:
        """Extract single EXECUTE: command from response"""
        pattern = r'EXECUTE:\s*(.+?)(?:\n|$)'
        matches = re.findall(pattern, text, re.MULTILINE | re.IGNORECASE)
        return matches[0].strip() if matches else None
    
    def extract_thought(self, text: str) -> Optional[str]:
        """Extract THOUGHT: section from response"""
        pattern = r'THOUGHT:\s*(.+?)(?=ACTION:|EXECUTE:|FLAG:|$)'
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else None
    
    def extract_action(self, text: str) -> Optional[str]:
        """Extract ACTION: description from response"""
        pattern = r'ACTION:\s*(.+?)(?=EXECUTE:|FLAG:|$)'
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else None
    
    def extract_flags(self, text: str) -> List[str]:
        """Extract FLAG: submissions"""
        flags = []
        pattern = r'FLAG:\s*([^\s\n]+)'
        flags.extend(re.findall(pattern, text, re.IGNORECASE))
        flag_pattern = r'(FLAG\{[^}]+\})'
        flags.extend(re.findall(flag_pattern, text, re.IGNORECASE))
        return list(set(flags))
    
    def get_recent_context(self) -> List[Dict]:
        """Get recent conversation for LLM context (sliding window)"""
        if len(self.full_history) <= self.memory_window * 2:
            return self.full_history
        
        return [self.full_history[0]] + self.full_history[-(self.memory_window * 2):]
    
    def solve_challenge(self, challenge: CTFChallenge) -> Tuple[bool, Optional[str]]:
        """Solve challenge using ReAct pattern"""
        print(f"\n{self.display['separator_main']}")
        print(self.messages['challenge_start_header'])
        print(self.display['separator_main'])
        print(self.messages['target'].format(target=challenge.target))
        print(self.messages['vulnerability'].format(vulnerability=challenge.vulnerability))
        print(f"Task:\n{challenge.task}")
        print(f"{self.display['separator_main']}\n")
        
        self.full_history = []
        self.command_history = []
        self.flag_attempts = []
        
        initial_message = self.prompts['challenge_start'].format(
            target=challenge.target,
            vulnerability=challenge.vulnerability,
            task=challenge.task
        )

        self.full_history.append({
            "role": "user",
            "content": initial_message
        })
        
        max_iterations = self.config['agent']['max_iterations']
        for iteration in range(max_iterations):
            print(f"\n{self.display['separator_iteration']}")
            print(self.messages['iteration_header'].format(current=iteration + 1, max=max_iterations))
            print(f"{self.display['separator_iteration']}\n")
            
            context = self.get_recent_context()
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": self.prompts['system']}] + context,
                temperature=self.config['agent']['temperature'],
                max_tokens=self.config['agent']['max_tokens']
            )
            
            agent_response = response.choices[0].message.content
            
            self.full_history.append({
                "role": "assistant",
                "content": agent_response
            })
            
            thought = self.extract_thought(agent_response)
            action = self.extract_action(agent_response)
            command = self.extract_command(agent_response)
            
            print(f"{self.display['separator_main']}")
            print(self.messages['agent_reasoning_header'])
            print(self.display['separator_main'])
            if thought:
                print(f"THOUGHT:\n{thought}\n")
            if action:
                print(f"ACTION:\n{action}\n")
            
            flags = self.extract_flags(agent_response)
            if flags:
                for flag in flags:
                    flag_clean = flag.strip()
                    if flag_clean not in self.flag_attempts:
                        self.flag_attempts.append(flag_clean)
                        print(f"\n{self.display['separator_main']}")
                        print(self.messages['flag_submission_header'])
                        print(self.display['separator_main'])
                        print(self.messages['submitted'].format(flag=flag_clean))
                        print(self.messages['expected'].format(flag=challenge.flag))
                        
                        if flag_clean == challenge.flag:
                            print(self.messages['result_correct'])
                            print(f"{self.display['separator_main']}\n")
                            return True, flag_clean
                        else:
                            print(self.messages['result_incorrect'])
                            print(f"{self.display['separator_main']}\n")
                
                feedback = self.prompts['flag_incorrect'].format(
                    attempts=', '.join(self.flag_attempts)
                )
                
                self.full_history.append({
                    "role": "user",
                    "content": feedback
                })
                continue
            
            if command:
                output, exit_code, log_entry = self.execute_command(command)
                
                print(f"\n{self.display['separator_main']}")
                print(self.messages['observation_header'])
                print(f"{self.display['separator_main']}")
                
                if exit_code == 0:
                    observation = self.prompts['observation_success'].format(
                        command=command,
                        output=output if output else self.messages['no_output']
                    )
                else:
                    observation = self.prompts['observation_failure'].format(
                        command=command,
                        exit_code=exit_code,
                        output=output if output else self.messages['no_output']
                    )
                
                print(observation[:500] + "..." if len(observation) > 500 else observation)
                print(f"{self.display['separator_main']}\n")
                
                self.full_history.append({"role": "user", "content": observation})
            else:
                if not flags:
                    prompt = self.prompts['prompt_for_command']
                    self.full_history.append({"role": "user", "content": prompt})
                    print(f"\n{self.display['separator_main']}")
                    print(self.messages['prompting_agent_header'])
                    print(f"{self.display['separator_main']}\n")
        
        print(f"\n{self.display['separator_main']}")
        print(self.messages['challenge_failed_header'])
        print(self.display['separator_main'])
        print(self.messages['max_iterations_reached'].format(max=max_iterations))
        print(self.messages['flag_attempts_count'].format(count=len(self.flag_attempts)))
        print(self.messages['commands_executed_count'].format(count=len(self.command_history)))
        print(f"{self.display['separator_main']}\n")
        
        return False, None
    
    def save_challenge_log(self, challenge: CTFChallenge, success: bool, flag: Optional[str]):
        """Save detailed log of challenge attempt"""
        log = {
            "challenge": {
                "target": challenge.target,
                "vulnerability": challenge.vulnerability,
                "task": challenge.task,
                "expected_flag": challenge.flag
            },
            "result": {
                "success": success,
                "captured_flag": flag,
                "flag_attempts": self.flag_attempts,
                "total_commands": len(self.command_history),
                "successful_commands": sum(1 for cmd in self.command_history if cmd.get('exit_code') == 0),
                "failed_commands": sum(1 for cmd in self.command_history if cmd.get('exit_code') != 0)
            },
            "commands": self.command_history,
            "full_conversation": self.full_history
        }
        
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            filename = self.output_dir / f"{challenge.target}.json"
            with open(filename, 'w') as f:
                json.dump(log, f, indent=2)
            print(f"\n{self.messages['log_saved'].format(filename=filename)}")
        except Exception as e:
            print(f"\n{self.messages['log_save_warning'].format(error=e)}")
            print(self.messages['log_save_attempt'].format(path=self.output_dir))
            print(f"\n{self.messages['log_stdout_fallback']}")
            print(json.dumps(log, indent=2))
    
    def run_challenges(self, challenges_file: str) -> Dict:
        """Run all challenges from JSON file"""
        print(self.messages['loading_challenges'].format(file=challenges_file))
        
        with open(challenges_file, 'r') as f:
            data = json.load(f)
        
        challenges = [
            CTFChallenge(**challenge_data)
            for challenge_data in data['in-vitro']['binary']
        ]
        
        print(self.messages['total_challenges'].format(count=len(challenges)))
        
        results = []
        for i, challenge in enumerate(challenges, 1):
            success, flag = self.solve_challenge(challenge)
            
            result = {
                "challenge_num": i,
                "target": challenge.target,
                "vulnerability": challenge.vulnerability,
                "success": success,
                "flag": flag,
                "flag_attempts": len(self.flag_attempts),
                "commands_executed": len(self.command_history),
                "successful_commands": sum(1 for cmd in self.command_history if cmd.get('exit_code') == 0)
            }
            results.append(result)
            
            self.save_challenge_log(challenge, success, flag)
            
            status = "SOLVED" if success else "FAILED"
            print(f"\n{self.display['separator_main']}")
            print(self.messages['challenge_complete_header'].format(num=i, status=status))
            print(f"{self.display['separator_main']}\n")
        
        summary = self._generate_summary(results)
        self._save_summary(summary)
        self._print_summary(summary)
        
        return summary
    
    def _generate_summary(self, results: List[Dict]) -> Dict:
        """Generate summary statistics"""
        solved = sum(1 for r in results if r['success'])
        total = len(results)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_challenges": total,
            "solved": solved,
            "failed": total - solved,
            "success_rate": f"{(solved/total)*100:.1f}%" if total > 0 else "0%",
            "results": results
        }
    
    def _save_summary(self, summary: Dict):
        """Save summary to file"""
        filename = self.output_dir / "summary.json"
        with open(filename, 'w') as f:
            json.dump(summary, f, indent=2)
    
    def _print_summary(self, summary: Dict):
        """Print summary to console"""
        print(f"\n{self.display['separator_main']}")
        print(self.messages['final_summary_header'])
        print(self.display['separator_main'])
        print(self.messages['solved_count'].format(
            solved=summary['solved'], 
            total=summary['total_challenges']
        ))
        print(self.messages['success_rate'].format(rate=summary['success_rate']))
        print()
        
        for result in summary['results']:
            status = "PASS" if result['success'] else "FAIL"
            print(f"[{status}] Challenge {result['challenge_num']}: {result['target']}")
            print(f"      Type: {result['vulnerability']}")
            if result['success']:
                print(f"      Flag: {result['flag']}")
            print(f"      Commands: {result['commands_executed']} ({result['successful_commands']} successful)")
            print()


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python ctf_agent.py <challenges.json>")
        sys.exit(1)
    
    challenges_file = sys.argv[1]
    
    if not os.path.exists(challenges_file):
        print(f"Error: File not found: {challenges_file}")
        sys.exit(1)
    
    api_key = os.getenv("OPENAI_API_KEY", "not-needed")
    base_url = os.getenv("OPENAI_BASE_URL", "http://localhost:8000/v1")
    model = os.getenv("MODEL_NAME", "your-model")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"/app/output/{timestamp}"
    
    print("="*80)
    print("CTF AGENT - ReAct Pattern")
    print("="*80)
    print(f"API: {base_url}")
    print(f"Model: {model}")
    print(f"Output: {output_dir}")
    print(f"Challenges: {challenges_file}")
    print("="*80)
    print()
    
    agent = ReActCTFAgent(
        api_key=api_key,
        base_url=base_url,
        model=model,
        config_path="/app/config.yaml",
        output_dir=output_dir
    )
    
    agent.run_challenges(challenges_file)


if __name__ == "__main__":
    main()