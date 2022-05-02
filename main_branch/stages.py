import os

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
            requirement=f'{cfg.build_dir}/Makefile.libucodes'
        )
        return [self.makefile]

    def get_command(self) -> Command:
        cmd = f'{self.make} -j8 -f {self.makefile}'
        return Command(
            bash_command=cmd
        )

class GenerateBlocks(stage.Stage):
    def __init__(self):
        super().__init__()
        self.generator = Requirement(
            requirement=f'{cfg.luna_home}/scripts/generate_cpp_blocks.py'
        )
        self.interpreter = Requirement(
            requirement=f'{cfg.python}'
        )
        self.headers = Requirement(
            requirement=f'{cfg.build_dir}/headers.ja'
        )
        self.program = Requirement(
            requirement=f'{cfg.build_dir}/program.ja'
        )
        self.preprocessed_text_information = Requirement(
            requirement=f'{cfg.build_dir}/preprocessed.fa.ti'
        )
        self.block_text_information = Requirement(
            requirement=f'{cfg.build_dir}/blocks.ti'
        )
        self.program_foreign = Requirement(
            requirement=f'{cfg.build_dir}/program_foreign.ja'
        )
        self.foreign_blocks = Requirement(
            requirement=f'{cfg.build_dir}/foreign_blocks.cpp'
        )
        self.foreign_blocks_text_information = Requirement(
            requirement=f'{cfg.build_dir}/foreign_blocks.cpp.ti'
        )

    def get_requirements(self) -> [Requirement]:
        #python3, pp.py, $PROGRAM
        return [self.generator, self.program, self.preprocessed_text_information, self.block_text_information]

    def get_command(self) -> Command:
        cmd = f'{self.interpreter} {self.generator} {self.program} {self.headers} {self.preprocessed_text_information} {self.block_text_information} {self.program_foreign} {self.foreign_blocks} {self.foreign_blocks_text_information}'
        return Command(
            bash_command=cmd
        )

class GenerateMakefile(stage.Stage):
    def __init__(self):
        super().__init__()
        self.interpreter = self.interpreter = Requirement(
            requirement=f'{cfg.python}'
        )
        self.mkgen = Requirement(
            requirement=f'{cfg.luna_home}/scripts/mkgen'
        )
        self.cxx = Requirement(
            requirement=f'{cfg.cxx}'
        )
        self.cxx_flags = Requirement(
            requirement=f'{cfg.cxx_flags}'
        )

        self.program_dir = os.path.dirname(os.path.abspath(cfg.program))

    def get_requirements(self) -> [Requirement]:
        #python3, pp.py, $PROGRAM
        return [self.mkgen]

    def get_command(self) -> Command:
        cmd = [f'{self.interpreter}',
               f'{self.mkgen}',
               f'--out={cfg.build_dir}/libucodes.so',
               f'--compile-flags={self.cxx_flags}',
               f'--compiler={self.cxx}',
               f'--obj={cfg.build_dir}',
               '--src-stdin',
               f'--link-flags= {cfg.ldflags} -lrts -shared -fPIC']
        cpp_list = [os.path.join(cfg.build_dir, f) for f in os.listdir(cfg.build_dir) if f.endswith('.cpp')]
        cpp_list += [os.path.join(self.program_dir, f) for f in os.listdir(self.program_dir) if f.endswith('.cpp')]
        return Command(
            bash_command=cmd,
            input=('\n'.join(cpp_list)),
            output_type=Command.FILE,
            output_file = f'{cfg.build_dir}/Makefile.libucodes'
        )

class GenerateCppBlocks(stage.Stage):
    def __init__(self):
        super().__init__()
        self.fcmp2 = Requirement(
            requirement=f'{cfg.luna_home}/scripts/fcmp2'
        )
        self.interpreter = Requirement(
            requirement=f'{cfg.python}'
        )
        self.cpp_block_info = Requirement(
            requirement=f'{cfg.build_dir}/cpp_blocks_info.json'
        )
        self.cpp = Requirement(
            requirement=f'{cfg.build_dir}/test.cpp'
        )
        self.recommendations = Requirement(
            requirement=f'{cfg.build_dir}/program_recom.ja'
        )

    def get_requirements(self) -> [Requirement]:
        #python3, pp.py, $PROGRAM
        return [self.fcmp2, self.recommendations]

    def get_command(self) -> Command:
        cmd = f'{self.interpreter} {self.fcmp2} {self.recommendations} {self.cpp} {self.cpp_block_info}'
        return Command(
            bash_command=cmd
        )

