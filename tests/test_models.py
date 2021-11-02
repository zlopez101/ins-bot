from data_models.models import CptCode


def test_CptCode():
    # test attributes and methods
    codes = CptCode.get_vaccines()
    assert len(codes) > 0
    code = CptCode.from_user_request("90636")
    assert code.name == "hepatitis a and hepatitis b vaccine"


def test_InsuranceExceptions():
    # test attributes and methods
    pass
