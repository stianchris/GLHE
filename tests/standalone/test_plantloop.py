import unittest
from standalone.plantloop import PlantLoop
import csv
import os


class TestBlah(unittest.TestCase):

    def setUp(self):
        self.this_file_directory = os.path.dirname(os.path.realpath(__file__))

    def test_a(self):
        json_file_path = os.path.join(self.this_file_directory, '..', '..', 'glhe', 'examples', 'single.json')
        p = PlantLoop(json_file_path)
        self.assertTrue(p.simulate())
