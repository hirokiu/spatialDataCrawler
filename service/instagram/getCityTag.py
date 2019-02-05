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
#max_id = 'AQD3njx3Hdjw5KtBTF0gw1pSHj4i1rwpGXBdHn6B3gVbvRdPRNcmy87f1vFibsoNBua2FrtQamuhHBTK1cnjD3VcDYh2YfMxRSNP5LzfI-V_wQ'

url = "https://www.instagram.com/explore/tags/" + hashtag + "/?__a=1"
base_dir = "./data_cities/{area}/".format(area=hashtag)
filename = "{dir}/{area}_{max_id}.json".format(dir=base_dir,area=hashtag,max_id=0)
#filename = "{dir}/{area}_{max_id}.json".format(dir=base_dir,area=hashtag,max_id=max_id)

headers = {"content-type": "application/json"}
res = requests.get(url, headers=headers)
#res = requests.get(url + "&max_id=" + str(max_id), headers = headers)

max_files = 10000
files = 0
=======

while res.status_code == 200 :
    # TODO
    # content-length compare with res.text
    
    if max_files < files :
        sys.exit()

    # file download
    with open(filename, mode='w') as f:
        f.write(res.text)

    try:
        # find next url
        timelines = json.loads(res.text)

        if timelines['graphql']['hashtag']['edge_hashtag_to_media']['page_info']['has_next_page'] :
            max_id = timelines['graphql']['hashtag']['edge_hashtag_to_media']['page_info']['end_cursor']
            filename = "{dir}/{area}_{max_id}.json".format(dir=base_dir,area=hashtag,max_id=max_id)
        else :
            max_id = None;
            filename = "{dir}/{area}_last.json".format(dir=base_dir,area=hashtag)

        sleep(3)

        if max_id is not None :
            print("NEXT call : " + str(max_id))
            res = requests.get(url + "&max_id=" + str(max_id), headers = headers)
        else :
            res.status_code = 404
        
        print(url + "&max_id=" + str(max_id) + " : " +res.status_code)

    except Exception:
        #import traceback
        #traceback.print_exc()
        pass
