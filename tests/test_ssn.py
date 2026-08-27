from py_tools.ssn import validate_18


def test_validate_18():
    assert validate_18("110101199912311230") is None
    assert validate_18("11010120001231129X") is None
    assert validate_18("11010120001231129x") is None
