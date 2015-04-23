python-chicago
==============

Information about Chicago and it's geographies.  Inspired by [python-us](https://github.com/unitedstates/python-us/tree/master/us).

Because sometimes you just need to loop through a list of Chicago neighborhoods.

Installation
------------

Install using pip:

    pip install chicago

Usage
-----

### Iterate over community areas

    >>> from chicago import COMMUNITY_AREAS
    >>> for ca in COMMUNITY_AREAS:
    ...     print(ca.name, ca.number)
    ...
    ('Rogers Park', '1')
    ('West Ridge', '2')
    ('Uptown', '3')
    ('Lincoln Square', '4')
    ('North Center', '5')
    ('Lake View', '6')
    ('Lincoln Park', '7')
    ('Near North Side', '8')
    ('Edison Park', '9')

### Get a community area by number

    >>> COMMUNITY_AREAS.get_by_number(22)
    CommunityArea(name='Logan Square', number='22')

### Iterate over neighborhoods

    >>> from chicago import NEIGHBORHOODS
    >>> for n in NEIGHBORHOODS:
    ...     print(n)
    Albany Park
    Andersonville
    Archer Heights
    Armour Square
    Ashburn
    Auburn Gresham
    Austin
    Avalon Park
    Avondale
    Belmont Cragin


Data Sources
------------

### Community Areas

[Boundaries - Community Areas (current)](https://data.cityofchicago.org/Facilities-Geographic-Boundaries/Boundaries-Community-Areas-current-/cauq-8yn6))

### Neighborhoods

[Boundaries - Neighborhoods](https://data.cityofchicago.org/Facilities-Geographic-Boundaries/Boundaries-Neighborhoods/bbvz-uum9) from the City of Chicago Data Portal
