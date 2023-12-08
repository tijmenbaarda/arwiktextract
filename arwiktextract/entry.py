from dataclasses import dataclass
from typing import Optional

from .normalizer import normalize, normalized_match

TAG_ABBREVIATIONS = {
    "singular": "sg",
    "dual": "dl",
    "plural": "pl",
}


@dataclass
class Form:
    data: dict

    @property
    def form(self) -> str:
        return self.data["form"]

    @property
    def normalized_form(self) -> str:
        return normalize(self.form)

    @property
    def tags(self) -> list[str]:
        return self.data["tags"]

    @property
    def tags_summary(self) -> str:
        tags = [TAG_ABBREVIATIONS.get(tag, tag) for tag in self.tags]
        return " ".join(tags)

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
            if normalized_form == form.normalized_form:
                forms.append(form)
        return forms

    def find_matching_forms(self, form: str) -> list[Form]:
        """Return a list of all forms of the entry that match the given form,
        which may contain (partial) vocalisation or other special signs."""
        normalized_form = normalize(form)
        possible_matches = self.find_normalized_forms(normalized_form)
        return [x for x in possible_matches if normalized_match(form, x.form)]

    def find_forms_with_tag(self, tag: str) -> list[Form]:
        return [x for x in self.forms if tag in x.tags]

    @property
    def glosses_summarized(self) -> str:
        senses = self.data["senses"]
        glosses = [x["glosses"][0] for x in senses if "glosses" in x]
        summary: Optional[str] = None
        if len(glosses) == 1:
            summary = glosses[0]
        else:
            glosses_strs = []
            for index, gloss in enumerate(glosses):
                glosses_strs.append(f"({index + 1}) {gloss}")
            summary = ". ".join(glosses_strs)
        return summary or "(no glosses)"

    @property
    def pos(self) -> str:
        return self.data["pos"]

    @property
    def canonical_form(self) -> Optional[str]:
        canonical_form_list = self.find_forms_with_tag("canonical")
        if len(canonical_form_list) != 0:
            return canonical_form_list[0].form
