"""repository.model_adapter"""
#########################################################
# Builtin packages
#########################################################
from dataclasses import dataclass, field

#########################################################
# 3rd party packages
#########################################################
# (None)

#########################################################
# Own packages
#########################################################
from models import Model


@dataclass
class ModelAdapter(object):
    """adapter between model and repository"""
    model: Model = field(init=True, default=None)
    key_map: dict = field(init=True, default_factory=None)

    def from_model(self, model: Model) -> dict:
        """convert from model to db

        Args:
            model (Model): _description_

        Returns:
            dict: _description_
        """
        model_dict = model.to_dict(without_none_field=True)
        result = {}
        for repo_key, key in self.key_map.items():
            value = model_dict.get(key)
            if value is not None:
                result[repo_key] = value
        return result

    def to_model(self, data_from_db: dict) -> Model:
        result = {}
        for repo_key, key in self.key_map.items():
            result[key] = data_from_db[repo_key]
        return self.model.from_dict(result)
