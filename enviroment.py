import os.path
import subprocess
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
    def __init__(self, message=None, error=None, return_code=0):
        self.message = message
        self.error = error
        self.return_code = return_code

    def is_success(self) -> bool:
        return True if self.return_code == 0 else False

    def __str__(self):
        if self.return_code != 0:
            return f'Status command finished with code: {self.return_code}\n' \
                   f'Error: {self.error}' \
                   f'Message: {self.message}'
        else:
            return f'Status command finished with code: {self.return_code}\n' \
                   f'Message: {self.message}'


class Environment(ABC):
    @abstractmethod
    def execute_command(self, cmd) -> Status:
        pass

    @abstractmethod
    def check(self, requirement) -> Status:
        pass

    def collect_status(self, err, message, returncode) -> Status:
        return Status(
            message=message,
            error=err,
            return_code=returncode,
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

    def execute_command(self, cmd) -> Status:
        if type(cmd.bash_command) is str:
            shell_flag = True
        else:
            shell_flag = False

        process = subprocess.run(cmd.bash_command,
                                 stderr=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 shell=shell_flag,
                                 encoding='utf-8',
                                 input=cmd.input,
                                 env=cmd.environment,
                                 )
        if cmd.output_type is cmd.FILE:
            open(cmd.output_file,
                     'w').write(process.stdout)
        elif cmd.output_type is cmd.STDOUT:
            print(process.stdout)
        return super().collect_status(message=process.stdout, err=process.stderr,
                                      returncode=process.returncode)


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
