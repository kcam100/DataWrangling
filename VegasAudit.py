#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Data Wrangling Project
By: Kyle Campbell
"""
# Import needed modules
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSM = "las-vegas_nevada.osm"
SAMPLE = "sample.osm"

# -------------------------------------------------
# |               STREET NAME AUDIT               |
# |                                               |
# ------------------------------------------------


# Audit street names to check for problems
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


# Expected street name values
expected = ["Street", 
            "Avenue", 
            "Boulevard",
            "Drive", 
            "Court", 
            "Place", 
            "Square", 
            "Lane", 
            "Road", 
            "Trail", 
            "Parkway", 
            "Commons"]

# Key value mapping of problematic street names to updated street name
mapping = { "Rd": "Road",
            "Ste": "Suite",
            "AVE": "Avenue",
            "Ave": "Avenue",
            "Ave.": "Avenue",
            "Blvd": "Boulevard",
            "Blvd.": "Boulevard",
            "Cir": "Circle",
            "Dr": "Drive",
            "Ln": "Lane",
            "Ln.": "Lane",
            "Mt.": "Mountain",
            "Pkwy": "Parkway",
            "Rd": "Road",
            "Rd.": "Road",
            "N.": "North",
            "S.": "South",
            "W.": "West",
            "E.": "East",
            "St": "Street",
            "St.": "Street",
            "ave": "Avenue",
            "blvd": "Boulevard",
            "drive": "Drive",
            "ln": "Lane",
            "parkway": "Parkway",
            "rainbow": "Raindow"           
            }

# Scan for street names not in 'expected' list
def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

# Check if element attribute of 'k' tag is street name
def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

# Audit street types and return list
def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types

# Print results of audit
# pprint.pprint(audit(SAMPLE))
# pprint.pprint(audit(OSM))

# Update/clean street names
def update_name(name, mapping):
    for key, value in mapping.iteritems():
        if key in name:
            name = name.replace(key, value)
            break
    return name
    
# Print old -> new street names
update_street = audit(SAMPLE) 
for street_type, ways in update_street.iteritems():
    for name in ways:
        new_name = update_name(name, mapping)
        print name, "=>", new_name  
        
        
# -------------------------------------------------
# |               STATE NAME AUDIT                |
# |                                               |
# ------------------------------------------------

# Define what state name is
def is_state(element):
    return (element.attrib['k'] == 'addr:state')

# Audit state name
def state_name_audit(osmfile):
    osm_file = open(osmfile, 'r')
    not_expected = set()
    for event, element in ET.iterparse(osm_file, events=('start',)):
        
        if element.tag == 'node' or element.tag == 'way':
            for tag in element.iter('tag'):
                if is_state(tag):
                    if tag.attrib['v'] != 'NV':
                        not_expected.add(tag.attrib['v'])
                        
    osm_file.close()
    return not_expected

# Print state names that are not 'NV'
# print state_name_audit(SAMPLE)
print state_name_audit(OSM)
        
# -------------------------------------------------
# |               CITY NAME AUDIT                 |
# |                                               |
# ------------------------------------------------

# Define what city is
def is_city(element):
    return (element.attrib['k'] == 'addr:city')

# Audit city name
def city_name_audit(osmfile):
    osm_file = open(osmfile, 'r')
    not_city = set()
    for event, element in ET.iterparse(osm_file, events=('start',)):
        
        if element.tag == 'node' or element.tag == 'way':
            for tag in element.iter('tag'):
                if is_city(tag):
                    if tag.attrib['v'] != 'Las Vegas':
                        not_city.add(tag.attrib['v'])
                        
    osm_file.close()
    return not_city

# Print city names that are not 'Las Vegas'
# print_city_name_audit(SAMPLE)
# print city_name_audit(OSM)
