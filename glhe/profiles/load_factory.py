from typing import Union

from glhe.input_processor.input_processor import InputProcessor
from glhe.output_processor.output_processor import OutputProcessor
from glhe.profiles.constant_load import ConstantLoad
from glhe.profiles.external_load import ExternalLoad
from glhe.profiles.pulse_load import PulseLoad
from glhe.profiles.sinusoid_load import SinusoidLoad
from glhe.profiles.synthetic_load import SyntheticLoad


def make_load_profile(inputs: dict, ip: InputProcessor, op: OutputProcessor) -> Union[ConstantLoad, PulseLoad,
                                                                                      ExternalLoad, SinusoidLoad,
                                                                                      SyntheticLoad]:
    load_profile_type = inputs['load-profile-type']
    if load_profile_type == 'constant':
        return ConstantLoad(inputs, ip, op)
    elif load_profile_type == 'single-impulse':
        return PulseLoad(inputs, ip, op)
    elif load_profile_type == 'external':
        return ExternalLoad(inputs, ip, op)
    elif load_profile_type == 'sinusoid':
        return SinusoidLoad(inputs, ip, op)
    elif load_profile_type == 'synthetic':
        return SyntheticLoad(inputs, ip, op)
    else:
        raise ValueError("Load profile '{}' is not valid.".format(load_profile_type))
