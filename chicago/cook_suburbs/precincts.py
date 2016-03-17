import os.path
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

from base import Model, Collection, DATA_DIRECTORY
from csv import DictReader

COOK_SUBURBAN_PRECINCT_CSV_FILENAME = os.path.join(
    DATA_DIRECTORY, 'cook_suburban_precincts_as_of_2016.csv')
COOK_SUBURBAN_PRECINCT_TRACT_CROSSWALK_CSV_FILENAME = os.path.join(
    DATA_DIRECTORY, 'suburban_cook_precinct_census_tract_crosswalk.csv')

class CookSuburbanPrecinct(Model):
    fields = [
        'town',
        'precinctid',
        'objectid'
    ]

    def __str__(self):
        return self.precinctid

    def __repr__(self):
        return "CookSuburbanPrecinct(town='{pc.town}', precinctid='{pc.precinctid}', objectid='{pc.objectid}'')".format(
            pc=self)


class CookSuburbanPrecinctCollection(Collection):
    model = CookSuburbanPrecinct

    def __init__(self):
        self._by_precinct_id = {}
        self._by_town_name = {}
        self._by_object_id = {}
        super(CookSuburbanPrecinctCollection, self).__init__()

    def add_item(self, item):
        super(CookSuburbanPrecinctCollection, self).add_item(item)
        self._by_precinct_id[item.precinctid] = item
        self._by_object_id[item.objectid] = item
        if item.town.lower() not in self._by_town_name:
            self._by_town_name[item.town.lower()] = []
        self._by_town_name[item.town.lower()].append(item)

    def transform_row(self, row):
        return {
            'town': row['name'],
            'precinctid': str(row['idpct']),
            'objectid': row['objectid']
        }

    def get_by_town_name(self, name):
        return self._by_town_name.get(str(name).lower(), None)

    def get_by_precinct_id(self, precinctid):
        return self._by_precinct_id.get(str(precinctid), None)

    def get_by_object_id(self, object_id):
        return self._by_object_id.get(str(object_id), None)

    def default_sort(self):
        self._items = sorted(self._items, key=lambda pc: int(pc.precinctid))
        return self


COOK_SUBURBAN_PRECINCTS = CookSuburbanPrecinctCollection().from_csv(
    COOK_SUBURBAN_PRECINCT_CSV_FILENAME)

# HACK - this seems duplicative with Chicago precinct crosswalk
COOK_SUBURBAN_CROSSWALK = []
with open(COOK_SUBURBAN_PRECINCT_TRACT_CROSSWALK_CSV_FILENAME) as fh:
    reader = DictReader(fh)
    for row in reader:
        COOK_SUBURBAN_CROSSWALK.append(row)

def get_suburban_cook_precincts_from_tract_geoid(geoid, precinct_key='precinct_objectid'):
    precinct_ids = []
    for row in COOK_SUBURBAN_CROSSWALK:
        if row['tract_geoid'] == str(geoid):
            precinct_ids.append(row.get(precinct_key, None))
    return precinct_ids

def get_suburban_cook_tract_from_precinct_number(precinct_id, precinct_key='precinct_objectid'):
    for row in COOK_SUBURBAN_CROSSWALK:
        if row.get(precinct_key, None) == str(precinct_id):
            return row['tract_geoid']
    return None