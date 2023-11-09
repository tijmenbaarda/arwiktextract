import readline
from pathlib import Path

from arwiktextract.shell import Shell
from arwiktextract import datadir


try:
    from colorama import just_fix_windows_console

    just_fix_windows_console()
except ImportError:
    pass

historyfile = Path(datadir) / "history"


def save_history() -> None:
    if not historyfile.parent.exists():
        historyfile.parent.mkdir(parents=True)
    readline.write_history_file(historyfile)


def main() -> None:
    if historyfile.exists():
        readline.read_history_file(historyfile)
    Shell().cmdloop()
    save_history()


if __name__ == "__main__":
    main()
