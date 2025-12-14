import docker
import tarfile
import io

class DockerSandbox:
    def __init__(self, image: str = "python:3.10-slim"):
        self.client = docker.from_env()
        self.image = image

    def run_code(self, code: str, timeout: int = 30) -> str:
        """Runs python code in an ephemeral container."""
        # Wrap code to print to stdout
        wrapped = f"try:\n{self._indent(code)}\nexcept Exception as e:\n    print(e)"
        
        try:
            container = self.client.containers.run(
                self.image,
                command=["python", "-c", wrapped],
                mem_limit="512m",
                network_disabled=True, # L5 Hardening: No Internet
                detach=True
            )
            
            exit_code = container.wait(timeout=timeout)
            logs = container.logs().decode('utf-8')
            container.remove()
            return logs
            
        except Exception as e:
            return f"Sandbox Error: {str(e)}"

    def _indent(self, text: str) -> str:
        return "\n".join("    " + line for line in text.splitlines())
