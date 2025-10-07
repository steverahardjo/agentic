import subprocess
import sys
import io
import re

class CodeRunner:
    def __init__(self, timeout:int):
        self.timeout=timeout
        
    def run_python(self, code_snippet:str):
<<<<<<< HEAD
        return exec(code_snippet)
=======
        """
        Tool function to create run using exec sandboxed
        args:
        - code_snippet = we want to  run
        """
        match = re.search(r"```python\s+(.*?)```", code_snippet, re.DOTALL)
        if match:
            res= match.group(1).strip()
        return ""
        return exec(res)
    
>>>>>>> 305b317 (tool is working for webscraper, but not for code)
    
    def run_shell(self, command:str)->str:
        try:
            result = subprocess.run(
                command, shell=True, capture_output = True, text = True, timeout = self.timeout
            )
            return {
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "returncode": result.returncode
            }
            
        except Exception as e:
            return {"stdout": "", "stderr": str(e), "returncode": -1}      
