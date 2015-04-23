import os.path

from .base import Model, Collection, DATA_DIRECTORY

NEIGHBORHOOD_CSV_FILENAME = os.path.join(DATA_DIRECTORY,
    'Neighborhoods_2012b.csv')

class Neighborhood(Model):
    fields = [
        'name',
    ]

    def __str__(self):
        return self.name

    def __repr__(self):
        return "Neighborhood(name='{ca.name}')".format(
            ca=self)


class NeighborhoodCollection(Collection):
    model = Neighborhood

    def transform_row(self, row):
        return {
            'name': row['PRI_NEIGH'],
        }

    def default_sort(self):
        self._items = sorted(self._items, key=lambda n: n.name)
        return self



NEIGHBORHOODS = NeighborhoodCollection().from_csv(NEIGHBORHOOD_CSV_FILENAME)
