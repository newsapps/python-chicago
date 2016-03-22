"""Tasks for generating data files that underly this package"""
import csv
import errno
import json
import os
import shutil

from six.moves.urllib.parse import urlparse

import fiona
import requests
from shapely.geometry import shape


BASE_DIR = os.path.dirname(os.path.realpath(__file__))
TEMP_DATA_DIR = os.path.join(BASE_DIR, '_data')
OUTPUT_DATA_DIR = os.path.join(BASE_DIR, 'chicago', 'data')


# Some utility functions

def _mkdir_p(path):
    """
    Create a directory, and its ancestors, failing silently if it already
    exists
    """

    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def _url_filename(url):
    """Get the filename from a file URL"""
    url_parsed = urlparse(url)
    return url_parsed.path.split('/')[-1]


def _download_file(url, dest=None):
    """Download a file from a URL"""
    if dest is None:
        dest = os.path.join(TEMP_DATA_DIR, _url_filename(url))

    dest_dir = os.path.dirname(dest)
    _mkdir_p(dest_dir)

    response = requests.get(url)

    with open(dest, 'w') as f:
        f.write(response.content)


ILLINOIS_TRACTS_SHAPEFILE_URL = 'http://www2.census.gov/geo/tiger/TIGER2015/TRACT/tl_2015_17_tract.zip'
ILLINOIS_COUNTY_FIPS_URL = 'http://www2.census.gov/geo/docs/reference/codes/files/st17_il_cou.txt'


def download_chicago_tracts(
        url='https://data.cityofchicago.org/api/geospatial/5jrd-6zik?method=export&format=GeoJSON',
        dest=None):
    """
    Download census tract GeoJSON from url.
    """
    if dest is None:
        dest = os.path.join(TEMP_DATA_DIR, 'chicago_tracts.geojson')

    _download_file(url, dest=dest)


def download_illinois_tracts(
        url=ILLINOIS_TRACTS_SHAPEFILE_URL,
        dest=None):
    """Download zip containing all census tracts in Illinois"""

    _download_file(url, dest=dest)


def download_illinois_county_fips_codes(
        url=ILLINOIS_COUNTY_FIPS_URL,
        dest=None):
    """Download Illinois county FIPS codes"""

    _download_file(url, dest=dest)


def download_chicago_precincts(
        url='https://data.cityofchicago.org/api/geospatial/uvpq-qeeq?method=export&format=GeoJSON',
        dest=None):
    """
    Download precinct GeoJSON from url. Set precincts_as_of flag to indicate vintage of precinct
    data.
    """
    if dest is None:
        dest = os.path.join(TEMP_DATA_DIR, 'chicago_precincts.geojson')

    _download_file(url, dest=dest)


def download_suburban_cook_precincts(
      url='https://datacatalog.cookcountyil.gov/api/geospatial/mtie-43p4?method=export&format=GeoJSON',
      dest=None):
    if dest is None:
        dest = os.path.join(TEMP_DATA_DIR, 'suburban_cook_precincts.geojson')

    _download_file(url, dest=dest)


