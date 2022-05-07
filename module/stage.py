import queue
import uuid
from module.enviroment import *

"""
    Этап сборки программы - имеет при себе исполнительную комманду, входящие потребности,
    а так же очередь с приоритетом для агрегирования следующих этапов. Этап сборки сопровождается
    некоторой мета информацией о спецификации реализующего алгоритма.
"""


class Command:
    STDOUT = 1
    NONE = 0
    FILE = 2

    def __init__(self, bash_command, input=None, output_type=None, output_file=None, environment=None):
        self.bash_command = bash_command
        self.input = input
        self.output_type = output_type
        if (self.output_type != self.FILE) and (output_file is not None):
            raise Exception("output_type must be FILE, output_file be not NONE")

        self.output_file = output_file
        self.environment = environment


class Requirement:
    def __init__(self, requirement):
        self.str_requirement = requirement

    def __str__(self):
        return self.str_requirement


class Result:
    def __init__(self, result):
        self.str_result = result

    def __str__(self):
        return self.str_result


class Meta:
    def __init__(self, tag, parent, cleanup_results, environment):
        self.id = uuid.uuid4()
        self.tag = tag
        self.parent = parent
        self.cleanup_results = cleanup_results
        self.environment = environment


class Stage(ABC):
    def __init__(self, parent=None):
        self.id = uuid.uuid4()
        self.parent = parent
        self.next_stages = queue.PriorityQueue()
        self.meta = None

    @abstractmethod
    def get_requirements(self) -> [Requirement]:
        pass

    @abstractmethod
    def get_command(self) -> Command:
        pass

    @abstractmethod
    def get_results(self) -> [Result]:
        pass

    def get_environment(self) -> Environment:
        return self.meta.environment

    def get_all_stages(self):
        return self.next_stages.queue

    def set_meta(self, meta):
        self.meta = meta

    def add_command(self, stage, priority=None):
        if priority is None:
            priority = self.next_stages.qsize() + 1
        self.next_stages.put((-priority, stage))

    def next(self):
        if self.next_stages.qsize() == 0:
            return None
        job = self.next_stages.get()
        self.next_stages.task_done()
        return job[1]

    def reset(self):
        return self.parent

    def reset_branch(self):
        return self.meta.parent

class RootStageNotExecutableException(Exception):
    MessageException = "parent stage isn't executable"

    def __init__(self):
        super().__init__(self.MessageException)

def singleton(class_):
  instances = {}
  def getinstance(*args, **kwargs):
    if class_ not in instances:
        instances[class_] = class_(*args, **kwargs)
    return instances[class_]
  return getinstance

@singleton
class RootStage(Stage):

    def get_requirements(self) -> [Requirement]:
        raise RootStageNotExecutableException()

    def get_command(self) -> Command:
        raise RootStageNotExecutableException()

    def get_results(self) -> [Result]:
        raise RootStageNotExecutableException()
