import subprocess
from abc import ABC, abstractmethod
from enviroment import Status
import logger as log
import stage

logger = log.init_logger("DEBUG", "build.log")

class ReaderWriter(ABC):
    @abstractmethod
    def write(self):
        pass

    @abstractmethod
    def read(self):
        pass


class Executor:
    def _exec(self, stage:stage.Stage) -> Status:
        env = stage.get_environment()
        status = self._validate_requirements(stage.get_requirements(), env)
        if not status.is_success():
            return status
        return env.execute_command(stage.get_command())

    def _validate_requirements(self, requirements:[stage.Requirement], environment) -> Status:
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
        while True:
            if self.current_stage is None:
                break
            status = self._exec(self.current_stage)
            if status.is_success():
                logger.info(f"{type(self.current_stage).__name__} is done")
                self.current_stage = self.current_stage.next()
            else:
                logger.error(f"{type(self.current_stage).__name__} {status}")
                self.current_stage = self.current_stage.reset_branch()
