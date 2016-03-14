import json
import requests
import shapely


def download_precincts(
        url='https://data.cityofchicago.org/api/geospatial/uvpq-qeeq?method=export&format=GeoJSON',
        precincts_as_of=2012):
    """
    Download precinct GeoJSON from url. Set precincts_as_of flag to indicate vintage of precinct
    data.
    """
    response = requests.get(url)
    assert response.status_code == 200

    data = response.json()

    with open('data/precincts_as_of_%s.geojson' % precincts_as_of, 'w+') as fh:
        fh.write(json.dumps(data))


def download_tracts(
        url='https://data.cityofchicago.org/api/geospatial/5jrd-6zik?method=export&format=GeoJSON',
        tracts_as_of='2010'):
    """
    Download census tract GeoJSON from url. Set tracts_as_of flag to indicate vintage of tract data.
    """
    response = requests.get(url)
    assert response.status_code == 200

    data = response.json()

    with open('data/census_tracts_as_of_%s.geojson' % tracts_as_of, 'w+') as fh:
        fh.write(json.dumps(data))


def generate_precinct_tract_crosswalk(
        precincts_path='data/precincts_as_of_2012.geojson',
        tracts_path='data/census_tracts_as_of_2010.geojson'):
    """
    Generate crosswalk of precincts<->census tracts.
    """
    with open(precincts_path) as fh:
        precincts = json.loads(fh.read())
    with open(tracts_path) as fh:
        tracts = json.loads(fh.read())
    print 'precincts', precincts['features'][0]['properties']
    print 'tracts', tracts['features'][0]['properties']
    print len(precincts['features']), 'precincts'
    print len(tracts['features']), 'tracts'
