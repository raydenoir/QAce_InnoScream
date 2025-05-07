import random
import pytest

from innoscream.services.meme import \
            _SINGLE_TEXT_MEME_TEMPLATES, \
            _TWO_TEXT_MEME_TEMPLATES, _choose_template


@pytest.mark.asyncio
async def test_choose_template_with_id_valid():
    text = "A B C D"

    id = random.choice(_SINGLE_TEXT_MEME_TEMPLATES)
    ch_id, params = await _choose_template(id, text)

    assert ch_id in _SINGLE_TEXT_MEME_TEMPLATES

    assert (
        params["text1"] == text and params["text0"] == ""
        or params["text0"] == text and params["text1"] == ""
    )

    id = random.choice(_TWO_TEXT_MEME_TEMPLATES)
    ch_id, params = await _choose_template(id, text)

    assert ch_id in _TWO_TEXT_MEME_TEMPLATES
    assert params["text0"] == "A B" and params["text1"] == "C D"
