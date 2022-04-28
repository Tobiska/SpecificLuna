from env_config import Config, parse_int, parse_bool, parse_str

class CustomConfig:
    cfg = Config()

    def __init__(self):
        self.cfg.declare("LUNA_HOME", parse_str()) #also set from std args
        self.cfg.declare("PYTHON", parse_str())
        self.cfg.declare("CXX_FLAGS", parse_str())
        self.cfg.declare("CXX", parse_str())
        self.cfg.declare("LDFLAGS", parse_str())
        self.cfg.declare("PROGRAM", parse_str())
        self.cfg.declare("LUNA_NO_CLEANUP", parse_bool())
        self.cfg.declare("DEBUG", parse_bool())

        self.cfg.declare("CLEANUP", parse_bool()) #also set from std args
        self.cfg.declare("TIME", parse_bool())
        self.cfg.declare("BALANCE", parse_str())

        self.cfg.declare("BUILD_DIR", parse_str()) #also set from std args

        self.cfg.apply_log_levels() #LOG_LEVEL, LOG_LEVEL, LOG_LEVEL_PARAMIKO.TRANSPORT

