from datetime import datetime,timedelta,timezone
import requests
import mongodbtry

tz = timezone(timedelta(hours=8))
today=datetime.now(tz)
delta=timedelta(hours=1)
n=today-delta
hour = 96
n=n-timedelta(hours=hour)


header={
    "user-agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }

for i in range(hour+1):

    w=n.strftime("%Y%m%d%H")
    vv= datetime(n.year,n.month,n.day,n.hour,0,0,0,tzinfo=tz)

    url = "https://airtw.moenv.gov.tw/json/AQI/Taiwan_{}.json".format(w)

    resp = requests.get(url,headers=header)
    resp.encoding = "utf-8"
    data = resp.json()

    stationAqis=[]
    for row in data:
        txt = row['txt'].split()
        onedata = {'id':row['id'],'stationName':txt[0],'aqi':txt[1],'county':row['county']}
        stationAqis.append(onedata)

    cursor = mongodbtry.db.aqi.find({'datehour':vv})
    if len(list(cursor))==0:
        mongodbtry.db.aqi.insert_one({'datehour':vv,'stationList':stationAqis})
        print(vv.isoformat())
    n+=delta

print("Finish!")