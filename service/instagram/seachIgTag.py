#!/usr/bin/python
# -*- coding: utf-8 -*- 

from time import sleep
import json
import requests
import configparser

inifile = configparser.ConfigParser()
inifile.read('../../env/config.ini')

ig_access_token = inifile.get('instagram', 'access_token')

hashtag = "odaiba"
max_id = ''

url = "https://www.instagram.com/explore/tags/" + hashtag + "/?__a=1"

headers = {"content-type": "application/json"}
res = requests.get(url, headers=headers)

while res.status_code == 200 :
    # TODO
    # content-length compare with res.text
    
    timelines = json.loads(res.text)

    if timelines['graphql']['hashtag']['edge_hashtag_to_media']['page_info']['has_next_page'] :
        max_id = timelines['graphql']['hashtag']['edge_hashtag_to_media']['page_info']['end_cursor']
    else :
        max_id = None;

    for line in timelines['graphql']['hashtag']['edge_hashtag_to_media']['edges'] :
        # individual photo url
        p_url = "https://www.instagram.com/p/" + line['node']['shortcode'] + "/?__a=1"
        sleep(0.5)
        p_res = requests.get(p_url, headers=headers)
        if p_res.status_code == 200:
            photo_data = json.loads(p_res.text)
            # text
            text = ''
            if photo_data['graphql']['shortcode_media']['edge_media_to_caption']['edges'] :
                for text_data in photo_data['graphql']['shortcode_media']['edge_media_to_caption']['edges'] :
                    text += text_data['node']['text']

            print("<Placemark>")
            print("    <name>" + photo_data['graphql']['shortcode_media']['owner']['username'] + "</name>")
            print("    <TimeStamp>")
            print("        <when>" + str(photo_data['graphql']['shortcode_media']['taken_at_timestamp']) + "</when>")
            print("    </TimeStamp>")
            print("    <description><![CDATA[" + text + "]]></description>")

            if photo_data['graphql']['shortcode_media']['location'] :
                loc_url = "https://www.instagram.com/explore/locations/{loc_id}/{slug}/?__a=1".format(loc_id=photo_data['graphql']['shortcode_media']['location']['id'], slug=photo_data['graphql']['shortcode_media']['location']['slug'])

                loc_res = requests.get(loc_url, headers=headers)
                if loc_res.status_code == 200:
                    loc_data = json.loads(loc_res.text)
                    print("    <Point>")
                    print("        <gx:drawOrder>1</gx:drawOrder>")
                    print("        <coordinates>" + str(loc_data['graphql']['location']['lng']) + "," + str(loc_data['graphql']['location']['lat']) + "</coordinates>")
                    print("    </Point>")

            print("</Placemark>")


    sleep(3)
    if max_id is not None :
        print("NEXT call : " + str(max_id))
        res = requests.get(url + "&max_id=" + str(max_id), headers = headers)
    else :
        res.status_code = 404

#else: #正常通信出来なかった場合
#    print("Failed: %d" % res.status_code)
