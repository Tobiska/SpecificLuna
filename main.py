# This is a sample Python script.
import config
import enviroment
from branch import Branch,TreeBuilder
from main_branch import stages as main_branch

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settin
cfg = config.LunaConfig()

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
        enviroment=enviroment.LocalEnvironment('local')
    )

    builder = TreeBuilder(main)
    root = builder.build()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    root = get_root()
    print(root)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
