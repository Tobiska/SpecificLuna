import pytest
from module.branch import *
from test_branch.stages import *

from module.enviroment import *


class StubEnvironment(Environment):
    def __init__(self):
        self.list = [None]
        self.check_failed_executions = 0
        self.success_executions = 0
        super().__init__()

    def check(self, requirement) -> Status:
        if requirement in self.list:
            status = Status(return_code=0, message="Success")
        else:
            status = Status(return_code=1, message=f"Requirement {requirement} is absent")
            self.check_failed_executions += 1
        return status

    def add_list(self, requirement):
        self.list.append(requirement)

    def cleanup(self, results):
        for result in results:
            if result in self.list:
                del result

    def execute_command(self, cmd) -> Status:
        self.list.append(cmd.bash_command)
        self.success_executions += 1
        return super().collect_status(message=None,
                                      err=None,
                                      returncode=0,
                                      execution_time=0.0)

@pytest.fixture(scope="session")
def stub_environment():
    return StubEnvironment()

@pytest.fixture
def only_root_tree(stub_environment):
    return TreeBuilder().build()


def _one_stage_tree(req, res):
    test = Branch(
        tag="test",
        stages=[
            TestStage(requirement=req,
                      result=res)
        ],
        environment=StubEnvironment()
    )
    return TreeBuilder(test).build()

@pytest.fixture
def one_stage_tree(stub_environment):
    test = Branch(
        tag="test",
        stages=[
            TestStage(requirement="req",
                      result="res")
        ],
        environment=stub_environment
    )
    return TreeBuilder(test).build()


@pytest.fixture
def normal_sequence(stub_environment):
    test = Branch(
        tag="test",
        stages=[
            TestStage(result="testres1"),
            TestStage(requirement="testres1",
                      result="testres2"),
            TestStage(requirement="testres2",
                      result="testres3"),
            TestStage(requirement="testres3",
                      result="testres4"),
            TestStage(requirement="testres4",
                      result="testres5"),
        ],
        environment=stub_environment
    )
    return TreeBuilder(test).build()


@pytest.fixture
def independent_fork_tree(stub_environment):
    test = Branch(
        tag="test",
        stages=[
            TestStage(result="testres1"),
            TestStage(requirement="testres1",
                      result="testres2"),
            TestStage(requirement="testres2",
                      result="testres3"),
            TestStage(requirement="testres3",
                      result="testres4"),
            TestStage(requirement="testres4",
                      result="testres5"),
        ],
        environment=stub_environment
    )

    test2 = Branch(
        tag="test2",
        stages=[
            TestStage(requirement=["notcontainsobj"],
                      result=["testres1"])
        ],
        environment=stub_environment
    )
    return TreeBuilder(test, test2).build()


@pytest.fixture
def fully_tree(stub_environment):
    """
                    test
                 /        \
           test2           test3
                        /        \
                     test4       test5
    """
    test = Branch(
        tag="test",
        stages=[
            TestStage(
                      result="testres1"),
        ],
        environment=stub_environment
    )

    test2 = Branch(
        tag="test2",
        parent_stage=test.TestStage,
        stages=[
            TestStage(requirement=["notcontainsobj"],
                      result=["testres2"])
        ],
        environment=stub_environment
    )

    test3 = Branch(
        tag="test3",
        parent_stage=test.TestStage,
        stages=[
            TestStage(requirement="testres1",
                      result="testres3")
        ],
        environment=stub_environment
    )

    test4 = Branch(
        tag="test4",
        parent_stage=test3.TestStage,
        stages=[
            TestStage(requirement="notcontainsobj",
                      result="testres4")
        ],
        environment=stub_environment
    )

    test5 = Branch(
        tag="test5",
        parent_stage=test3.TestStage,
        stages=[
            TestStage(requirement="testres3",
                      result="testres5")
        ],
        environment=stub_environment
    )
    return TreeBuilder(test, test3, test2, test5, test4).build()


@pytest.fixture
def circle(stub_environment):
    test = Branch(
        tag="test",
        stages=[
            TestStage(
                result="testres1"),
        ],
        environment=stub_environment
    )

    test2 = Branch(
        tag="test2",
        parent_branch=test.TestStage,
        stages=[
            TestStage(requirement=["notcontainsobj"],
                      result=["testres2"])
        ],
        environment=stub_environment
    )

    test3 = Branch(
        tag="test3",
        parent_branch=test2.TestStage,
        stages=[
            TestStage(requirement="testres1",
                      result="testres3")
        ],
        environment=stub_environment
    )

    test.set_parent(parent_branch=test3.TestStage)



