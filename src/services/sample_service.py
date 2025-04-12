"""services.sample_service"""
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
from common.decorator import exception_module


@dataclass
class SampleService(object):
    """sample service"""

    @exception_module
    def sample(self):
        pass
