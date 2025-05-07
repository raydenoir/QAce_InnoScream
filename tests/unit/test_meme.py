import random
import pytest

from innoscream.services.meme import \
            _SINGLE_TEXT_MEME_TEMPLATES, \
            _TWO_TEXT_MEME_TEMPLATES, _choose_template

from innoscream.services.meme import _prepare_for_single_box


@pytest.mark.parametrize(
    "template_id, target_key",
    [
        ("5496396", "text1"),
        ("101470",  "text1"),
        ("4087833", "text1"),
        ("1234567", "text0"),
    ],
)
def test_prepare_for_single_box(template_id, target_key):
    text = "HELLO WORLD"
    result = _prepare_for_single_box(text, template_id)

    assert result[target_key] == text
    other_key = "text0" if target_key == "text1" else "text1"
    assert result[other_key] == ""

    assert set(result.keys()) == {"text0", "text1"}


@pytest.mark.asyncio
async def test_choose_template_with_id_valid():
    text = "A B C D"

    id = random.choice(_SINGLE_TEXT_MEME_TEMPLATES)
    ch_id, params = await _choose_template(text, id)

    assert ch_id in _SINGLE_TEXT_MEME_TEMPLATES

    assert (
        params["text1"] == text and params["text0"] == ""
        or params["text0"] == text and params["text1"] == ""
    )

    id = random.choice(_TWO_TEXT_MEME_TEMPLATES)
    ch_id, params = await _choose_template(text, id)

    assert ch_id in _TWO_TEXT_MEME_TEMPLATES
    assert params["text0"] == "A B" and params["text1"] == "C D"
