import os
import tempfile
import unittest

from glhe.input_processor.input_processor import InputProcessor
from glhe.output_processor.output_processor import OutputProcessor
from glhe.profiles.constant_load import ConstantLoad
from glhe.profiles.external_load import ExternalLoad
from glhe.profiles.load_factory import make_load_profile
from glhe.profiles.pulse_load import PulseLoad
from glhe.profiles.sinusoid_load import SinusoidLoad
from glhe.profiles.synthetic_load import SyntheticLoad
from glhe.utilities.functions import write_json


class TestLoadFactory(unittest.TestCase):

    @staticmethod
    def add_instance(method):
        fpath = os.path.dirname(os.path.abspath(__file__))
        data_str = '../../../glhe/profiles/external_data/GSHP-GLHE_USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.csv'
        data_path = os.path.normpath(os.path.join(fpath, data_str))
        d = {'fluid': {'fluid-type': 'water'},
             'load-profile': [{'load-profile-type': method,
                               'value': 10,
                               'name': 'my name',
                               'path': data_path,
                               'start-time': 1,
                               'end-time': 10,
                               'amplitude': 100,
                               'offset': 100,
                               'period': 10,
                               'synthetic-method': 'symmetric'}]}

        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, 'temp.json')

        write_json(temp_file, d)

        ip = InputProcessor(temp_file)
        op = OutputProcessor(temp_dir, 'out.csv')

        return make_load_profile(d['load-profile'][0], ip, op)

    def test_factory_constant(self):
        tst = self.add_instance('constant')
        self.assertIsInstance(tst, ConstantLoad)

    def test_factory_single_impulse(self):
        tst = self.add_instance('single-impulse')
        self.assertIsInstance(tst, PulseLoad)

    def test_factory_external(self):
        tst = self.add_instance('external')
        self.assertIsInstance(tst, ExternalLoad)

    def test_factory_sinusoid(self):
        tst = self.add_instance('sinusoid')
        self.assertIsInstance(tst, SinusoidLoad)

    def test_factory_synthetic(self):
        tst = self.add_instance('synthetic')
        self.assertIsInstance(tst, SyntheticLoad)

    def test_fail(self):
        d = {'fluid': {'fluid-type': 'water'},
             'load-profile': [{'load-profile-type': 'constant',
                               'value': 10,
                               'name': 'my name'}]}

        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, 'temp.json')

        write_json(temp_file, d)

        ip = InputProcessor(temp_file)
        op = OutputProcessor(temp_dir, 'out.csv')

        make_load_profile(d['load-profile'][0], ip, op)

        with self.assertRaises(ValueError) as _:
            make_load_profile({'load-profile-type': 'not-a-method'}, ip, op)
