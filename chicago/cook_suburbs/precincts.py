import os.path
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

from base import Model, Collection, DATA_DIRECTORY

COOK_SUBURBAN_PRECINCT_CSV_FILENAME = os.path.join(
    DATA_DIRECTORY, 'cook_suburban_precincts_as_of_2016.csv')

class CookSuburbanPrecinct(Model):
    fields = [
        'town',
        'precinctid'
    ]

    def __str__(self):
        return self.precinctid

    def __repr__(self):
        return "CookSuburbanPrecinct(town='{pc.town}', precinctid='{pc.precinctid}')".format(
            pc=self)


class CookSuburbanPrecinctCollection(Collection):
    model = CookSuburbanPrecinct

    def __init__(self):
        self._by_precinct_id = {}
        self._by_town_name = {}
        super(CookSuburbanPrecinctCollection, self).__init__()

    def add_item(self, item):
        super(CookSuburbanPrecinctCollection, self).add_item(item)
        self._by_precinct_id[item.precinctid] = item
        if item.town.lower() not in self._by_town_name:
            self._by_town_name[item.town.lower()] = []
        self._by_town_name[item.town.lower()].append(item)

    def transform_row(self, row):
        return {
            'town': row['name'],
            'precinctid': str(row['idpct'])
        }

    def get_by_town_name(self, name):
        return self._by_town_name.get(str(name).lower(), None)

    def get_by_precinct_id(self, precinctid):
        return self._by_precinct_id.get(str(precinctid), None)

    def default_sort(self):
        self._items = sorted(self._items, key=lambda pc: int(pc.precinctid))
        return self


COOK_SUBURBAN_PRECINCTS = CookSuburbanPrecinctCollection().from_csv(
    COOK_SUBURBAN_PRECINCT_CSV_FILENAME)