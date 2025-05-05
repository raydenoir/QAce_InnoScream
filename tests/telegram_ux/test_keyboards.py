from src.innoscream.telegram_ux.keyboards import get_reaction_keyboard, get_main_keyboard

def test_reaction_keyboard():
    """Test reaction keyboard generation"""
    keyboard = get_reaction_keyboard("test123")
    assert len(keyboard.inline_keyboard) == 1
    assert len(keyboard.inline_keyboard[0]) == 3
    assert keyboard.inline_keyboard[0][0].text == "👍"
    assert "test123" in keyboard.inline_keyboard[0][0].callback_data

def test_main_keyboard():
    """Test main keyboard generation"""
    keyboard = get_main_keyboard()
    assert len(keyboard.keyboard) == 3
    assert keyboard.keyboard[0][0].text == "/scream"