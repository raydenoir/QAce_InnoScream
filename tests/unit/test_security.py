from innoscream.services.security import hash_user_id


def test_hash_user_id_is_consistent():
    user_id = 123
    hashed1 = hash_user_id(user_id)
    hashed2 = hash_user_id(user_id)
    assert hashed1 == hashed2
    assert isinstance(hashed1, str)
    assert len(hashed1) == 64
