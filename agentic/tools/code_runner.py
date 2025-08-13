import subprocess


class CodeRunner:
    def __init__(self, timeout:int):
        self.timeout=timeout
        
    def run_python(self, code_snippet:str):
        namespace={}
        print(code_snippet)
        exec(code_snippet, namespace)
        return namespace
    
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
