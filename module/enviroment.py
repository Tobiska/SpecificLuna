import os.path
import subprocess
import time
from abc import ABC, abstractmethod
from functools import reduce

environments = {
    "abc_virtual": {
        "host": "192.168.0.1",
        "port": "22",
        "user": "user",
        "password": "password"
    },
    "local": {
        "user": "root",
        "password": "root"
    }
}


class Status:
    def __init__(self, execution_time=0, message=None, error=None, return_code=0):
        self.message = message
        self.error = error
        self.return_code = return_code
        self.execution_time = execution_time

    def is_success(self) -> bool:
        return True if self.return_code == 0 else False

    def __str__(self):
        if self.return_code != 0:
            return f"Status command finished with code: {self.return_code}\n" \
                   f"Error: {self.error}\n" \
                   f"Message: {self.message}\n" \
                   f"Time: {self.execution_time}\n"
        else:
            return f"Time: {self.execution_time}"


class Environment(ABC):
    @abstractmethod
    def execute_command(self, cmd) -> Status:
        pass

    @abstractmethod
    def check(self, requirement) -> Status:
        pass

    @abstractmethod
    def cleanup(self, paths):
        pass

    def collect_status(self, err, message, returncode, execution_time) -> Status:
        return Status(
            message=message,
            error=err,
            return_code=returncode,
            execution_time=execution_time
        )


class LocalEnvironment(Environment):
    def __init__(self, key_environment):
        local = environments[key_environment]
        self.user = local["user"]
        self.password = local["password"]

    def check(self, requirement) -> Status:
        if os.path.exists(str(requirement)):
            status = Status(return_code=0, message="Success")
        else:
            status = Status(return_code=1, message=f"Requirement {requirement} is absent")
        return status

    def cleanup(self, paths):
        for path in paths:
            if os.path.exists(str(path)):
                os.remove(str(path))

    def format_print_result(self, out):
        print(f"-----------------------------------------------------------------\n"
              f"{out}"
              f"-----------------------------------------------------------------\n")

    def execute_command(self, cmd) -> Status:
        if type(cmd.bash_command) is str:
            shell_flag = True
        else:
            shell_flag = False

        start_time = time.perf_counter()
        process = subprocess.run(cmd.bash_command,
                                 stderr=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 shell=shell_flag,
                                 encoding='utf-8',
                                 input=cmd.input,
                                 env=cmd.environment,
                                 )
        end_time = time.perf_counter()
        if cmd.output_type is cmd.FILE:
            open(cmd.output_file,
                     'w').write(process.stdout)
        elif cmd.output_type is cmd.STDOUT:
            print(process.stdout)
        return super().collect_status(message=process.stdout,
                                      err=process.stderr,
                                      returncode=process.returncode,
                                      execution_time=(end_time - start_time))


class RemoteSshEnvironment(Environment):
    def __init__(self, key_environment):
        remote = environments[key_environment]
        self.host = remote["host"]
        self.port = remote["port"]
        self.user = remote["user"]
        self.password = remote["password"]

    def execute_command(self, cmd) -> Status:
        ssh_process = subprocess.Popen(f'ssh {self.user}@{self.host} -p {self.port}',
                                       stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE,
                                       universal_newlines=True,
                                       bufsize=0
                                       )
        ssh_process.stdin.write(self.password)
        ssh_process.stdin.write(cmd)
        ssh_process.stdin.close()

        return super().collect_status(process=ssh_process)
