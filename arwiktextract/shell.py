import cmd2


class Shell(cmd2.Cmd):
    intro = "Welcome to ArWiktextract! Type ‘help’ for a list of commands."
    prompt = "[arwiktextract] # "

    def __init__(self):
        super().__init__()
