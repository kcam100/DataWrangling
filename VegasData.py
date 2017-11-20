#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Data Wrangling Project
By: Kyle Campbell
"""

# A large portion of the following code is from the foundational code
# provided by Udacity. The main process below is left in for reference
# and to provide structure to the following code.

'''
The process for this transformation is as follows:
- Use iterparse to iteratively step through each top level element in the XML
- Shape each element into several data structures using a custom function
- Utilize a schema and validation library to ensure the transformed data is in the correct format
- Write each data structure to the appropriate .csv files
'''

# Import necessary modules
import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET
import cerberus
import schema

OSM_PATH = "las-vegas_nevada.osm"
SAMPLE = 'sample.osm'

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# City cleaning function to be passed to shape_element() function
def update_city(element):
    if element.tag == 'node' or element.tag == 'way':
        for secondary in element:
            if secondary.tag == 'tag':
                if secondary.attrib['v'] != 'Las Vegas':
                    if secondary.attrib['v'] == 'Las Vegas NV':
                        secondary.attrib['v'] == 'Las Vegas'
                    if secondary.attrib['v'] == 'Las vegas':
                        secondary.attrib['v'] == 'Las Vegas'
                    if secondary.attrib['v'] == 'Las Vegas, NV':
                        secondary.attrib['v'] == 'Las Vegas'
                    if secondary.attrib['v'] == 'las vegas':
                        secondary.attrib['v'] == 'Las Vegas'
                    if secondary.attrib['v'] == 'Las Vagas':
                        secondary.attrib['v'] == 'Las Vegas'
                    if secondary.attrib['v'] == 'LAS VEGAS':
                        secondary.attrib['v'] == 'Las Vegas'
                    else:
                        pass
                return secondary.attrib['v']
    
# State cleaning function to be passed to shape_element() function
def update_state(element):
    if element.tag == 'node' or element.tag == 'way':
        for secondary in element:
            if secondary.tag == 'tag':
                if secondary.attrib['v'] != 'NV':
                    if secondary.attrib['v'] =='nv':
                        secondary.attrib['v'] == 'NV'
                    if secondary.attrib['v'] =='Nevada':
                        secondary.attrib['v'] == 'NV' 
                    else:
                        pass
                return secondary.attrib['v']

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements
    
    
    # Node Fields
    if element.tag == 'node':
        for attrib in element.attrib:
            if attrib in NODE_FIELDS:
                node_attribs[attrib] = element.attrib[attrib]
                
        # Secondary Element Attribs
        for secondary in element:
            if secondary.tag == 'tag':
                tag_dict = {}
                tag_dict['id'] = element.attrib['id']
                
                # Passing over problem characters
                if PROBLEMCHARS.match(secondary.attrib['k']):
                    continue
                    
                elif LOWER_COLON.match(secondary.attrib['k']):
                    tag_dict['key'] = secondary.attrib['k'].split(':',1)[1]
                    tag_dict['type'] = secondary.attrib['k'].split(':')[0]
                    
                    # use cleaning function for city/state on node_tags
                    if secondary.attrib["k"] == 'addr:city':
                        tag_dict['value'] = update_city(element)
                    elif secondary.attrib["k"] == 'addr:state':
                        tag_dict['value'] = update_state(element)
                    else:
                        tag_dict['value'] = secondary.attrib['v']
                    tags.append(tag_dict) 
                    
                    
                else:
                    tag_dict['key'] = secondary.attrib['k']
                    tag_dict['value'] = secondary.attrib['v']
                    tag_dict['type'] = 'regular'
                    tags.append(tag_dict)
                    
        return {'node': node_attribs, 'node_tags': tags} 
        # print {'node': node_attribs, 'node_tags': tags}

                
    # Way Fields
    elif element.tag =='way':
        for attrib in element.attrib:
            if attrib in WAY_FIELDS:
                way_attribs[attrib] = element.attrib[attrib]
        
        # Secondary Element Attribs 
        position_count = 0
        for secondary in element:
            if secondary.tag == 'nd':
                way_node_dict = {}               
                way_node_dict['id'] = element.attrib['id']
                way_node_dict['node_id'] = secondary.attrib['ref']
                way_node_dict['position'] = position_count
                position_count += 1
                way_nodes.append(way_node_dict)
                    
            elif secondary.tag == 'tag':  
                way_tag_dict = {}
                way_tag_dict['id'] = element.attrib['id']
                
                # Passing over problem characters
                if PROBLEMCHARS.match(secondary.attrib['k']):
                    continue
                        
                elif LOWER_COLON.match(secondary.attrib['k']):
                    way_tag_dict['key'] = secondary.attrib['k'].split(':',1)[1]
                    way_tag_dict['type'] = secondary.attrib['k'].split(':')[0]
                    
                    # Use city/state cleaning functions on way_tags
                    if secondary.attrib['k'] == 'addr:city':
                        way_tag_dict['value'] = update_city(element)
                    elif secondary.attrib["k"] == 'addr:state':
                        way_tag_dict['value'] = update_state(element)
                    else:
                        way_tag_dict['value'] = secondary.attrib['v']
                    tags.append(way_tag_dict)
                    
                else:
                    way_tag_dict['key'] = secondary.attrib['k']
                    way_tag_dict['value'] = secondary.attrib['v']
                    way_tag_dict['type'] = 'regular'
                    tags.append(way_tag_dict)
                
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}
        # print {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}

        
    

# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(SAMPLE, validate=True)


