import queue
import uuid
from abc import ABC, abstractmethod
from enviroment import *

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
        self.input=input
        self.output_type=output_type
        if (self.output_type != self.FILE) and (output_file is not None):
            raise Exception("output_type must be FILE, output_file be not NONE")

        self.output_file = output_file
        self.environment = environment


class Requirement:
    def __init__(self, requirement):
        self.str_requirement = requirement

    def __str__(self):
        return self.str_requirement

"""
    tag - уникальный идентификатор реализуемого частного решения ('pic-method')
    parent - родитель ветки, для отката. 
"""


class Meta:
    def __init__(self, tag, parent, environment):
        self.id = uuid.uuid4()
        self.tag = tag
        self.parent = parent
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

    def get_environment(self) -> Environment:
        return self.meta.environment

    def meta(self) -> str:
        pass

    def set_meta(self, meta):
        self.meta = meta

    def add_command(self, stage, priority=None):
        if priority is None:
            priority = self.next_stages.qsize() + 1
        self.next_stages.put((priority, stage))

    def next(self):
       job = self.next_stages.get()
       self.next_stages.task_done()
       return job[1]

    def reset(self):
        return self.parent

    def reset_branch(self):
        return self.meta.parent