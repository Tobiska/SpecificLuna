from module import executor


def test_only_root_stage(only_root_tree, stub_environment):
    executor.Executor().Run(only_root_tree)
    assert True


def test_only_one_stage(one_stage_tree, stub_environment):
    requirement = "req"
    result = "res"
    stage = one_stage_tree
    stub_environment.add_list(requirement)
    executor.Executor().Run(stage)
    assert stub_environment.check(result).is_success()


def test_sequence(normal_sequence, stub_environment):
    stage = normal_sequence
    executor.Executor().Run(stage)
    assert stub_environment.success_executions == 5


def test_independent_fork_tree(independent_fork_tree, stub_environment):
    stage = independent_fork_tree
    executor.Executor().Run(stage)
    assert stub_environment.success_executions == 5
    assert stub_environment.check_failed_executions == 1


def test_fully_tree(fully_tree, stub_environment):
    stage = fully_tree
    executor.Executor().Run(stage)
    assert stub_environment.success_executions == 3
    assert stub_environment.check_failed_executions == 2
    assert stub_environment.check("testres5")


