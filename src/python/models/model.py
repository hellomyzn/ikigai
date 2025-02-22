"""models.model"""
#########################################################
# Builtin packages
#########################################################
import json
from abc import ABC, abstractmethod
from typing import TypeVar

#########################################################
# 3rd party packages
#########################################################
# (None)

#########################################################
# Own packages
#########################################################
# (None)

TModel = TypeVar("TModel", bound="Model")


class Model(ABC):
    """ Model abstract class
    """

    @classmethod
    @abstractmethod
    def from_dict(cls: TModel, dict_: dict) -> TModel:
        """convert from dict to model

        Args:
            cls (TModel): model
            dict_ (dict): dict data

        Returns:
            TModel: model
        """

    @abstractmethod
    def to_dict(self, without_none_field: bool = False) -> dict:
        """convert from model to dict

        Args:
            without_none_field (bool, optional): option to remove none fields. Defaults to False.

        Returns:
            dict: dict data
        """

    @abstractmethod
    def to_json(self) -> json:
        """convert from model to json

        Returns:
            json: json data
        """
