import unittest

from glhe.aggregation.dynamic import Dynamic
from glhe.aggregation.aggregation_factory import make_aggregation
from glhe.aggregation.no_agg import NoAgg
from glhe.aggregation.static import Static


class TestFactory(unittest.TestCase):

    def test_static(self):
        inputs = {'type': 'static'}
        agg_method = make_aggregation(inputs=inputs)
        self.assertIsInstance(agg_method, Static)

    def test_dynamic(self):
        inputs = {'type': 'dynamic'}
        agg_method = make_aggregation(inputs=inputs)
        self.assertIsInstance(agg_method, Dynamic)

    def test_no_aggregation(self):
        inputs = {'type': 'none'}
        agg_method = make_aggregation(inputs=inputs)
        self.assertIsInstance(agg_method, NoAgg)

    def test_error(self):
        inputs = {'type': 'bob'}
        self.assertRaises(ValueError, lambda: make_aggregation(inputs=inputs))
