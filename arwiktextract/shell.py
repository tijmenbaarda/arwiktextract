import cmd2
import json

from arwiktextract.data import Data, Entry


def as_cell(input_str: str, width: int):
    size = cmd2.ansi.style_aware_wcswidth(input_str)
    if size <= width:
        return input_str + " " * (width - size)
    else:
        return input_str[:(width - 1)] + "…"


class Shell(cmd2.Cmd):
    intro = "Welcome to ArWiktextract! Type ‘help’ for a list of commands."
    prompt = "[arwiktextract] # "
    data: Data

    def show_entry(self, entry: Entry, inputform: str) -> None:
        pos = as_cell(entry.pos, 5)
        glosses = as_cell(entry.glosses_summarized, 80)
        cf = as_cell(entry.canonical_form or "-", 15)
        for i, form in enumerate(entry.find_matching_forms(inputform)):
            form_str = as_cell(form.form, 15)
            tags_str = as_cell(form.tags_summary, 50)
            if i == 0: 
                self.poutput(
                    f"{cf } {pos} {glosses} {form_str} {tags_str}"
                )
            else:
                self.poutput(
                    " " * 103 + form_str + " " + tags_str
                )


    def __init__(self):
        super().__init__()
        self.data = Data()
        self.data.prepare_data()

    def do_word(self, args, show_raw=False):
        word = args
        entries = self.data.get_by_form(word)
        for entry in entries:
            if not show_raw:
                self.show_entry(entry, word)
            else:
                self.poutput(json.dumps(entry.data, ensure_ascii=False, indent=4))

    def do_wordraw(self, args):
        self.do_word(args, show_raw=True)

    def do_refresh(self, args):
        self.data.prepare_data(refresh=True)
