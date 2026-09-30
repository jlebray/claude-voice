from claude_voice.text import detect_language, split_sentences, to_speech


def test_keeps_the_words_and_drops_markup():
    markdown = "## Done\n\nFixed **the bug** in `packs/foo/app/services/bar_service.rb:42`, see [the PR](https://x.y)."

    assert to_speech(markdown) == "Done.\nFixed the bug in bar_service.rb, see the PR."


def test_skips_code_blocks():
    assert to_speech("Run this:\n```sh\nrm -rf /tmp/cache\n```\nThen retry.") == "Run this:\nThen retry."


def test_ends_list_items_with_a_pause():
    assert to_speech("- first point\n- second point") == "first point.\nsecond point."


def test_reads_table_rows_as_lists_and_skips_rulers():
    assert to_speech("| a | b |\n|---|---|\n| 1 | 2 |") == "a, b.\n1, 2."


def test_keeps_snake_case_identifiers():
    assert to_speech("Call my_method now.") == "Call my_method now."


def test_splits_on_sentences_and_lines():
    assert split_sentences("One. Two? Three\nFour: five") == ["One.", "Two?", "Three", "Four:", "five"]


def test_detects_french_from_accents():
    assert detect_language("C'est terminé") == "fr"


def test_detects_french_from_common_words():
    assert detect_language("le fichier est dans la branche") == "fr"


def test_defaults_to_english():
    assert detect_language("The file is fixed") == "en"
    assert detect_language("") == "en"
