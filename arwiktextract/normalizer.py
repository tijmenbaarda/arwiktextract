SUBSTITUTIONS = {
    "أ": "ا",
    "إ": "ا",
    "آ": "ا",
    "ى": "ي",
    #  'ئ': 'ي',
    #    'ؤ': 'و',
}

REMOVALS = "ًٌٍَُِّْ"


def normalize(input_string):
    vowels_removed = input_string.translate({ord(i): None for i in REMOVALS})
    diacritics_removed = vowels_removed.translate(
        {ord(i): ord(SUBSTITUTIONS[i]) for i in SUBSTITUTIONS}
    )
    return diacritics_removed
