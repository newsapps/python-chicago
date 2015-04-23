from unittest import TestCase

from chicago import COMMUNITY_AREAS

class CommunityAreaTestCase(TestCase):
    def test_len(self):
        self.assertEqual(len(COMMUNITY_AREAS), 77)

    def test_get_by_number(self):
        ca = COMMUNITY_AREAS.get_by_number(22)
        self.assertEqual(ca.name, "Logan Square")
        self.assertEqual(ca.number, "22")

        ca = COMMUNITY_AREAS.get_by_number('22')
        self.assertEqual(ca.name, "Logan Square")
        self.assertEqual(ca.number, "22")

    def test_iter(self):
        filtered = [ca for ca in COMMUNITY_AREAS
                    if ca.name == "Logan Square"]
        self.assertEqual(len(filtered), 1)
        ca = filtered[0]
        self.assertEqual(ca.name, "Logan Square")
        self.assertEqual(ca.number, "22")

    def test_default_sort(self):
        ca = COMMUNITY_AREAS[0]
        self.assertEqual(ca.number, '1')
        self.assertEqual(ca.name, "Rogers Park")
