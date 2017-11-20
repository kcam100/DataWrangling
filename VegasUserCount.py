#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Data Wrangling Project
By: Kyle Campbell
"""

import xml.etree.cElementTree as ET

OSM = 'las-vegas_nevada.osm'

# Searching for, and returning UID (User ID)
def get_user(element):
    if element.tag in ["node", "way", "relation"]:
        return element.attrib["uid"]
    else:
        return None

# Creating a set of UIDs
def process_map(filename):
    users = set()
    for _, element in ET.iterparse(filename):
        if 'uid' in element.attrib:
            users.add(element.get('uid'))
    return users
    
# Printing number of Unique UIDs
x = process_map(OSM)
print '# of Unique UIDs:'
print len(x)
