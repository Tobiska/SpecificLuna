import argparse
import os

import configargparse


class LunaConfig:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(LunaConfig, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.parser = configargparse.ArgParser()
        self.parser.add_argument("-lh", "--luna_home", required=True, help="Luna home path", env_var="LUNA_HOME") #also set from std args
        self.parser.add_argument('--python', required=True, env_var="PYTHON")
        self.parser.add_argument('--cxx_flags', required=True, env_var="CXX_FLAGS")
        self.parser.add_argument('--cxx', required=True, env_var="CXX")
        self.parser.add_argument('--debug', required=True, env_var="DEBUG", default=False)
        self.parser.add_argument('program')
        self.parser.add_argument('argv', nargs='*')
        self.parser.add_argument('--cleanup', type=bool, env_var="CLEANUP")
        self.parser.add_argument('--log_level', env_var="LOG_LEVEL", default="ERROR")
        self.parser.add_argument('--log_filename', env_var="LOG_FILENAME", default="build.log")
        self.parser.add_argument('--ld_library_path', env_var='LD_LIBRARY_PATH', default="")
        self.parser.add_argument('-g', env_var="DEBUG", default=False)
        self.parser.add_argument("--build-dir", env_var="BUILD_DIR", default=os.getcwd()) #also set from std args

        self.parser.add_argument("--iclu_home", required=True, help="home directory iclu-project", env_var="ICLU_HOME")
        self.cfg = self.parser.parse_args()

    def GetConfig(self):
        return self.cfg

cfg = LunaConfig().GetConfig()
