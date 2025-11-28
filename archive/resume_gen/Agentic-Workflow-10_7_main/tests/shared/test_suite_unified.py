import os


def test_test_suite_unified():
    assert not os.path.exists("tests_flat"), "tests_flat should not exist"
    assert os.path.isdir("tests/v10_7")
    assert os.path.isdir("tests/v10_8")
