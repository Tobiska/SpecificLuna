import subprocess
from abc import ABC, abstractmethod
from enviroment import Status
import stage
import os

"""
    Executor - класс, который берёт всю известную информацию о этапе и выполняет
    в нужном окружении
"""

class ReaderWriter(ABC):
    @abstractmethod
    def write(self):
        pass

    @abstractmethod
    def read(self):
        pass


class Executor:
    def Exec(self, stage:stage.Stage) -> Status:
        env = stage.get_environment()
        status = self.validate_requirements(stage.get_requirements(), env)
        if not status.is_success():
            return status
        return env.execute_command(stage.get_command().bash_command)

    def validate_requirements(self, requirements:[stage.Requirement], environment) -> Status:
        for requirement in requirements:
            status = environment.check(requirement)
            if not status.is_success():
                return status
        return Status(
            return_code=0,
            message="Validate Successes"
        )

    def Run(self, root:stage.Stage):
        self.current_stage = root
        for stage in self.current_stage.next():
            status = self.Exec(stage)
            if status == 0:
                self.current_stage = stage
            else:
                self.current_stage = stage.reset_branch()
        return
