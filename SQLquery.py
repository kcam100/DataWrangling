#!/usr/bin/env python

"""
Data Wrangling Project
By: Kyle Campbell
"""

import sqlite3
import csv

# Name of SQL DB
SQL_DB = 'sqldb.db'

# DB Connection
conn = sqlite3.connect(SQL_DB)

# Create cursor object
c = conn.cursor()

# Drop old tables
c.execute('''DROP TABLE IF EXISTS nodes_tags''')
c.execute('''DROP TABLE IF EXISTS nodes''')
c.execute('''DROP TABLE IF EXISTS ways''')
c.execute('''DROP TABLE IF EXISTS ways_tags''')
c.execute('''DROP TABLE IF EXISTS ways_nodes''')
conn.commit()

# Create nodes table
c.execute('''CREATE TABLE nodes (
    id INTEGER PRIMARY KEY NOT NULL,
    lat REAL,
    lon REAL,
    user TEXT,
    uid INTEGER,
    version INTEGER,
    changeset INTEGER,
    timestamp TEXT
)''')

# Pass csv into nodes table
with open ('nodes.csv', 'rb') as f:
    dr = csv.DictReader(f)
    to_db = [(i['id'], i['lat'], i['lon'], i['user'].decode("utf-8"), 
              i['uid'], i['version'], i['changeset'], 
              i['timestamp']) for i in dr]

c.executemany('''INSERT INTO nodes (id, lat, lon, user, uid, version, 
                                    changeset, timestamp) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?);''', to_db)

conn.commit()

# Create nodes_tags table
c.execute('''CREATE TABLE nodes_tags (
    id INTEGER,
    key TEXT,
    value TEXT,
    type TEXT,
    FOREIGN KEY (id) REFERENCES nodes(id)
)''')

# Pass csv into nodes_tags table
with open ('nodes_tags.csv', 'rb') as f:
    dr = csv.DictReader(f)
    to_db = [(i['id'], i['key'], i['value'].decode("utf-8"), 
              i['type']) for i in dr]

c.executemany('''INSERT INTO nodes_tags (id, key, value, type) 
                 VALUES (?, ?, ?, ?);''', to_db)

conn.commit()


# Create ways table
c.execute('''CREATE TABLE ways (
    id INTEGER PRIMARY KEY NOT NULL,
    user TEXT,
    uid INTEGER,
    version TEXT,
    changeset INTEGER,
    timestamp TEXT
) ''')

# Pass csv into ways table
with open ('ways.csv', 'rb') as f:
    dr = csv.DictReader(f)
    to_db = [(i['id'], i['user'].decode("utf-8"), i['uid'], i['version'], 
              i['changeset'], i['timestamp']) for i in dr]

c.executemany('''INSERT INTO ways (id, user, uid, version, changeset,
                                    timestamp)
                 VALUES (?, ?, ?, ?, ?, ?);''', to_db)

conn.commit()

# Create ways_tags table
c.execute('''CREATE TABLE ways_tags (
    id INTEGER NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    type TEXT,
    FOREIGN KEY (id) REFERENCES ways(id)
)''')

# Pass csv into ways_tags table
with open ('ways_tags.csv', 'rb') as f:
    dr = csv.DictReader(f)
    to_db = [(i['id'], i['key'], i['value'].decode("utf-8"),
              i['type']) for i in dr]

c.executemany('''INSERT INTO ways_tags (id, key, value, type) 
                 VALUES (?, ?, ?, ?);''', to_db)

conn.commit()

# Create ways_nodes table
c.execute('''CREATE TABLE ways_nodes (
    id INTEGER NOT NULL,
    node_id INTEGER NOT NULL,
    position INTEGER NOT NULL,
    FOREIGN KEY (id) REFERENCES ways(id),
    FOREIGN KEY (node_id) REFERENCES nodes(id)
)''')

# Pass csv into ways_nodes table
with open ('ways_nodes.csv', 'rb') as f:
    dr = csv.DictReader(f)
    to_db = [(i['id'], i['node_id'], i['position']) for i in dr]

c.executemany('''INSERT INTO ways_nodes (id, node_id, position) 
                 VALUES (?, ?, ?);''', to_db)

conn.commit()


# ------------------------------------------------
#             Queries start here 
# ------------------------------------------------

# Number of unique users
def unique():
    u = c.execute('''SELECT COUNT(DISTINCT(uid))          
                      FROM (SELECT uid FROM nodes UNION
                            SELECT uid FROM ways)''')
    return u.fetchone()[0]
print unique()


# Number of nodes
def node_count():
    nc = c.execute('''SELECT COUNT(*) FROM nodes''')
    return nc.fetchone()[0]
print node_count()

# Number of ways
def ways_count():
    w = c.execute('''SELECT COUNT(*) FROM ways''')
    return w.fetchone()[0]
print ways_count()

# Number of cafes
def cafe_count():
    cc = c.execute('''SELECT COUNT(*) FROM nodes_tags
                      WHERE nodes_tags.value = 'cafe' OR
                      nodes_tags.value = 'coffee_shop' ''')
    return cc.fetchone()[0]
print cafe_count()


# ----------- ADDITIONAL QUERIES --------------------- #

# Top 10 contributing users
def top_contributing():
    uc = []
    for row in c.execute('''SELECT user, COUNT(user) as NUM
                            FROM (SELECT user FROM nodes UNION ALL 
                                  SELECT user FROM ways) 
                            GROUP BY user 
                            ORDER BY NUM DESC 
                            LIMIT 10'''):
                                uc.append(row)
    return uc
print top_contributing()


# Most popular religion
def religion():
    mpr = c.execute('''SELECT nodes_tags.value, COUNT(*) as NUM
                       FROM nodes_tags JOIN 
                       (SELECT DISTINCT(id) FROM nodes_tags 
                       WHERE value='place_of_worship') pow
                       ON nodes_tags.id = pow.id
                       WHERE nodes_tags.key='religion'
                       GROUP BY nodes_tags.value
                       ORDER BY num DESC 
                       LIMIT 1''')
    return mpr.fetchone()[0]
print religion()

# Number of schools
def schools():
    s = c.execute('''SELECT COUNT(*) as NUM
                     FROM nodes_tags
                     WHERE nodes_tags.value = 'school' OR
                     nodes_tags.value = 'college' OR
                     nodes_tags.value = 'kindergarden' OR
                     nodes_tags.value = 'university' ''')
    return s.fetchone()[0]
print schools()

# Number of casinos
def casinos():
    cas = c.execute(''' SELECT COUNT(*) as NUM
                        FROM ways_tags
                        WHERE ways_tags.value = 'casino' OR
                        ways_tags.value = 'adult_gaming_centre' OR
                        ways_tags.value = 'amusement_arcade' OR
                        ways_tags.value = 'gambling' ''')
    return cas.fetchone()[0]
print casinos()

# Close DB connection
conn.close()