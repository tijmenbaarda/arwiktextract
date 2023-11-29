from dataclasses import dataclass


@dataclass
class Form:
    data: dict

    @property
    def form(self) -> str:
        return self.data["form"]

    @property
    def tags(self) -> list[str]:
        return self.data["tags"]

    def __str__(self) -> str:
        return self.form


@dataclass
class Entry:
    data: dict

    @property
    def forms(self) -> list[Form]:
        return [Form(x) for x in self.data["forms"]]

    def find_normalized_forms(self, normalized_form: str) -> list[Form]:
        forms: list[Form] = []
        for form in self.forms:
            if normalized_form == form.form:
                forms.append(form)
        return forms

    @property
    def glosses_summarized(self) -> str:
        senses = self.data["senses"]
        glosses = [x["glosses"][0] for x in senses]
        if len(glosses) == 1:
            return glosses[0]
        else:
            glosses_strs = []
            for index, gloss in enumerate(glosses):
                glosses_strs.append(f"({index + 1}) {gloss}")
            return ". ".join(glosses_strs)

    @property
    def pos(self) -> str:
        return self.data["pos"]

    @property
    def canonical_form(self) -> str:
        return "geen"
