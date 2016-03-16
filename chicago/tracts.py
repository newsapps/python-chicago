import os.path

from .base import Model, Collection, DATA_DIRECTORY

TRACT_CSV_FILENAME = os.path.join(DATA_DIRECTORY, 'chicago_precinct_census_tract_crosswalk.csv')

class Tract(Model):
    fields = [
        'commarea_num',
        'countyfp',
        'geoid',
        'name',
        'statefp',
        'precinct_full_name'
    ]

    def __str__(self):
        return self.geoid

    def __repr__(self):
        return "Tract(commarea_num='{t.commarea_num}',countyfp='{t.countyfp}',geoid='{t.geoid}',name='{t.name}',statefp='{t.statefp}',precinct_full_name='{t.precinct_full_name}')".format(
            t=self)


class TractCollection(Collection):
    model = Tract

    def __init__(self):
        self._by_geoid = {}
        super(TractCollection, self).__init__()

    def add_item(self, item):
        super(TractCollection, self).add_item(item)
        self._by_geoid[item.geoid] = item

    def transform_row(self, row):
        return {
            'commarea_num': row['tract_commarea_num'],
            'countyfp': row['tract_countyfp'],
            'geoid': row['tract_geoid'],
            'name': row['tract_name'],
            'statefp': row['tract_statefp'],
            'precinct_full_name': row['precinct_full_name']
        }

    def get_by_geoid(self, geoid):
        return self._by_geoid[str(geoid)]

    def default_sort(self):
        self._items = sorted(self._items, key=lambda p: int(p.geoid))
        return self


TRACTS = TractCollection().from_csv(TRACT_CSV_FILENAME)


def get_tract_from_ward_and_precinct(ward, precinct):
    precinct_id = '%s%s' % (str(ward).zfill(2), str(precinct).zfill(3))
    return get_tract_from_precinct_id(precinct_id)


def get_tract_from_precinct_id(precinct_id):
    for tract in TRACTS:
        if tract.precinct_full_name == str(precinct_id):
            return tract
    return None
