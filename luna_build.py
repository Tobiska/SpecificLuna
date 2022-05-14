# This is a sample Python script.
import os

from module import enviroment, executor as ex
from module.branch import Branch,TreeBuilder
from main_branch import stages as main_branch
from iclu_branch import stages as iclu_branch
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settin

def get_root():
    main = Branch(
        tag='main',
        stages=[
           main_branch.Preprocessor(),
           main_branch.Parser(),
           main_branch.Substitution(),
           main_branch.GenerateBlocks(),
           main_branch.GenerateRecoms(),
           main_branch.GenerateCppBlocks(),
           main_branch.GenerateMakefile(),
           main_branch.BuildLibUcodes(),
           main_branch.RunRTS(),
        ],
        environment=enviroment.LocalEnvironment('local')
    )

    iclu = Branch(
        tag='luic',
        stages=[
            iclu_branch.Preprocessor(),
            iclu_branch.Parser(),
            iclu_branch.Compiler(),
            #Runner
        ],
        environment= enviroment.LocalEnvironment('local')
    )

    builder = TreeBuilder(main, iclu)
    return builder.build()


def execute(root):
    executor = ex.Executor()
    executor.Run(root)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    root = get_root()
    execute(root)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
