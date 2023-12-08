SUBSTITUTIONS = {
    "أ": "ا",
    "إ": "ا",
    "آ": "ا",
    "ى": "ي",
    'ئ': 'ي',
    'ؤ': 'و',
}

REMOVALS = "ًٌٍَُِّْ"


def normalize(input_string: str) -> str:
    vowels_removed = input_string.translate({ord(i): None for i in REMOVALS})
    diacritics_removed = vowels_removed.translate(
        {ord(i): ord(SUBSTITUTIONS[i]) for i in SUBSTITUTIONS}
    )
    return diacritics_removed


def normalized_match(input_str: str, match_str: str) -> bool:
    # input_str may contain vowel signs, hamzas and maddas, and match_str
    # is the complete form. If an additional sign is present on
    # input_str, it should match with match_str. If no sign is present,
    # it can match with any or no sign on match_str.
    # Example: الكِتاب matches اَلْكِتَابُ, and الكُتّاب does not.
    pos1: int = 0
    pos2: int = 0
    while pos1 < len(input_str):
        if pos2 >= len(match_str):
            return False
        if input_str[pos1] == match_str[pos2]:
            pos1 += 1
            pos2 += 1
        elif match_str[pos2] in REMOVALS:
            pos2 += 1
        elif input_str[pos1] == SUBSTITUTIONS.get(match_str[pos2], None):
            pos1 += 1
            pos2 += 1
        else:
            return False
    return True

