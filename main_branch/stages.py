import stage
from stage import Command, Requirement
from main import cfg


class BuildLibUcodes(stage.Stage):
    def __init__(self):
        super().__init__()
        self.make = None
        self.makefile = None

    def get_requirements(self) -> [Requirement]:
        #python3, pp.py, $PROGRAM
        self.make = Requirement(
            requirement=f'make'
        )
        self.makefile = Requirement(
            requirement=f'${cfg.get("BUILD_DIR")}/Makefile.libucodes'
        )
        return [self.make, self.makefile]

    def get_command(self) -> Command:
        cmd = f'${self.make} -j8 -f ${self.makefile}'
        return Command(
            bash_command=cmd
        )

class GenerateBlocks(stage.Stage):
    def __init__(self):
        super().__init__()
        self.generator = Requirement(
            requirement=f'${cfg.get("LUNA_HOME")}/scripts/generate_cpp_blocks.py'
        )
        self.interpreter = Requirement(
            requirement=f'${cfg.get("PYTHON")}'
        )
        self.headers = Requirement(
            requirement=f'${cfg.get("BUILD_DIR")}/headers.ja'
        )
        self.program = Requirement(
            requirement=f'${cfg.get("BUILD_DIR")}/program.ja'
        )
        self.preprocessed_text_information = Requirement(
            requirement=f'${cfg.get("BUILD_DIR")}/preprocessed.fa.ti'
        )
        self.block_text_information = Requirement(
            requirement=f'${cfg.get("BUILD_DIR")}/blocks.ti'
        )
        self.program_foreign = Requirement(
            requirement=f'${cfg.get("BUILD_DIR")}/program_foreign.ja'
        )
        self.foreign_blocks = Requirement(
            requirement=f'${cfg.get("BUILD_DIR")}/foreign_blocks.cpp'
        )
        self.foreign_blocks_text_information = Requirement(
            requirement=f'${cfg.get("BUILD_DIR")}/foreign_blocks.cpp.ti'
        )

    def get_requirements(self) -> [Requirement]:
        #python3, pp.py, $PROGRAM
        return [self.interpreter, self.generator, self.headers, self.program, self.preprocessed_text_information, self.block_text_information]

    def get_command(self) -> Command:
        cmd = f'${self.interpreter} ${self.generator} ${self.program} ${self.headers} ${self.preprocessed_text_information} ${self.program_foreign} ${self.foreign_blocks} ${self.foreign_blocks_text_information}'
        return Command(
            bash_command=cmd
        )

class GenerateMakefile(stage.Stage):
    def __init__(self):
        super().__init__()
        self.interpreter = None
        self.mkgen = None
        self.cxx = None
        self.cxx_flags = None
        self.ldflags = None

    def get_requirements(self) -> [Requirement]:
        #python3, pp.py, $PROGRAM
        self.interpreter =  self.interpreter = Requirement(
            requirement=f'${cfg.get("PYTHON")}'
        )
        self.mkgen = Requirement(
            requirement=f'${cfg.get("LUNA_HOME")}/scripts/mkgen'
        )
        self.cxx = Requirement(
            requirement=f'${cfg.get("CXX")}'
        )
        self.cxx_flags = Requirement(
            requirement=f'${cfg.get("CXX_FLAGS")}'
        )
        return [self.interpreter, self.mkgen, self.cxx]

    def get_command(self) -> Command:
        cmd = f'${self.interpreter} ${self.mkgen} --out=${cfg.get("BUILD_DIR")}/libucodes.so --compile-flags=${self.cxx_flags} --compiler=${self.cxx} --obj=${cfg.get("BUILD_DIR")} --src-stdin --link-flags=${self.ldflags} -shared -fPIC'
        return Command(
            bash_command=cmd
        )

class GenerateCppBlocks(stage.Stage):
    def __init__(self):
        super().__init__()
        self.interpreter = None
        self.fcmp2 = None
        self.cpp_block_info = None
        self.cpp = None
        self.recommendations = None

    def get_requirements(self) -> [Requirement]:
        #python3, pp.py, $PROGRAM
        self.fcmp2 = Requirement(
            requirement=f'${cfg.get("LUNA_HOME")}/scripts/fcmp2'
        )
        self.interpreter = Requirement(
            requirement=f'${cfg.get("PYTHON")}'
        )
        self.cpp_block_info = Requirement(
            requirement=f'${cfg.get("BUILD_DIR")}/cpp_blocks_info.json'
        )
        self.cpp = Requirement(
            requirement=f'${cfg.get("BUILD_DIR")}/test.cpp'
        )
        self.recommendations = Requirement(
            requirement=f'${cfg.get("BUILD_DIR")}/program_recom.ja'
        )
        return [self.interpreter, self.fcmp2, self.recommendations, self.cpp_block_info, self.cpp]

    def get_command(self) -> Command:
        cmd = f'${self.interpreter} ${self.fcmp2} ${self.recommendations} ${self.cpp} ${self.cpp_block_info}'
        return Command(
            bash_command=cmd
        )

