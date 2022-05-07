from module.stage import Stage, Meta, RootStage, Result


class Branch:
    def __init__(self, tag, stages=None, parent_stage=RootStage(), parent_branch=None, environment=None):
        self.parent_stage = parent_stage
        self.parent_branch = parent_branch
        self.stages = stages
        self.tag = tag
        self.environment = environment

    def __getattr__(self, item):
        for stage in self.stages:
            if item == type(stage).__name__:
                return stage
        return None

    def set_stages(self, stages):
        self.stages = stages

    def set_parent(self, parent_stage, parent_branch):
        self.parent_stage = parent_stage
        self.parent_branch = parent_branch

    def get_results_stages(self) -> [Result]:
        acc = []
        for item in self.stages:
            acc += item.get_results()
        return acc



class TreeBuildException(Exception):
    """Exception raised for errors build tree"""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class ParentBranchException(TreeBuildException):
    """Exception raised for errors build tree"""
    def __init__(self, branch, stage, message="Relation problem"):
        self.message = message
        self.stage = stage
        self.branch = branch
        super().__init__(self.message)
    def __str__(self):
        return f'branch: {self.branch.tag} has no stage with name: {self.stage.name}'


class InitialBranchException(TreeBuildException):
    """Exception raised for errors build tree"""
    def __init__(self, branch, stage, message="Relation problem"):
        self.message = message
        self.stage = stage
        self.branch = branch
        super().__init__(self.message)

    def __str__(self):
        return f'initial branch: {self.branch.tag} has no stage with name: {self.stage.name}'


class TreeBuilder:
    def __init__(self, *branches):
        self.branches = branches

    def _collect_relationships(self) -> []:
        rels = dict()
        for branch in self.branches:
            rels[branch.parent_branch] = branch
        return rels

    def _add_stages(self, branch):
        current_stage = branch.parent_stage
        for stage in branch.stages:
            stage.set_meta(
                meta=Meta(
                    tag=branch.tag,
                    parent=branch.parent_stage,
                    cleanup_results=branch.get_results_stages(),
                    environment=branch.environment,
                )
            )
            if current_stage is not None:
                current_stage.add_command(stage=stage)
            current_stage=stage

    def _find_circles(self, rels):
        pass

    def _make_tree(self) -> Stage:
        for branch in self.branches:
            self._add_stages(branch)
        return RootStage()

    def _find_initial_branch(self) -> Branch:
        global initial_branch
        found_branch_without_parent = 0
        for branch in self.branches:
            if branch.parent_stage is RootStage():
                found_branch_without_parent += 1
                initial_branch = branch
        if found_branch_without_parent > 1:
            raise TreeBuildException("Found branch without parent more than 1")
        if found_branch_without_parent < 1:
            raise TreeBuildException("Found branch without parent less than 1")
        return initial_branch

    def build(self) -> Stage:
        relations = self._collect_relationships()
        self._find_circles(relations)
        root_stage = self._make_tree()
        return root_stage




