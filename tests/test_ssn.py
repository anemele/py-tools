from py_tools.ssn import cvt_15_to_18, validate_18


def test_validate_18():
    assert validate_18("110101199912311230") == "110101199912311230"
    assert validate_18("11010120001231129X") == "11010120001231129X"
    assert validate_18("11010120001231129x") == "11010120001231129X"


def test_cvt_15_to_18():
    assert cvt_15_to_18("110101991231123") == "110101199912311230"
