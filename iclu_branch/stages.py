from module import stage
from module.stage import Command, Requirement, Result
from module.config import cfg

class Preprocessor(stage.Stage):
    def __init__(self):
        super().__init__()

        self.interpreter = Requirement(
            requirement=f'{cfg.python}'
        )

        self.preprocessor = Requirement(
            requirement=f'{cfg.iclu_home}/bin/preprocessor.py'
        )

        self.preprocessed_program = Result(
            result=f'{cfg.build_dir}/preprocessed.fa'
        )

        self.program = Requirement(
            requirement=f'{cfg.program}'
        )

    def get_requirements(self) -> [Requirement]:
        return [self.preprocessor, self.program]

    def get_results(self) -> [Result]:
        return [self.preprocessed_program]

    def get_command(self) -> Command:
        cmd = f'{self.interpreter} {self.preprocessor} < {self.program} > {self.preprocessed_program}'
        return Command(
            bash_command=cmd
        )


class Parser(stage.Stage):
    def __init__(self):
        super().__init__()
        self.parser = Requirement(
            requirement=f'{cfg.iclu_home}/bin/iclu-parser'
        )

        self.preprocessed_program = Requirement(
            requirement=f'{cfg.build_dir}/preprocessed.fa'
        )

        self.result_program = Result(
            result=f'{cfg.build_dir}/program_parsed.ja'
        )

    def get_requirements(self) -> [Requirement]:
        return [self.parser, self.preprocessed_program]

    def get_results(self) -> [Result]:
        return [self.result_program]

    def get_command(self) -> Command:
        cmd = f'{self.parser} < {self.preprocessed_program} > {self.result_program}'
        return Command(
            bash_command=cmd
        )


class Compiler(stage.Stage):
    def __init__(self):
        super().__init__()
        self.compiler = Requirement(
            requirement=f'{cfg.iclu_home}/bin/luic'
        )
        self.program = Requirement(
            requirement=f'{cfg.build_dir}/program_parsed.ja'
        )

        self.compiled_program = Requirement(
            requirement=f'{cfg.build_dir}/compiled.c'
        )

    def get_requirements(self) -> [Requirement]:
        return [self.compiler, self.program]

    def get_results(self) -> [Result]:
        return [self.compiled_program]

    def get_command(self) -> Command:
        cmd = f'{self.compiler} {self.program} {self.compiled_program}'
        return Command(
            bash_command=cmd
        )


class Runner(stage.Stage):
    def __init__(self):
        super().__init__()
        self.env_library = Requirement(
            requirement=f"{cfg.iclu_home}/iclu-libucenvhelpher"
        )

        self.program = Requirement(
            requirement=f"{cfg.build_dir}/compiled.c"
        )

        self.mpicxx = Requirement(
            f"{cfg.iclu_home}"
        )

        self.ldflags = f"-L {self.env_library}"

    def get_requirements(self) -> [Requirement]:
        return [self.env_library, self.mpicxx, self.program]

    def get_results(self) -> [Result]:
        return []

    def get_command(self) -> Command:
        cmd = f'{self.mpicxx} {self.program} {self.ldflags}'
        return Command(
            bash_command=cmd
        )


