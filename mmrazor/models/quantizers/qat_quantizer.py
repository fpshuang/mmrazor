from mmrazor.registry import MODELS
from .base import CustomQuantizer

from mmrazor.structures.quantization import (CheckArgs, DefalutQconfigs,
                                             QuantizeScheme, SupportQtypes)


@MODELS.register_module()
class QATQuantizer(CustomQuantizer):
    def __init__(self, 
                qconfig=DefalutQconfigs['default'],
                 is_qat=True, skipped_methods=None, prepare_custom_config_dict=None, convert_custom_config_dict=None, equalization_qconfig_dict=None, _remove_qconfig=True, init_cfg=None):
        super().__init__(qconfig, is_qat, skipped_methods, prepare_custom_config_dict, convert_custom_config_dict, equalization_qconfig_dict, _remove_qconfig, init_cfg)