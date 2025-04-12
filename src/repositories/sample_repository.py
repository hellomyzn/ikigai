"""repositories.sample_repository"""
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
from repositories import ModelAdapter
from models import Sample


@dataclass
class SampleRepository(object):
    """sample repository"""
    sample_adapter: ModelAdapter = ModelAdapter(Sample, {
        "id": "id",
        "hoge": "hoge",
        "fuga": "fuga",
        "piyo": "piyo"
    })