class GenerateRecoms(stage.Stage):
    def __init__(self):
        super().__init__()
        self.interpreter = None
        self.fcmp = None
        self.foreign = None
        self.recom = None

    def get_requirements(self) -> [Requirement]:
        #python3, pp.py, $PROGRAM
        self.fcmp = Requirement(
            requirement=f'${cfg.get("LUNA_HOME")}/scripts/fcmp'
        )
        self.interpreter = Requirement(
            requirement=f'${cfg.get("PYTHON")}'
        )
        self.foreign = Requirement(
            requirement=f'${cfg.get("BUILD_DIR")}/program_foreign.ja'
        )
        self.recom = Requirement(
            requirement=f'${cfg.get("BUILD_DIR")}/program_recom.ja'
        )
        return [self.interpreter, self.fcmp, self.recom, self.foreign]

    def get_command(self) -> Command:
        cmd = f'${self.interpreter} ${self.fcmp} ${self.foreign} -h ${self.recom} --only-request'
        return Command(
            bash_command=cmd
        )

class Parser(stage.Stage):
    def __init__(self):
        super().__init__()
        self.prepocessed = None
        self.parser = None

    def get_requirements(self) -> [Requirement]:
        #python3, pp.py, $PROGRAM
        self.preprocessed = Requirement(
            requirement=f'${cfg.get("BUILD_DIR")}/prepocessed.fa'
        )
        self.parser = Requirement(
            requirement=f'${cfg.get("LUNA_HOME/bin/parser")}'
        )
        return [self.preprocessed, self.parser]

    def get_command(self) -> Command:
        cmd = f'${self.parser} ${self.preprocessed} -O ${cfg.get("BUILD_DIR")}/program.ja -h ${cfg.get("headers.ja")}'
        return Command(
            bash_command=cmd
        )

class Preprocessor(stage.Stage):
    def __init__(self):
        super().__init__()
        self.program = None
        self.interpreter = None
        self.preprocessor = None

    def get_requirements(self) -> [Requirement]:
        #python3, pp.py, $PROGRAM
        self.interpreter = Requirement(
            requirement=cfg.get("PYTHON")
        )
        self.preprocessor = Requirement(
            requirement=f'${cfg.get("LUNA_HOME")}/scripts/pp.py'
        )
        self.program = Requirement(
            requirement=f'${cfg.get("PROGRAM")}'
        )
        return [self.interpreter, self.preprocessor, self.program]

    def get_command(self) -> Command:
        cmd = f'${self.interpreter} ${self.preprocessor} -D ${self.program} --text-info=${cfg.get("BUILD_DIR")}/preprocessed.fa --blocks-path=${cfg.get("BUILD_DIR")}/blocks.ti'
        return Command(
            bash_command=cmd
        )


class RunRTS(stage.Stage):
    def __init__(self):
        super().__init__()
        self.interpreter = None
        self.mkgen = None
        self.cxx = None
        self.cxx_flags = None
        self.ldflags = None

    def get_requirements(self) -> [Requirement]:
        #python3, pp.py, $PROGRAM
        self.interpreter =  self.interpreter = Requirement(
            requirement=f'${cfg.get("PYTHON")}'
        )
        self.mkgen = Requirement(
            requirement=f'${cfg.get("LUNA_HOME")}/scripts/mkgen'
        )
        self.cxx = Requirement(
            requirement=f'${cfg.get("CXX")}'
        )
        self.cxx_flags = Requirement(
            requirement=f'${cfg.get("CXX_FLAGS")}'
        )
        return [self.interpreter, self.mkgen, self.cxx]

    def get_command(self) -> Command:
        cmd = f'${self.interpreter} ${self.mkgen} --out=${cfg.get("BUILD_DIR")}/libucodes.so --compile-flags=${self.cxx_flags} --compiler=${self.cxx} --obj=${cfg.get("BUILD_DIR")} --src-stdin --link-flags=${self.ldflags} -shared -fPIC'
        return Command(
            bash_command=cmd
        )

class Substitution(stage.Stage):
    def __init__(self):
        super().__init__()
        self.interpreter = None
        self.substitution = None
        self.program = None

    def get_requirements(self) -> [Requirement]:
        #python3, pp.py, $PROGRAM
        self.interpreter = Requirement(
            requirement=cfg.get("PYTHON")
        )
        self.substitution = Requirement(
            requirement=f'${cfg.get("LUNA_HOME")}/scripts/substitution_let.py'
        )
        self.program = Requirement(
            requirement=f'${cfg.get("BUILD_DIR")}/program.ja'
        )
        return [self.interpreter, self.substitution, self.program]

    def get_command(self) -> Command:
        cmd = f'${self.interpreter} ${self.substitution} ${self.program}'
        return Command(
            bash_command=cmd
        )



