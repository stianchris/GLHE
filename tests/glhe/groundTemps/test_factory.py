import unittest

from glhe.groundTemps.constant import Constant
from glhe.groundTemps.factory import get_ground_temp_model
from glhe.groundTemps.single_harmonic import SingleHarmonic
from glhe.groundTemps.two_harmonic import TwoHarmonic


class TestGTMFactory(unittest.TestCase):
    def test_ground_temperature_model_factory(self):
        inputs = {"type": "constant",
                  "constant": {
                      "temperature": 20}
                  }

        model = get_ground_temp_model(inputs=inputs)
        self.assertIsInstance(model, Constant)

        inputs = {"type": "single-harmonic",
                  "soil-diffusivity": 1e-6,
                  "single-harmonic": {
                      "ave-temperature": 20,
                      "amplitude": 0,
                      "phase-shift": 0}
                  }

        model = get_ground_temp_model(inputs=inputs)
        self.assertIsInstance(model, SingleHarmonic)

        inputs = {"type": "two-harmonic",
                  "soil-diffusivity": 1e-6,
                  "two-harmonic": {
                      "ave-temperature": 20,
                      "amplitude-1": 10,
                      "amplitude-2": 0,
                      "phase-shift-1": 0,
                      "phase-shift-2": 0}
                  }

        model = get_ground_temp_model(inputs=inputs)
        self.assertIsInstance(model, TwoHarmonic)

        inputs = {'type': 'bob'}
        self.assertRaises(ValueError, lambda: get_ground_temp_model(inputs=inputs))
