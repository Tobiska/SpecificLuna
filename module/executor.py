from abc import ABC, abstractmethod
from module.enviroment import Status
import module.logger as log
import module.stage as stage
from module.config import cfg

logger = log.init_logger("DEBUG", "../build.log")

class ReaderWriter(ABC):
    @abstractmethod
    def write(self):
        pass

    @abstractmethod
    def read(self):
        pass


class Executor:
    def _exec(self, stage: stage.Stage) -> Status:
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

    def do_cleanup(self, stage):
        env = stage.get_environment()
        env.cleanup(stage.meta.cleanup_results)


    def Run(self, root: stage.Stage):
        self.parent_stage = root
        while True:
            self.current_stage = self.parent_stage.next()
            if self.current_stage is None:
                if cfg.cleanup:
                    self.do_cleanup(self.parent_stage)
                break
            status = self._exec(self.current_stage)
            if status.is_success():
                logger.info(f"Branch Tag: {self.current_stage.meta.tag} {type(self.current_stage).__name__} is done.\n{status}")
                self.parent_stage = self.current_stage
            else:
                logger.error(f"Branch Tag: {self.current_stage.meta.tag} {type(self.current_stage).__name__} is failed\n {status}")
                self.parent_stage = self.current_stage.reset_branch()
                if cfg.cleanup:
                    self.do_cleanup(self.current_stage)


