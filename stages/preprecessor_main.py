
import stage
from stage import Command, Requirement


class Preprocessor(stage.Stage):
    def get_requirement_input(self) -> [Requirement]:
        cmd = [combiner.cfg.get('PYTHON')]
        cmd += [os.path.join(combiner.cfg.get("LUNA_HOME"), 'scripts', 'pp.py')]
        cmd += [cfg.get("PROGRAM")]
        cmd += ['-o', os.path.join(combiner.cfg.get("BUILD_DIR"), 'preprocessed.fa')]
        cmd += ['--text-info=%s' % os.path.join(combiner.cfg.get("BUILD_DIR"),
                                                'preprocessed.fa.ti')]
        cmd += ['--blocks-path=%s' % os.path.join(combiner.cfg.get("BUILD_DIR"),
                                                  'blocks.ti')]

    def get_command_execution(self) -> Command:
        pass