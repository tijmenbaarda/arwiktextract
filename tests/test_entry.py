import pytest
import json
from pathlib import Path

from arwiktextract.entry import Entry, Form


@pytest.fixture
def sampleentry() -> Entry:
    entry = Entry(json.load((Path(__file__).parent / "data" / "entry.json").open()))
    return entry


class TestEntry:
    def test_find_normalized_forms(self, sampleentry: Entry):
        entry = sampleentry
        forms = entry.find_normalized_forms("القصص")
        assert len(forms) == 4

    def test_forms(self, sampleentry: Entry):
        entry = sampleentry
        forms = entry.forms
        assert all([isinstance(x, Form) for x in forms])
        assert len(forms) == 16
