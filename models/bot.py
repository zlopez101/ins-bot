"""Holds the models for the microsoft teams bot"""
from dataclasses import dataclass
from typing import Callable, List

from .api import Insurance


@dataclass
class Conversation_State:

    patient: int = None
    patient_age: int = None
    coverage: Insurance = None
    provider: int = None
    location: str = None
    cpt_code: List[int] = None
    payer: str = None


@dataclass
class UserProfile:

    name: str = None
    role: str = None
    location: str = None
    choices_to_display: int = 5


class ChoiceLooper:
    """Class for holding the choices for the ChoicePrompt."""

    def __init__(
        self, items: list, sorting_key: Callable = None, items_to_show: int = 5
    ):
        self.items = sorted(items, key=sorting_key)
        self.start = 0
        self.end = items_to_show
        self.items_to_show = items_to_show

    def __bool__(self):
        return True

    def __iter__(self):
        return self

    def __next__(self):
        current_choices = self.items[self.start : self.end]
        if not current_choices:
            self.start = 0
            self.end = self.items_to_show
            current_choices = self.items[self.start : self.end]
        self.start += 5
        self.end += 5
        return current_choices
