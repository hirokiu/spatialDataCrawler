#!/usr/bin/python
# -*- coding: utf-8 -*- 

from time import sleep
import configparser
from os import listdir
from os.path import isfile, join
import mysql.connector
import googlemaps
import re

inifile = configparser.ConfigParser()
inifile.read('../env/config.ini')

key = inifile.get('google', 'maps_api_key')
gmaps = googlemaps.Client(key=key)

hashtag = "Istanbul"
max_id = ''
max_locations = 5

regex_type = 'political'
pattern = ['political', 'postal_code', 'locality', 'sublocality']

# mysql connect
dbcon = mysql.connector.connect(
  database="dev_SpatialKG",
  user="root",
  password="",
  host="127.0.0.1",
)
dbcur = dbcon.cursor()

# base query
#stmt_sel_locations = 'SELECT name, url, ST_X(geo) AS lng, ST_Y(geo) AS lat FROM locations ORDER BY name LIMIT %s'
stmt_sel_locations = 'SELECT name, url, ST_X(geo) AS lng, ST_Y(geo) AS lat FROM locations LIMIT %s'

dbcur.execute(stmt_sel_locations, (max_locations, ))
_rows = dbcur.fetchall()
for loc_row in _rows :
    print("名称： "  + loc_row[0])
    print("URL： "  + loc_row[1])
    print(str(loc_row[2]) + " , " + str(loc_row[3]))
    results = gmaps.reverse_geocode((str(loc_row[3]), str(loc_row[2])))

    tmp_len = 0
    max_addr = []
    max_array = []
    #results.reverse()
    for result in results:
        types = result['types']
        if ('political' in types) or ('postal_code' in types) :
        #if ('sublocality' in types) :
            #print('types', types)
            addr = result['formatted_address']
            addr_list = addr.split(', ')
            #print('addr', addr_list)

            if tmp_len < len(addr_list) :
                max_addr = addr_list
                max_array = result
                tmp_len = len(addr_list)

    print('max_addr', max_addr)
    #print('max_result', max_array)
    last_name = loc_row[0]
    for result in max_array['address_components'] :
        print(result['long_name'] + " <- " + last_name)
        last_name = result['long_name']
        if "country" in result['types'] :
            last_name = loc_row[0]

    print("=======================================================")

exit()
