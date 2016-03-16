import os.path
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

from base import Model, Collection, DATA_DIRECTORY

COUNTY_CSV_FILENAME = os.path.join(DATA_DIRECTORY, 'county_fips.csv')

class County(Model):
    fields = [
        'state',
        'statefp',
        'countyfp',
        'countyname'
    ]

    def __str__(self):
        return self.countyname

    def __repr__(self):
        return "County(state='{c.state}', statefp='{c.statefp}', countyfp='{c.countyfp}', countyname='{c.countyname}')".format(
            c=self)


class CountyCollection(Collection):
    model = County

    def __init__(self):
        self._by_fips = {}
        self._by_name = {}
        super(CountyCollection, self).__init__()

    def add_item(self, item):
        super(CountyCollection, self).add_item(item)
        self._by_fips[item.countyfp] = item
        self._by_name[item.countyname.lower()] = item

    def transform_row(self, row):
        return {
            'state': row['State'],
            'statefp': str(row['StateFP']),
            'countyfp': str(row['CountyFP']),
            'countyname': row['County'].replace(' County', '')
        }

    def get_by_name(self, name):
        return self._by_name.get(str(name).lower(), None)

    def get_by_fips(self, fips):
        return self._by_fips.get(str(fips), None)

    def default_sort(self):
        self._items = sorted(self._items, key=lambda c: c.countyname)
        return self


COUNTIES = CountyCollection().from_csv(COUNTY_CSV_FILENAME)
