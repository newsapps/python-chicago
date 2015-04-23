from unittest import TestCase

from chicago import NEIGHBORHOODS

class NeighborhoodTestCase(TestCase):
    def test_len(self):
        self.assertEqual(len(NEIGHBORHOODS), 98)

    def test_iter(self):
        neighborhood = next(n for n in NEIGHBORHOODS
                            if n.name == "Humboldt Park")
        self.assertEqual(neighborhood.name, "Humboldt Park")

    def test_default_sort(self):
        hood = NEIGHBORHOODS[0]
        self.assertEqual(hood.name, "Albany Park")
