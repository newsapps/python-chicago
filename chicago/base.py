import csv
import os.path


DATA_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)),
    'data')


class Model(object):
    fields = []

    def __init__(self, **kwargs):
        for field in self.fields:
            try:
                val = kwargs[field]
                setattr(self, field, val)
            except KeyError:
                pass


class Collection(object):
    model = Model

    def __init__(self, items=None):
        self._items = []
        if items is None:
            items = []
        for item in items:
            self.add_item(item)

        self.default_sort()

    def __iter__(self):
        return iter(self._items);

    def __getitem__(self, i):
        return self._items[i]

    def __len__(self):
        return len(self._items)

    def __repr__(self):
        cls_name = self.__class__.__name__
        return "{}([{}])".format(
            cls_name,
            ','.join([repr(item) for item in self._items])
        )

    def default_sort(self):
        return self

    def get_model(self):
        return self.model

    def add_item(self, item):
        self._items.append(item)

    def _from_csv_file(self, csvfile):
        reader = csv.DictReader(csvfile)
        model_cls = self.get_model()
        for row in reader:
            model_kwargs = self.transform_row(row)
            self.add_item(model_cls(**model_kwargs))

        self.default_sort()

        return self

    def from_csv(self, csvfile):
        try:
            return self._from_csv_file(csvfile)
        except KeyError:
            # Couldn't parse CSV properly, so csvfile is probably a string
            with open(csvfile, 'r') as f:
                return self._from_csv_file(f)

    def transform_row(self, row):
        return row
