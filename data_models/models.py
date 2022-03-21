from dataclasses import dataclass
from typing import List, Union
import json
from errors.error import NotValidInput


def load_json(file: str) -> dict:
    """generic loading of json resources

    Args:
        file (str): filename to load, either codes or insurance

    Returns:
        list: the list of either codes or insurance
    """
    with open("data/" + file, "r") as fp:
        _file = json.load(fp)
        # strange stripping b/c all at once will remove the "s" in codes
        return _file[file.strip("json").strip(".")]


class Checker:
    def __init__(self):
        self.codes = load_json("codes.json")
        self.insurnaces = load_json("insurances.json")

    def verify_code(self, code: str) -> bool:
        """Return true if code is acceptable, otherwise false

        Args:
            code (int): user input code

        Returns:
            bool: Valid Code
        """
        if code.isnumeric():
            self.code = self.codes.get(code)
        else:
            # user supplied invalid literal, maybe supplied a string
            pass
        return True if hasattr(self, code) else False

    def verify_insurance(self, insurance_string: str) -> bool:
        """Return true if the insurance is accepted, otherwise false

        Args:
            insurance_string (str): user inputted insurance

        Returns:
            bool: valid insurance
        """

        pass

    def supply_drop_down(self) -> dict:
        pass


@dataclass
class CptCode:
    name: str
    abrrevation: str
    cpt_code: int
    trade_names: List[str]

    @classmethod
    def from_db(cls, azure_response: dict):
        """From the database response, once we activate it

        *************TBD***************

        Args:
            azure_response (dict): [description]

        Returns:
            [type]: [description]
        """
        return cls(
            azure_response["id"],
            azure_response["Abbreviations"],
            azure_response["Trade"],
        )

    @classmethod
    def from_user_request(cls, user_input: str):
        """User is requesting verification on a cpt code. Return information to confirm correct code is selected

        Args:
            user_input (str): user inputted information

        Returns:
            CptCode: Dataclass holding attributes regarding the cpt code
        """
        codes = cls.get_vaccines()
        if user_input.isdigit():
            # user gave us a cpt code
            just_cpts = [code["CPT Code"] for code in codes]
            try:
                vaccine_chosen = codes.pop(just_cpts.index(int(user_input)))
                return cls(
                    vaccine_chosen["id"],
                    vaccine_chosen["Abbreviations"],
                    vaccine_chosen["CPT Code"],
                    vaccine_chosen["Trade Names"],
                )
            except ValueError as error:
                raise NotValidInput
        elif isinstance(user_input, str) and user_input.isalpha():
            # building iterable
            [
                (vaccine["id"], vaccine["Trade Names"], vaccine["Abbreviations"])
                for vaccine in codes
            ]
            # user gave us a valid str
            pass
        else:
            # user did not give valid input
            # raise some error for the bot to check
            pass

    @staticmethod
    def get_vaccines() -> list:
        with open(r"data\vaccines.json", "r") as f:
            return json.load(f)["codes"]


@dataclass
class InsuranceException:
    name: str
    exceptions: List[dict]

    @classmethod
    def from_db(cls, azure_response: dict):
        return cls(azure_response["id"], azure_response["exceptions"])


if __name__ == "__main__":
    check = Checker()

