#!/usr/bin/python
# -*- coding: utf-8 -*- 

from time import sleep
import json
import configparser
from os import listdir
from os.path import isfile, join
import mysql.connector
import simplekml

inifile = configparser.ConfigParser()
inifile.read('../../env/config.ini')

user_limit = 100

# mysql connect
dbcon = mysql.connector.connect(
  database=inifile.get('mysql','db_name'),,
  user=inifile.get('mysql','db_user'),,
  password=inifile.get('mysql','db_password'),,
  host=inifile.get('mysql','db_host'),,
)
dbcur = dbcon.cursor()

stmt_sel_hashtags = 'SELECT hashtags, COUNT(*) FROM entities GROUP BY hashtags;'
stmt_sel_entity = 'SELECT COUNT(*) FROM entities WHERE shortcode = %s'
stmt_sel_location = 'SELECT ST_X(geo) AS lng, ST_Y(geo) AS lat FROM locations WHERE location_id = %s'
stmt_sel_users = 'SELECT hashtags, user_id, COUNT(*) AS cnt FROM entities WHERE location_id IS NOT NULL GROUP BY user_id, hashtags ORDER BY cnt DESC LIMIT %s'
stmt_sel_user_entity = 'SELECT en.location_id, loc.name, en.text, ST_X(loc.geo) AS lng, ST_Y(loc.geo) AS lat, count(*) AS cnt FROM entities AS en JOIN locations AS loc ON en.location_id = loc.location_id WHERE en.user_id = %s GROUP BY en.location_id ORDER BY cnt'
stmt_sel_only_entity = 'SELECT q1.u_id, q1.loc_name, q1.loc_country, q1.lng, q1.lat, COUNT(*) AS q_cnt FROM (SELECT en.user_id AS u_id, loc.name AS loc_name, loc.country AS loc_country, ST_X(loc.geo) AS lng, ST_Y(loc.geo) AS lat, count(*) AS cnt FROM entities AS en JOIN locations AS loc ON en.location_id = loc.location_id WHERE en.hashtags = %s GROUP BY en.location_id, en.user_id ORDER BY en.location_id, cnt) AS q1 GROUP BY q1.loc_name HAVING q_cnt = 1'

kml = simplekml.Kml()

"""
dbcur.execute(stmt_sel_users, (user_limit, ))
_user_rows = dbcur.fetchall()
for _user_row in _user_rows :
    kml = simplekml.Kml()
    user_id = _user_row[1]
    dbcur.execute(stmt_sel_user_entity, (user_id, ))
    _entity_rows = dbcur.fetchall()
    for _entity_row in _entity_rows :
        kml.newpoint(name=_entity_row[1], coords=[(_entity_row[3], _entity_row[4])])

    kml_name = str(_user_row[0])+"_"+str(user_id)+'.kml'
    kml.save(kml_name)

"""

dbcur.execute(stmt_sel_hashtags)
_hashtags_rows = dbcur.fetchall()
for _hashtags_row in _hashtags_rows : 
    hashtag = _hashtags_row[0]
    kml = simplekml.Kml()
    dbcur.execute(stmt_sel_only_entity, (hashtag, ))
    _entity_rows = dbcur.fetchall()
    for _entity_row in _entity_rows :
        kml.newpoint(name=_entity_row[1], coords=[(_entity_row[3], _entity_row[4])])

    kml_name = str(hashtag)+"_"+'only_loc.kml'
    kml.save(kml_name)
