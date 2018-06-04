import json, config #標準のjsonモジュールとconfig.pyの読み込み
from time import sleep
from requests_oauthlib import OAuth1Session #OAuthのライブラリの読み込み

CK = config.CONSUMER_KEY
CS = config.CONSUMER_SECRET
AT = config.ACCESS_TOKEN
ATS = config.ACCESS_TOKEN_SECRET
twitter = OAuth1Session(CK, CS, AT, ATS) #認証処理

url = "https://api.twitter.com/1.1/search/tweets.json" #タイムライン取得エンドポイント

# Maxまで取得
from_id = ''
count = 100
query = "お台場"

params ={'count' : count,
        #'max_id' : '',
        'result_type' : "recent",
        'q' : query}
res = twitter.get(url, params = params)

# kml format
"""
    <Placemark>
        <name>南清水沢（2014）</name>
        <description><![CDATA[夕張中学校、本照寺、道営歩団地、南清水沢生活館、夕張川]]></description>
        <Point>
            <gx:drawOrder>1</gx:drawOrder>
            <coordinates>142.00485,42.98521111111111,0</coordinates>
        </Point>
    </Placemark>
"""
# geo example
# {'type': 'Point', 'coordinates': [35.26993594, 139.67680582]}

while res.status_code == 200: #正常通信出来た場合
    timelines = json.loads(res.text) #レスポンスからタイムラインリストを取得
    #print(timelines)
    for line in timelines['statuses']: #タイムラインリストをループ処理
        #print(line)
        if ( (line['geo']) or (line['place']) ) :
            print("<Placemark>")
            print("    <name>" + line['user']['screen_name'] + "</name>")
            print("    <TimeStamp>")
            print("        <when>" + line['created_at'] + "</when>")
            print("    </TimeStamp>")
            if line['geo'] :
                print("    <description><![CDATA[" + line['text'] + "]]></description>")
                print("    <Point>")
                print("        <gx:drawOrder>1</gx:drawOrder>")
                print("        <coordinates>" + str(line['geo']['coordinates'][1]) + "," + str(line['geo']['coordinates'][0]) + "</coordinates>")
                print("    </Point>")
            if line['place'] :
                print("    <description><![CDATA[" + line['text'] + "\n TW_GEO_DATA : " + json.dumps(line['place']) + "]]></description>")
            print("</Placemark>")

        from_id = line['id'] - 1

    # parms
    #print("tweet ID : " + str(line['id']))
    #print(timelines['search_metadata']['max_id'])
    #from_id = timelines['search_metadata']['max_id'] - 1
    #next_results = timelines['search_metadata']['next_results']

    # 再度API呼び出し
    sleep(5)
    params ={'count' : count,
            'max_id' : from_id,
            'result_type' : "recent",
            'q' : query}
    print("NEXT call : " + str(from_id))
    #res = twitter.get(url+"next_results")
    res = twitter.get(url, params = params)

#else: #正常通信出来なかった場合
print("Failed: %d" % res.status_code)
