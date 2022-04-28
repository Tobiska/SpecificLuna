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
    def __init__(self, message, return_code):
        self.message = message
        self.return_code = return_code

    def is_success(self) -> bool:
        return True if self.return_code == 0 else False

    def __str__(self):
        return f'Status command finished with code: {self.return_code}\n' \
               f'Message: {self.message}'


class Environment(ABC):
    @abstractmethod
    def execute_command(self, cmd) -> Status:
        pass

    @abstractmethod
    def check(self, requirement) -> Status:
        pass

    def collect_status(self, process) -> Status:
        message = reduce(lambda m, ln: m + ln, process.stdout)
        return Status(
            message=message,
            return_code=process.returncode,
        )


class LocalEnvironment(Environment):
    def __init__(self, key_environment):
        local = environments[key_environment]
        self.user = local["user"]
        self.password = local["password"]

    def check(self, requirement) -> Status:
        if os.path.isfile(requirement):
            status = Status(return_code=0, message="Success")
        else:
            status = Status(return_code=1, message=f"Requirement {requirement} is absent")
        return status

    def execute_command(self, cmd) -> Status:
        process = subprocess.Popen(f'su {self.user} -c {cmd}',
                                       stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE,
                                       universal_newlines=True,
                                       bufsize=0
                                       )
        process.stdin.write(self.password)
        return super().collect_status(process=process)


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


