import os.path

from .base import Model, Collection, DATA_DIRECTORY

COMMUNITY_AREA_CSV_FILENAME = os.path.join(DATA_DIRECTORY, 'CommAreas.csv')

class CommunityArea(Model):
    fields = [
        'name',
        'number',
    ]

    def __str__(self):
        return self.name

    def __repr__(self):
        return "CommunityArea(name='{ca.name}', number='{ca.number}')".format(
            ca=self)


class CommunityAreaCollection(Collection):
    model = CommunityArea

    def __init__(self):
        self._by_number = {}
        super(CommunityAreaCollection, self).__init__()

    def add_item(self, item):
        super(CommunityAreaCollection, self).add_item(item)
        self._by_number[item.number] = item

    def transform_row(self, row):
        return {
            'name': row['COMMUNITY'].title(),
            'number': row['AREA_NUMBE'],
        }

    def get_by_number(self, number):
        number_s = str(number)
        return self._by_number[number_s]

    def default_sort(self):
        self._items = sorted(self._items, key=lambda ca: int(ca.number))
        return self


COMMUNITY_AREAS = CommunityAreaCollection().from_csv(COMMUNITY_AREA_CSV_FILENAME)
