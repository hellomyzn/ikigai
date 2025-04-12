"""repositories.base_repository_interface"""
#########################################################
# Builtin packages
#########################################################
import abc

#########################################################
# 3rd party packages
#########################################################
# (None)

#########################################################
# Own packages
#########################################################
# (None)


class BaseRepositoryInterface(metaclass=abc.ABCMeta):
    """base repository interface"""

    def __init__(self):
        pass

    @abc.abstractmethod
    def all(self) -> list:
        """get all data

        Raises:
            NotImplementedError: not implemented

        Returns:
            list: all data
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def find_by_id(self, id_: int) -> dict:
        """get a data

        Args:
            id_ (int): data id you want to get

        Raises:
            NotImplementedError: not implemented

        Returns:
            dict: a data
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def add(self, data: dict) -> None:
        """add a data into repo

        Args:
            data (dict): a data

        Raises:
            NotImplementedError: not implemented
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def delete_by_id(self, id_: int) -> None:
        """delete data by id

        Args:
            id_ (int): data id you want to delete

        Raises:
            NotImplementedError: note implemented
        """
        raise NotImplementedError()
