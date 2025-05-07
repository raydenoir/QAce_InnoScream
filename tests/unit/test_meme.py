import pytest
import random

from innoscream.services.meme import \
            _SINGLE_TEXT_MEME_TEMPLATES, _SINGLE_TEXT_BOTTOMTEXT_TEMPLATES, \
            _TWO_TEXT_MEME_TEMPLATES, _choose_template


def test_choose_template_with_id_valid():
    id = random.choice(_SINGLE_TEXT_MEME_TEMPLATES)
    text = "A B C D"
    ch_id, params = _choose_template(text, id)

    assert ch_id in _SINGLE_TEXT_MEME_TEMPLATES
    if id in _SINGLE_TEXT_BOTTOMTEXT_TEMPLATES:
        assert params["text1"] == text and params["text0"] == ""
    else:
        assert params["text0"] == text and params["text1"] == ""
    
    id = random.choice(_TWO_TEXT_MEME_TEMPLATES)
    ch_id, params = _choose_template(text, id)

    assert ch_id in _TWO_TEXT_MEME_TEMPLATES
    assert params["text0"] == "A B" and params["text1"] == "C D"