class GenerateRecoms(stage.Stage):
    def __init__(self):
        super().__init__()
        self.fcmp = Requirement(
            requirement=f'{cfg.luna_home}/scripts/fcmp'
        )
        self.interpreter = Requirement(
            requirement=f'{cfg.python}'
        )
        self.foreign = Requirement(
            requirement=f'{cfg.build_dir}/program_foreign.ja'
        )
        self.recom = Requirement(
            requirement=f'{cfg.build_dir}/program_recom.ja'
        )

    def get_requirements(self) -> [Requirement]:
        #python3, pp.py, $PROGRAM
        return [self.fcmp, self.foreign]

    def get_command(self) -> Command:
        cmd = f'{self.interpreter} {self.fcmp} {self.foreign} {self.recom} --only-requests'
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
            requirement=f'{cfg.build_dir}/preprocessed.fa'
        )
        self.parser = Requirement(
            requirement=f'{cfg.luna_home}/bin/parser'
        )
        return [self.preprocessed, self.parser]

    def get_command(self) -> Command:
        cmd = f'{self.parser} {self.preprocessed} -o {cfg.build_dir}/program.ja -h {cfg.build_dir}/headers.ja'
        return Command(
            bash_command=cmd
        )

class Preprocessor(stage.Stage):
    def __init__(self):
        super().__init__()
        self.preprocessor = Requirement(
            requirement=f'{cfg.luna_home}/scripts/pp.py'
        )
        self.program = Requirement(
            requirement=f'{cfg.program}'
        )

        self.interpreter = Requirement(
            requirement=f'{cfg.python}'
        )

    def get_requirements(self) -> [Requirement]:
        #python3, pp.py, $PROGR
        return [self.preprocessor, self.program]

    def get_command(self) -> Command:
        cmd = f'{self.interpreter} {self.preprocessor} {self.program} -o {cfg.build_dir}/preprocessed.fa --text-info={cfg.build_dir}/preprocessed.fa.ti --blocks-path={cfg.build_dir}/blocks.ti'
        return Command(
            bash_command=cmd
        )


class RunRTS(stage.Stage):
    def __init__(self):
        super().__init__()
        self.interpreter = self.interpreter = Requirement(
            requirement=f'{cfg.python}'
        )
        self.mkgen = Requirement(
            requirement=f'{cfg.luna_home}/scripts/mkgen'
        )
        self.rts = Requirement(
            requirement=f'{cfg.luna_home}/bin/rts'
        )
        self.rts_debug = Requirement(
            requirement=f'{cfg.luna_home}/bin/rts.dbg'
        )
        self.lib_ucodes = Requirement(
            requirement=f'{cfg.build_dir}/libucodes.so'
        )
        self.ld_lib = f'{cfg.ld_library_path}:{cfg.luna_home}/lib'

    def get_requirements(self) -> [Requirement]:
        #python3, pp.py, $PROGRAM
        return [self.rts, self.rts_debug, self.lib_ucodes]

    def get_command(self) -> Command:
        env = dict(os.environ)
        env['LD_LIBRARY_PATH'] = self.ld_lib
        rts = self.rts if not cfg.debug else self.rts_debug
        cmd = f'{rts} {self.lib_ucodes} {" ".join(cfg.argv)}'
        return Command(
            output_type=Command.STDOUT,
            bash_command=cmd,
            environment=env
        )

class Substitution(stage.Stage):
    def __init__(self):
        super().__init__()
        self.interpreter = Requirement(
            requirement=cfg.python
        )
        self.substitution = Requirement(
            requirement=f'{cfg.luna_home}/scripts/substitution_let.py'
        )
        self.program = Requirement(
            requirement=f'{cfg.build_dir}/program.ja'
        )

    def get_requirements(self) -> [Requirement]:
        #python3, pp.py, $PROGRAM
        return [self.substitution, self.program]

    def get_command(self) -> Command:
        cmd = f'{self.interpreter} {self.substitution} {self.program}'
        return Command(
            bash_command=cmd
        )



