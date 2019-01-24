#!/usr/bin/python
# -*- coding: utf-8 -*- 

from time import sleep
import sys
import json
import requests
import configparser

inifile = configparser.ConfigParser()
inifile.read('../../env/config.ini')

ig_access_token = inifile.get('instagram', 'access_token')

args = sys.argv
arg_num = len(args)

hashtag = args[1]
max_id = ''

url = "https://www.instagram.com/explore/tags/" + hashtag + "/?__a=1"
base_dir = "/home/hiroki/SpatialKG/ranking_cities/{area}/".format(area=hashtag)
filename = "{dir}/{area}_{max_id}.json".format(dir=base_dir,area=hashtag,max_id=0)

headers = {"content-type": "application/json"}
res = requests.get(url, headers=headers)

max_files = 10000
files = 0

while res.status_code == 200 :
    # TODO
    # content-length compare with res.text
    
    if max_files < files :
        sys.exit()

    # file download
    with open(filename, mode='w') as f:
        f.write(res.text)

    files+=1

    # find next url
    # Content-Length分をread  
    #json_text = res.read(length)  
        
    timelines = json.loads(res.text)
    #timelines = json.loads(json_text)

    if timelines['graphql']['hashtag']['edge_hashtag_to_media']['page_info']['has_next_page'] :
        max_id = timelines['graphql']['hashtag']['edge_hashtag_to_media']['page_info']['end_cursor']
        filename = "{dir}/{area}_{max_id}.json".format(dir=base_dir,area=hashtag,max_id=max_id)
    else :
        max_id = None;
        filename = "{dir}/{area}_last.json".format(dir=base_dir,area=hashtag)

    sleep(3)
    if max_id is not None :
        print("NEXT call : " + url + "&max_id=" + str(max_id))
        res = requests.get(url + "&max_id=" + str(max_id), headers = headers)
        #headers_data = res.info()  
        # ヘッダーからContent-Lengthを取得  
        #json_length = int(headers_data.getheader('Content-Length', -1))  
        #print(json_length)
    else :
        res.status_code = 404

print(url + "&max_id=" + str(max_id) + " : " +res.status_code)
