import os.path

from .base import Model, Collection, DATA_DIRECTORY

PRECINCT_CSV_FILENAME = os.path.join(DATA_DIRECTORY, 'chicago_precinct_census_tract_crosswalk.csv')

class Precinct(Model):
    fields = [
        'number',
        'ward',
        'full_name',
        'census_tract_geoid'
    ]

    def __str__(self):
        return self.full_name

    def __repr__(self):
        return "Precinct(ward='{p.ward}', number='{p.number}', full_name='{p.full_name}', census_tract_geoid='{p.census_tract_geoid}')".format(
            p=self)


class PrecinctCollection(Collection):
    model = Precinct

    def __init__(self):
        self._by_full_name = {}
        super(PrecinctCollection, self).__init__()

    def add_item(self, item):
        super(PrecinctCollection, self).add_item(item)
        self._by_full_name[item.full_name] = item

    def transform_row(self, row):
        return {
            'number': row['precinct_number'],
            'ward': row['precinct_ward'],
            'full_name': row['precinct_full_name'],
            'census_tract_geoid': row['tract_geoid']
        }

    def get_by_full_name(self, full_name):
        return self._by_full_name[str(full_name)]

    def default_sort(self):
        self._items = sorted(self._items, key=lambda p: int(p.full_name))
        return self


PRECINCTS = PrecinctCollection().from_csv(PRECINCT_CSV_FILENAME)


def get_precincts_from_tract_geoid(geoid):
    matching_precincts = []
    for precinct in PRECINCTS:
        if precinct.census_tract_geoid == str(geoid):
            matching_precincts.append(precinct)
    return matching_precincts
