from module.stage import *


class TestStage(Stage):
    def __init__(self, result, requirement=None):
        super().__init__()

        self.requirement = requirement

        self.result = result

    def get_requirements(self) -> [Requirement]:
        return [self.requirement]

    def get_results(self) -> [Result]:
        return [self.result]

    def get_command(self) -> Command:
        cmd = f'{self.result}'
        return Command(
            bash_command=cmd
        )