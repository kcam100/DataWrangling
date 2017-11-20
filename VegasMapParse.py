#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Data Wrangling Project
By: Kyle Campbell
"""

import xml.etree.cElementTree as ET
import pprint

OSM = 'las-vegas_nevada.osm'

# Iteratively parse map file and return dictionary with tag name
# and count

def count_tags(filename):
    tags = {}
    for event, element in ET.iterparse(filename):
        if element.tag in tags: 
            tags[element.tag] += 1
        else:
            tags[element.tag] = 1
    return tags


pprint.pprint(count_tags(OSM))

