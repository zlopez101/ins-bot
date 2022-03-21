from data_models.models import CptCode, Checker


def test_CptCode():
    # test attributes and methods
    codes = CptCode.get_vaccines()
    assert len(codes) > 0
    code = CptCode.from_user_request("90636")
    assert code.name == "hepatitis a and hepatitis b vaccine"


def test_InsuranceExceptions():
    # test attributes and methods
    pass


class TestChecker:
    def test_checker(self):
        checker = Checker()
        checker.verify_code("90750")
        assert hasattr(checker, "code")
        assert isinstance(checker.code, dict)
        assert checker.code["name"] == "zoster vaccine, recombinant"


def test_checker():

    check = Checker()
    check.verify_code("90750")
    assert hasattr(check, "code")
    assert isinstance(check.code, dict)
    assert check.code["name"] == "zoster vaccine, recombinant"
