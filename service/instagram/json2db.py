#!/usr/bin/python
# -*- coding: utf-8 -*- 

import sys
from time import sleep
import json
import requests
import configparser
from os import listdir
from os.path import isfile, join
import mysql.connector

inifile = configparser.ConfigParser()
inifile.read('../../env/config.ini')

json_data_dir = inifile.get('general', 'json_data_dir')

retry = int(inifile.get('general', 'retry_num'))
ig_access_token = inifile.get('instagram', 'access_token')

args = sys.argv
arg_num = len(args)

hashtag = args[1]

max_id = ''
headers = {"content-type": "application/json"}

followers_hash = inifile.get('instagram','followers_hash')
follow_hash = inifile.get('instagram','follow_hash')

# mysql connect
dbcon = mysql.connector.connect(
  database=inifile.get('mysql','db_name'),
  user=inifile.get('mysql','db_user'),
  password=inifile.get('mysql','db_password'),
  host=inifile.get('mysql','db_host'),
  charset='utf8'
)
dbcur = dbcon.cursor()

# base query
stmt_ins_entity = 'INSERT INTO entities (photo_id, shortcode, url, photo_url, user_id, text, hashtags, location_id, poi, timestamp, service) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, ST_GeomFromText("POINT(%s %s)"), %s, %s)'
stmt_ins_entity_no_loc = 'INSERT INTO entities (photo_id, shortcode, url, photo_url, user_id, text, hashtags, timestamp, service) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)'
stmt_ins_location = "INSERT INTO locations (location_id, url, name, geo, service, country) VALUES(%s, %s, %s, ST_GeomFromText('POINT(%s %s)'), %s, %s)"
stmt_ins_users = 'INSERT INTO users () VALUES()'
stmt_ins_follows = 'INSERT INTO follows () VALUES()'

stmt_sel_entity = 'SELECT COUNT(*) FROM entities WHERE shortcode = %s'
stmt_sel_location = 'SELECT ST_X(geo) AS lng, ST_Y(geo) AS lat FROM locations WHERE location_id = %s'


def get_user_info():
    return {
            "username": inifile.get('instagram','username'),
            "password": inifile.get('instagram','password')
            }

# HTTP Headers to login
def login_http_headers():
    ua = "".join(["Mozilla/5.0 (Windows NT 6.1; WOW64) ",
                  "AppleWebKit/537.36 (KHTML, like Gecko) ",
                  "Chrome/56.0.2924.87 Safari/537.36"])
    return {
            "user-agent": ua,
            "referer":"https://www.instagram.com/",
            "x-csrftoken":"null",
            "cookie":"sessionid=null; csrftoken=null"
            }

# login session
def logined_session():
    session = requests.Session()
    login_headers = login_http_headers()
    user_info = get_user_info()
    login_url = "https://www.instagram.com/accounts/login/ajax/"
    session.post(login_url, data=user_info, headers=login_headers)
    return session

# a fetch (max 3000 followers)
def fetch_followers(session, user_id, query_id, after=None):
    variables = {
        "id": user_id,
        "first": 3000,
    }
    if after:
        variables["after"] = after

    followers_url = "".join(["https://www.instagram.com/graphql/query/?",
                             "query_hash=" + query_id + "&",
                             "variables=" + json.dumps(variables)])
    # HTTP Request
    followers = session.get(followers_url)
    #print(followers)
    dic = json.loads(followers.text)
    if "edge_followed_by" in dic["data"]["user"]:
        edge_followed_by = dic["data"]["user"]["edge_followed_by"]
    else:
        edge_followed_by = dic["data"]["user"]["edge_follow"]

    count = edge_followed_by["count"] # number of followers
    after = edge_followed_by["page_info"]["end_cursor"] # next pagination
    has_next = edge_followed_by["page_info"]["has_next_page"]
    return {
            "count": count,
            "after": after,
            "has_next":  has_next,
            "followers": edge_followed_by["edges"]
            }

def fetch_all_followers(session, user_id, query_id):
    after     = None # pagination
    followers = []  

    while(True):
        fetched_followers = fetch_followers(session, user_id, query_id, after)
        followers += fetched_followers["followers"]

        if fetched_followers["has_next"]:
            after = fetched_followers["after"]
        else:
            return {
                    "count": fetched_followers["count"],
                    "followers": followers
                    }

# login session
#session = logined_session()

dbcur.execute('SET NAMES utf8mb4')
dbcur.execute("SET CHARACTER SET utf8mb4")
dbcur.execute("SET character_set_connection=utf8mb4")
dbcur.execute("SET character_set_database=utf8mb4")
dbcur.execute("SET character_set_server=utf8mb4")
dbcur.execute("SET collation_database=utf8mb4_general_ci")
dbcur.execute("SET collation_server=utf8mb4_general_ci")

#dbcur.execute("show variables like 'char%'")
#_rows = dbcur.fetchall()
#for row in _rows :
#    print(row)