def build_county_fips_crosswalk(src=None, dest=None):
    """
    Generate a CSV of Illinois county FIPS codes, to allow us to convert back
    and forth between county names and FIPS codes.
    """
    if src is None:
        src = os.path.join(TEMP_DATA_DIR,
            _url_filename(ILLINOIS_COUNTY_FIPS_URL))

    if dest is None:
        dest = os.path.join(OUTPUT_DATA_DIR, 'county_fips.csv')

    fieldnames = ['State', 'StateFP', 'CountyFP', 'County', 'H1']

    with open(src) as f:
        with open(dest, 'w') as f_out:
            # The input file is essentially a CSV without a header
            # Just re-write it to a new output file with a header
            reader = csv.DictReader(f, fieldnames=fieldnames)
            writer = csv.DictWriter(f_out, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                writer.writerow(row)


def generate_county_tracts_geojson(src=None, dest=None, county='Cook'):
    """
    Open a zipped shapefile of all census Tracts in Illinois and save GeoJSON of
    specified county's tracts.
    """
    if src is None:
        src = os.path.join(TEMP_DATA_DIR, _url_filename(ILLINOIS_TRACTS_SHAPEFILE_URL))

    if dest is None:
        root, ext = os.path.splitext(src)
        dest = root + '__' + county.lower() + '.geojson'

    from chicago.illinois.counties import COUNTIES
    county_info = COUNTIES.get_by_name(county)

    with fiona.open('/tl_2015_17_tract.shp', vfs='zip://' + src) as shp:
        tract_geojson = {
            'type': 'FeatureCollection',
            'features': []
        }

        for row in shp:
            if row['properties']['COUNTYFP'] == county_info.countyfp:
                tract_geojson['features'].append(row)

        with open(dest, 'w') as f:
            f.write(json.dumps(tract_geojson))


def build_suburban_cook_precincts_csv(src=None, dest=None, vintage=2016):
    """
    Save precinct properties from GeoJSON to a CSV.
    """
    if src is None:
        src = os.path.join(TEMP_DATA_DIR, 'suburban_cook_precincts.geojson')

    if dest is None:
        dest_filename = 'cook_suburban_precincts_as_of_{}.csv'.format(vintage)
        dest = os.path.join(OUTPUT_DATA_DIR, dest_filename)

    with open(src) as f:
        with open(dest, 'w') as f_out:
            geojson = json.load(f)

            fieldnames = sorted(geojson['features'][0]['properties'].keys())
            writer = csv.DictWriter(f_out, fieldnames=fieldnames)
            writer.writeheader()

            for feature in geojson['features']:
                writer.writerow(feature['properties'])


def _generate_precinct_tract_crosswalk(tracts_path, precincts_path, dest,
        tract_properties, precinct_properties, crosswalk_tract_properties):
    with open(precincts_path) as fh:
        precincts = json.loads(fh.read())

    with open(tracts_path) as fh:
        tracts = json.loads(fh.read())

    # Create iterable of shapely geometries of tracts, since there are fewer & they're bigger
    tract_geos = []
    for tract in tracts['features']:
        tract_geo = {}
        for src_prop, dst_prop in tract_properties:
            tract_geo[dst_prop] = tract['properties'].get(src_prop, '')

        tract_geo['shape'] = shape(tract['geometry'])
        tract_geos.append(tract_geo)

    # Now, loop over precincts, take the centroid of each and find the tract that centroid is in
    with open(dest, 'w') as fh:
        fieldnames = [dst_prop for src_prop, dst_prop in precinct_properties]
        fieldnames += [dst_prop for src_prop, dst_prop in crosswalk_tract_properties]
        writer = csv.DictWriter(fh, sorted(fieldnames))
        writer.writeheader()

        for precinct in precincts['features']:
            centroid = shape(precinct['geometry']).centroid

            cw = {}

            for src_prop, dst_prop in precinct_properties:
                cw[dst_prop] = precinct['properties'].get(src_prop, None)

            for tract in tract_geos:
                if tract['shape'].contains(centroid):
                    for src_prop, dst_prop in crosswalk_tract_properties:
                        cw[dst_prop] = tract[src_prop]

                    break

            # Every precinct should map to some tract
            assert cw['tract_geoid']

            writer.writerow(cw)


def generate_chicago_precinct_tract_crosswalk(precincts_path=None,
        tracts_path=None, dest=None):
    """
    Generate crosswalk of precincts<->census tracts for Chicago.
    """

    if precincts_path is None:
        precincts_path = os.path.join(TEMP_DATA_DIR, 'chicago_precincts.geojson')

    if tracts_path is None:
        tracts_path = os.path.join(TEMP_DATA_DIR, 'chicago_tracts.geojson')

    if dest is None:
        dest = os.path.join(OUTPUT_DATA_DIR, 'chicago_precinct_census_tract_crosswalk.csv')

    tract_properties = (
        ('geoid10', 'geoid10'),
        ('name10', 'name10'),
        ('countyfp10', 'countyfp10'),
        ('commarea_n', 'commarea_num'),
        ('statefp10', 'statefp10'),
    )

    precinct_properties = (
        ('precinct', 'precinct_number'),
        ('ward', 'precinct_ward'),
        ('full_text', 'precinct_full_name'),
    )

    crosswalk_tract_properties = (
        ('geoid10', 'tract_geoid'),
        ('name10', 'tract_name'),
        ('countyfp10', 'tract_countyfp'),
        ('commarea_num', 'tract_commarea_num'),
        ('statefp10', 'tract_statefp'),
    )

    _generate_precinct_tract_crosswalk(tracts_path, precincts_path, dest,
        tract_properties, precinct_properties, crosswalk_tract_properties)


def generate_suburban_cook_precinct_tract_crosswalk(precincts_path=None,
        tracts_path=None, dest=None):
    """
    Generate crosswalk of precincts<->census tracts for suburban Cook County.
    """
    if precincts_path is None:
        precincts_path = os.path.join(TEMP_DATA_DIR, 'suburban_cook_precincts.geojson')

    if tracts_path is None:
        tracts_path = os.path.join(TEMP_DATA_DIR, 'tl_2015_17_tract__cook.geojson')

    if dest is None:
        dest = os.path.join(OUTPUT_DATA_DIR, 'suburban_cook_precinct_census_tract_crosswalk.csv')

    tract_properties = (
        ('GEOID', 'geoid'),
    )

    precinct_properties = (
       ('idpct', 'precinct_number'),
       ('objectid', 'precinct_objectid'),
    )

    crosswalk_tract_properties = (
       ('geoid', 'tract_geoid'),
    )

    _generate_precinct_tract_crosswalk(tracts_path, precincts_path, dest,
        tract_properties, precinct_properties, crosswalk_tract_properties)


def build_precinct_to_tract_crosswalks():
    download_chicago_tracts()
    download_illinois_tracts()
    download_illinois_county_fips_codes()
    download_chicago_precincts()
    download_suburban_cook_precincts()

    build_county_fips_crosswalk()
    generate_county_tracts_geojson()
    build_suburban_cook_precincts_csv()
    generate_chicago_precinct_tract_crosswalk()
    generate_suburban_cook_precinct_tract_crosswalk()


def clean():
    shutil.rmtree(TEMP_DATA_DIR)

