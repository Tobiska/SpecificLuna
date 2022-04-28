from stage import Stage, Meta


class Branch:
    def __init__(self, tag):
        self.parent_stage = None
        self.parent_branch = None
        self.stages = None
        self.tag = tag

    def set_stages(self, stages):
        self.stages = stages

    def set_parent(self, parent):
        self.parent = parent


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

    def collect_relationships(self) -> []:
        rels = dict()
        for branch in self.branches:
            rels[branch.parent_branch] = branch
            if branch.parent_stage not in branch.parent_branch.stages:
                raise ParentBranchException(
                    branch=branch.parent_branch,
                    stage=branch.parent_stage
                )
        return rels

    def add_stages(self, sequence_branch, parent):
        current_stage = parent
        for stage in sequence_branch:
            current_stage.add_command(stage=stage)
            current_stage=stage

    def find_circles(self, rels):
        pass

    def make_tree(self) -> Stage:
        global root
        for branch in self.branches:
            if branch.parent_branch == None:
                root = branch.stages[0]
            self.add_stages(branch.stages, branch.parent_stage)
        return root

    def find_initial_branch(self) -> Branch:
        global initial_branch
        found_branch_without_parent = 0
        for branch in self.branches:
            if branch.parent == None:
                found_branch_without_parent += 1
                initial_branch = branch
        if found_branch_without_parent > 1:
            raise TreeBuildException("Found branch without parent more than 1")
        if found_branch_without_parent < 1:
            raise TreeBuildException("Found branch without parent less than 1")
        return initial_branch

    def build(self) -> Stage:
        init_branch = self.find_initial_branch()
        relations = self.collect_relationships()
        self.find_circles(relations)
        root_stage = self.make_tree()
        if init_branch.stages[0] != root_stage:
            raise InitialBranchException(stage=root, branch=init_branch)

        return root_stage




