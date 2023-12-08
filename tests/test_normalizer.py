from arwiktextract.normalizer import normalized_match

MATCHES = [
    ("الكتاب", "الكتاب"),
    ("الكِتاب", "اَلْكِتَابُ"),
    ("الامر", "اَلأَمرُ"),
    ("الف", "أَلِف"),
]

NO_MATCHES = [
    ("الكُتّاب", "اَلْكِتَابُ"),
]


def test_normalized_match():
    for match in MATCHES:
        assert normalized_match(match[0], match[1])
    for match in NO_MATCHES:
        assert not normalized_match(match[0], match[1])