json_files = [f for f in listdir(json_data_dir+'/'+hashtag) if isfile(join(json_data_dir+'/'+hashtag, f))]
for filename in json_files :

    print("try : " + filename)

    with open(json_data_dir+'/'+hashtag+'/'+filename, mode='r') as f:
        timelines = json.load(f)

        total_count = timelines['graphql']['hashtag']['edge_hashtag_to_media']['count']
        #print("総数：{num}".format(num=total_count))

        if timelines['graphql']['hashtag']['edge_hashtag_to_media']['page_info']['has_next_page'] :
            max_id = timelines['graphql']['hashtag']['edge_hashtag_to_media']['page_info']['end_cursor']
        else :
            max_id = None;

        for line in timelines['graphql']['hashtag']['edge_hashtag_to_media']['edges'] :
            # isExist on DB
            dbcur.execute(stmt_sel_entity, (line['node']['shortcode'], ))
            _rows = dbcur.fetchall()
            if _rows[0][0] >= 1 :
                continue

            # individual photo url
            _p_url = "https://www.instagram.com/p/" + line['node']['shortcode'] + "/"
            p_url = "https://www.instagram.com/p/" + line['node']['shortcode'] + "/?__a=1"

            # table rows initialize
            photo_id = line['node']['id']
            shortcode = line['node']['shortcode']
            url = _p_url
            photo_url = ''
            user_id = ''
            text = ''
            hashtag_id = ''
            hashtags = hashtag
            location_id = ''
            poi = ''
            timestamp = ''
            service = 2 # twitter:01, instagram:02

            print("try : " + p_url)
            sleep(3)
            p_res = requests.get(p_url, headers=headers)
            if p_res.status_code == 200:
                photo_data = json.loads(p_res.text)
                # text
                _text = ''
                if photo_data['graphql']['shortcode_media']['edge_media_to_caption']['edges'] :
                    for text_data in photo_data['graphql']['shortcode_media']['edge_media_to_caption']['edges'] :
                        _text += text_data['node']['text']

                photo_url = photo_data['graphql']['shortcode_media']['display_url']
                user_id = photo_data['graphql']['shortcode_media']['owner']['id']
                #text = _text.encode('unicode_escape')
                text = _text
                timestamp = photo_data['graphql']['shortcode_media']['taken_at_timestamp']

                # hashtag from text
                #hashtag_id = 
                #hashtags = 

                """
                # follow
                sleep(1)
                follow_url = "https://www.instagram.com/graphql/query/?query_hash=" + follow_hash + "&variables=%7B%22id%22%3A%22" + photo_data['graphql']['shortcode_media']['owner']['id']  + "%22%2C%22first%22%3A24%7D"
                #follow_res = requests.get(follow_url, headers=headers)
                #follow_res = session.get(follow_url)
                #if follow_res.status_code == 200:
                #    follow_data = json.loads(follow_res.text)
                #    print(follow_data['data']['user']['edge_follow']['count'])
                #else:
                #    print(follow_res.status_code)
                #    print(follow_url)

                follow = fetch_all_followers(session, photo_data['graphql']['shortcode_media']['owner']['id'], follow_hash)
                print(follow['count'])
                #for follower in followers['followers']:
                #    print(follower)

                # followers
                #sleep(1)
                #followers_url = "https://www.instagram.com/graphql/query/?query_hash=" + followers_hash + "&variables=%7B%22id%22%3A%22" + photo_data['graphql']['shortcode_media']['owner']['id']  + "%22%2C%22first%22%3A24%7D"
                #followers_res = requests.get(followers_url, headers=headers)
                #followers_res = session.get(followers_url)
                #if followers_res.status_code == 200:
                #    followers_data = json.loads(followers_res.text)
                #    print(followers_data['data']['user']['edge_followed_by']['count'])
                #else:
                #    print(followers_res.status_code)
                #    print(followers_url)

                followers = fetch_all_followers(session, photo_data['graphql']['shortcode_media']['owner']['id'], followers_hash)
                print(followers['count'])
                #print(followers['followers'])
                for follower in followers['followers']:
                    print(follower['node']['id'])
                """

                # has location
                if photo_data['graphql']['shortcode_media']['location'] :
                    _lng = ''
                    _lat = ''
                    loc_name = ''

                    # isExist locations table
                    location_id = photo_data['graphql']['shortcode_media']['location']['id']
                    dbcur.execute(stmt_sel_location, (location_id, ))
                    _rows = dbcur.fetchall()
                    if len(_rows) >= 1 :
                        _lng = _rows[0][0]
                        _lat = _rows[0][1]
                    else :
                        _loc_url = "https://www.instagram.com/explore/locations/{loc_id}/{slug}".format(loc_id=photo_data['graphql']['shortcode_media']['location']['id'], slug=photo_data['graphql']['shortcode_media']['location']['slug'])
                        loc_url = "https://www.instagram.com/explore/locations/{loc_id}/{slug}?__a=1".format(loc_id=photo_data['graphql']['shortcode_media']['location']['id'], slug=photo_data['graphql']['shortcode_media']['location']['slug'])

                        sleep(1)
                        loc_res = requests.get(loc_url, headers=headers)
                        if loc_res.status_code == 200:
                            loc_data = json.loads(loc_res.text)
                            _lng = loc_data['graphql']['location']['lng']
                            _lat = loc_data['graphql']['location']['lat']
                            loc_name = loc_data['graphql']['location']['name']

                            # construct location insert query.
                            if _lng == None or _lat == None :
                                #print('Location {name} error : {url}'.format(name=loc_name,url=loc_url))
                                print('Location data error : {url}'.format(url=loc_url))
                                _lng = 0
                                _lat = 0

                            dbcur.execute(stmt_ins_location, (location_id, _loc_url, loc_name, _lng, _lat, service, hashtags))

                    # construct entity insert query.
                    dbcur.execute(stmt_ins_entity, (photo_id, shortcode, _p_url, photo_url, user_id, text, hashtags, location_id, _lng, _lat, timestamp, service))

                else :
                    # construct entity insert query.
                    dbcur.execute(stmt_ins_entity_no_loc, (photo_id, shortcode, _p_url, photo_url, user_id, text, hashtags, timestamp, service))
                

                # DEBUG
                dbcon.commit()

            else :
                continue


dbcon.close()


