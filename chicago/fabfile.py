import json
import requests

from csv import DictWriter
from shapely.geometry import shape, Point


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

    # Create iterable of shapely geometries of tracts, since there are fewer & they're bigger
    tract_geos = []
    for tract in tracts['features']:
        tract_geos.append({
            'geoid10': tract['properties']['geoid10'],
            'shape': shape(tract['geometry'])
        })

    # Now, loop over precincts, take the centroid of each and find the tract that centroid is in
    crosswalk = []
    for precinct in precincts['features']:
        centroid = shape(precinct['geometry']).centroid
        cw = {
            'precinct_number': precinct['properties']['precinct'],
            'precinct_ward': precinct['properties']['ward'],
            'precinct_full_name': precinct['properties']['full_text'],
            'tract_geoid': None
        }
        for tract in tract_geos:
            if tract['shape'].contains(centroid):
                cw['tract_geoid'] = tract['geoid10']
                break
        if not cw['tract_geoid']:
            print 'No tract matches precinct %s' % cw['precinct_full_name']
        crosswalk.append(cw)

    with open('data/precinct_census_tract_crosswalk.csv', 'w+') as fh:
        writer = DictWriter(fh, sorted(crosswalk[0].keys()))
        writer.writeheader()
        writer.writerows(crosswalk)
