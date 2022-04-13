from models.api import CPT_code, Insurance, Provider


def check_cpt_code_insurance_age_combination(
    code: CPT_code, coverage: Insurance, age: int = 55
) -> bool:
    """Check cpt_code, insurance, and age to verify that a vaccination is covered

    Args:
        code (CPT_code): CPT code to check
        coverage (Insurance): insurance selected from the main_dialog workflow
        age (int, optional): Does the CPT code have age restrictions. Defaults to None.
    """
    covered = True

    def check_financial_class(code: CPT_code, coverage: Insurance) -> bool:
        # coverage.financial_class is a list
        if code.financial_class_exceptions:
            if [
                exc
                for exc in code.financial_class_exceptions
                if exc in coverage.financial_class
            ]:
                return True

    def check_insurance_exception(code: CPT_code, coverage: Insurance) -> bool:
        if code.coverage_exceptions:
            if [exc for exc in code.coverage_exceptions if exc == coverage.id]:
                return True

    def check_age(code: CPT_code, age: int) -> bool:
        if age > code.age_maximum or age < code.age_minimum:
            return True

    if any(
        [
            check_financial_class(code, coverage),
            check_insurance_exception(code, coverage),
            check_age(code, age),
        ]
    ):
        covered = False

    return covered


def requires_age_prompt(code: CPT_code, coverage: Insurance) -> bool:
    """Determine if the age of patient prompt is required.

    Args:
        code (CPT_code)
        coverage (Insurance)

    Returns:
        bool: True if prompt else False
    """
    requires_prompt = False
    # defaults for CPT code creation
    if code.age_minimum != 0 or code.age_maximum != 1000:
        requires_prompt = True
    return requires_prompt


def requires_referral(coverage: Insurance) -> bool:
    return True if coverage.referral_required == "No" else False

