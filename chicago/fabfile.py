import fiona
import json
import requests

from csv import DictWriter
from shapely.geometry import shape, Point
from StringIO import StringIO
from zipfile import ZipFile


def download_all_tracts_for_county(
        url='http://www2.census.gov/geo/tiger/TIGER2015/TRACT/tl_2015_17_tract.zip',
        tracts_as_of=2015,
        county='Cook'):
    """
    Download zip containing all census tracts in Illinois, and save GeoJSON of selected county's
    tracts.
    """
    response = requests.get(url)
    with open('/tmp/il_counties.zip', 'w+') as fh:
        fh.write(response.content)
    with fiona.open('/tl_2015_17_tract.shp', vfs='zip:///tmp/il_counties.zip') as shp:
        for row in shp:
            print shape(row['geometry']).centroid, row['properties']


def download_county_fips_codes(
        url='http://www2.census.gov/geo/docs/reference/codes/files/st17_il_cou.txt',
        counties_as_of=2016):
    """
    Download Illinois county FIPS codes, to allow us to convert back and forth between names and
    FIPS codes.
    """
    response = requests.get(url)
    header = ['State', 'StateFP', 'CountyFP', 'County', 'H1']
    results = []
    for row in response.content.split('\n'):
        split = row.strip().split(',')
        assert len(split) == 5
        result = {}
        for idx, val in enumerate(split):
            result[header[idx]] = val
        results.append(result)
    with open('data/county_fips.csv', 'w+') as fh:
        writer = DictWriter(fh, header)
        writer.writeheader()
        writer.writerows(results)


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


def download_suburban_precincts(
        url='https://datacatalog.cookcountyil.gov/api/geospatial/mtie-43p4?method=export&format=GeoJSON',
        precincts_as_of=2016):
    """
    Download suburban Cook precinct GeoJSON from url. Set precincts_as_of flag to indicate vintage
    of precinct data. Save GeoJSON and also save features to a CSV.
    """
    response = requests.get(url)
    assert response.status_code == 200

    data = response.json()

    with open('data/cook_suburban_precincts_as_of_%s.geojson' % precincts_as_of, 'w+') as fh:
        fh.write(json.dumps(data))

    csv_data = [feature['properties'] for feature in data['features']]
    with open('data/cook_suburban_precincts_as_of_%s.csv' % precincts_as_of, 'w+') as fh:
        writer = DictWriter(fh, sorted(csv_data[0].keys()))
        writer.writeheader()
        writer.writerows(csv_data)


def download_tracts(
        url='https://data.cityofchicago.org/api/geospatial/5jrd-6zik?method=export&format=GeoJSON',
        tracts_as_of=2010):
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
            'geoid10': tract['properties'].get('geoid10', ''),
            'name10': tract['properties'].get('name10', ''),
            'countyfp10': tract['properties'].get('countyfp10', ''),
            'commarea_num': tract['properties'].get('commarea_n', ''),
            'statefp10': tract['properties'].get('statefp10', ''),
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
            'tract_geoid': None,
            'tract_name': None,
            'tract_countyfp': None,
            'tract_commarea_num': None,
            'tract_statefp': None
        }
        for tract in tract_geos:
            if tract['shape'].contains(centroid):
                cw['tract_geoid'] = tract['geoid10']
                cw['tract_name'] = tract['name10']
                cw['tract_countyfp'] = tract['countyfp10']
                cw['tract_commarea_num'] = tract['commarea_num']
                cw['tract_statefp'] = tract['statefp10']
                break
        if not cw['tract_geoid']:
            print 'No tract matches precinct %s' % cw['precinct_full_name']
        crosswalk.append(cw)

    with open('data/precinct_census_tract_crosswalk.csv', 'w+') as fh:
        writer = DictWriter(fh, sorted(crosswalk[0].keys()))
        writer.writeheader()
        writer.writerows(crosswalk)
