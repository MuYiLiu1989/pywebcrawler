from flask import Flask,render_template,request
from flask_paginate import Pagination,get_page_parameter
from urllib.request import Request,urlopen
from bs4 import BeautifulSoup
from datetime import datetime,timedelta,timezone
import mysql.connector
import requests
import json
import ssl
import re
from waitress import serve
import logging
import pymongo
import os

def dbegin():
	global conn
	conn = mysql.connector.connect(
    host='mysqlchiang',
    user = 'lcc',
    password = '0987654321',
    database = 'webcrawler',
    buffered = True
    )

	global cursor
	cursor = conn.cursor()  #建立一個資料庫操作物件

def dbclose():
	cursor.close()
	conn.close()

def mongodb():
	global client
	global db
	try:
		client = pymongo.MongoClient("mongodbaqi:27017")
	except:
		print("mongodb連接失敗")
	else:
		print("mongodb連接成功")

	db = client.crawlerdisplay

def total(table):
    page = request.args.get('page')
    sql = "select count(*) from {}".format(table)
    cursor.execute(sql)
    count = cursor.fetchone()
    count = int(count[0])
    return page,count

ssl._create_default_https_context = ssl._create_unverified_context

app = Flask(__name__)

@app.route('/')
def index():
#------------------------------------cwa溫度------------------------------------
    county=['10017','63','68','10004','66','10007','10020','67','64','10013']
#------------------------------------cwa溫度------------------------------------
#------------------------------------drama--------------------------------------
    url="https://www.litv.tv/drama/search-program/category-id/55"

    header = {
        "user-agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "referer":
    "https://www.litv.tv/drama"
    }

    data = requests.get(url,headers=header)
    data.encoding = "utf-8"
    print(data.status_code)
    data = data.text
    soup = BeautifulSoup(data,"html.parser")


    div = soup.find('div',class_="flex flex-wrap items-stretch justify-start")
    divs = div.find_all('div',class_="w-[calc(25%-20px)] min-[1024px]:w-[calc(16.66%-20px)] m-[10px]")

    drama=[]
    for row in divs:
        link0 = "https://www.litv.tv"
        link = link0 + row.find('a').get('href') 
        photo = row.select_one(".relative.overflow-hidden").find('img').get('src') 
        rate = row.find(class_="pl-[5px] pr-[5px] overflow-hidden h-[30px]").find('p').text
        title = row.find(class_="pl-[5px] pr-[5px] overflow-hidden h-[30px]").find('figcaption').text
        episode = row.select_one("figure>p").text

        item=[]
        item.append(title)
        item.append(rate)
        item.append(episode)
        item.append(photo)
        item.append(link)
        drama.append(item)
#--------------------------------------drama------------------------------------
#--------------------------------------books------------------------------------  
    url = "https://www.books.com.tw/web/sys_tdrntb/books/"

    param = {"loc":"subject_004"}
    header = {
        "user-agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
    }
    data = requests.get(url,params=param,headers=header)
    data.encoding = "utf-8"
    data = data.text
    soup = BeautifulSoup(data,"html.parser")

    div = soup.find(class_="mod_no clearfix")
    lis = div.find_all('li',class_="item")
    books=[]
    n=0
    for li in lis:
        topnum = li.find('p',class_="no_list")
        rate = topnum.find('strong').text
        link = li.find('a').get('href')
        photo = li.find('img').get('src')
        context = li.find('div',class_="type02_bd-a")
        bookname = context.find('h4').text
        other = context.find('ul',class_="msg").text.strip().split('\n')
        try:
            author = other[0]
            price = other[1]
        except:
            price = other[0]
            author = "作者：None"
        item=[]
        item.append(bookname)
        item.append(rate)
        item.append(author)
        item.append(price)
        item.append(photo)
        item.append(link)
        books.append(item)
        n+=1
        if n>=7:
            break
#---------------------------------books-----------------------------------
#---------------------------------aqi-------------------------------------
    aqistid = ['46','29','43','55','28','64','63','67','17','39']
    x=datetime.now()
    z=timedelta(hours=1)
    y=x-z
    w=y.strftime("%Y%m%d%H")
    #print(w)

    url = "https://airtw.moenv.gov.tw/json/AQI/Taiwan_{}.json".format(w)

    header={
    "user-agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }

    resp = requests.get(url,headers=header)
    resp.encoding = "utf-8"
    print(resp.status_code)
    data = resp.json()

    maplist={}
    aqistch=[]
    rawaqinow=[]
    for row in data:
        stid = row['id']
        station,aqi = row['txt'].split()
        maplist[stid]=[station,aqi]

    for item in aqistid:
        aqistch.append(maplist[item][0])
        rawaqinow.append(maplist[item][1])
            
    pattern = "[0-9]+"
    aqinow=[]
    for i in rawaqinow:
        try:
            aqi = re.findall(pattern,i)[0].strip()
        except:
            aqinow.append(None)
        else:
            aqinow.append(aqi)
#---------------------------------aqi-------------------------------------     
    return render_template('index.html',**locals())

@app.route('/aqi',methods=['POST','GET'])
def aqi():

    ST1ID = request.args.get('station1')
    ST2ID = request.args.get('station2')

    mongodb()
    mapsample = db.aqi.find().sort({'datehour':-1}).limit(1)
    mapdata = mapsample[0]['stationList']  #字典裝在串列裡，就算只有一個元素也一樣
    maplist = {i['id']:[i['stationName'],i['county']] for i in mapdata}
    countyList = ['Keelung', 'Taipei', 'Newtaipei', 'Taoyuan', 'Hsinchu', 'Hsinchu_city', 'Miaoli', 'Taichung', 'Changhua', 'Nantou', 'Yunlin', 'Chiayi', 'Chiayi_city', 'Tainan', 'Kaohsiung', 'Pingtung', 'Yilan', 'Hualien', 'Taitung', 'Penghu', 'Kinmen', 'Lienchiang']
    categ=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
    for i in maplist:
    	n = countyList.index(maplist[i][1])
    	categ[n].append(i)

    categList = zip(*[countyList,categ])
    categList = dict(categList) #要用dict不要用list

    countyOrder =["基隆","台北","新北","桃園","新竹","新竹市","苗栗","台中","彰化","南投","雲林","嘉義","嘉義市","台南","高雄","屏東","宜蘭","花蓮","台東","澎湖","金門","連江"]

    countymap = zip(*[countyList,countyOrder])
    countymap = dict(countymap)

    if request.method == 'POST':
    	os.chdir('../datadrain')
    	os.system('python3 aqidrain.py')
    	succuss="更新成功"

    if ST1ID==None or ST2ID==None:
        da=""
        aqi1=[]
        aqi2=[]
        date=[]
        stname1=None
        stname2=None
        st1=[]
        st2=[]

    else:
        
        stname1 = maplist[ST1ID][0]
        stname2 = maplist[ST2ID][0]
        
        cursor = db.aqi.aggregate([
		  { '$sort': { 'datehour': -1 } },
		  { '$limit': 96 },
		  {
		    "$project": {
		      "datehour": 1,
		      "_id":0,
		      "twostations": {
		        "$filter": {
		          "input": "$stationList",   # 指定要篩選的陣列
		          "as": "station",        # 定義變數 "station"
		          "cond": { "$or": [
		              { "$eq": ["$$station.id", ST1ID] },
		              { "$eq": ["$$station.id", ST2ID] }
		            ]}  # 變數 $$station 代表陣列內的每個物件
		        }
		      }
		    }
		  }
		])

        date=[]
        st1=[]
        st2=[]
        for item in list(cursor):
            date0 = item['datehour'].astimezone(timezone(timedelta(hours=8))).strftime("%Y/%m/%d %H時")
            st10 = item['twostations'][0]['aqi']
            st20 = item['twostations'][1]['aqi']
            date.append(date0)
            st1.append(st10)
            st2.append(st20)

        date.reverse()
        st1.reverse()
        st2.reverse()

        pattern = "[0-9]+"
        aqi1=[]
        for i in st1: 
            try: 
                aqi = re.findall(pattern,i)[0].strip()
            except:
                aqi1.append(None)
            else:
                aqi1.append(aqi)


        aqi2=[]
        for i in st2:
            try:  
                aqi = re.findall(pattern,i)[0].strip()
            except:
                aqi2.append(None)
            else:
                aqi2.append(aqi)

        

    return render_template("aqi.html",**locals())

    

    
@app.route('/24temp')
def cwa():
    ST1ID = request.args.get('station1')
    ST2ID = request.args.get('station2')

    response = requests.get("https://www.cwa.gov.tw/Data/js/Observe/OSM/C/STMap.json")
    data = response.json()

    TEMPER=[]
    STATION=[]

    if ST1ID==None or ST2ID==None:
        da=""
        DATE=[]
    else:
        for sid in [ST1ID,ST2ID]:

            with urlopen("https://www.cwa.gov.tw/V8/C/W/Observe/MOD/24hr/{}.html".format(sid)) as resp:
                dataa = resp.read().decode("utf-8")

            soup = BeautifulSoup(dataa,'html.parser')
            trs = soup.select('tr')
            TEMP=[]
            DATE=[]
            for tr in trs:
                date = tr.find('th').text
                if tr.select_one(".tem-C.is-active") == None:
                    temp = None
                else:
                    temp = tr.select_one(".tem-C.is-active").text
                TEMP.append(temp)
                DATE.append(date)
            TEMP.reverse()
            DATE.reverse()
            TEMPER.append(TEMP)
            station = soup.find('tr').get('data-cstname')
            STATION.append(station)
    
    return render_template("cwa.html",**locals())

@app.route('/drama')
def drama():
    dbegin()
    page, count = total("drama")
    q = request.args.get('q')
    minp = request.args.get('minp')
    maxp = request.args.get('maxp')
    sortp = request.args.get('sortp')

    if page == None:
        page = 1
    
    startp = int(page) - 1
    
    if q == None:
        # 全部
        sql = "select * from drama where 1=2 limit {},28".format(startp*28)
    elif len(q) == 0 and len(minp) > 0 and len(maxp) > 0:        
        # 只查詢價格
        sql = "select * from drama where year between {} and {} order by year {} limit {},28".format(minp,maxp,sortp,startp*28)
    elif len(q) > 0 and len(minp) == 0 and len(maxp) == 0:
        # 只查書本
        sql = "select * from drama where title like '%{}%' or category like '%{}%' order by year {} limit {},28".format(q,q,sortp,startp*28)
        
    elif len(q) == 0 and len(minp) == 0 and len(maxp) == 0:
         sql = "select * from drama order by year {} limit {},28".format(sortp,startp*28)
        
    else:
        #查詢書本、價格
        sql = "select * from drama where title like '%{}%' or category like '%{}%' and year between {} and {} order by price {} limit {},28".format(q,q,minp,maxp,sortp,startp*28)

    cursor.execute(sql)
    data = cursor.fetchall()   
    
    pagination = Pagination(page=page,total=count,per_page=28)

    dbclose()

    return render_template('drama.html',**locals())

@app.route('/books')
def books():
    dbegin()
    page, count = total("books")
    q = request.args.get('q')
    minp = request.args.get('minp')
    maxp = request.args.get('maxp')
    sortp = request.args.get('sortp')

    if page == None:
        page = 1
    
    startp = int(page) - 1
    
    if q == None:
        # 全部
        sql = "select * from books where 1=2 limit {},28".format(startp*28)
    elif len(q) == 0 and len(minp) > 0 and len(maxp) > 0:        
        # 只查詢價格
        sql = "select * from books where price between {} and {} order by price {} limit {},28".format(minp,maxp,sortp,startp*28)
    elif len(q) > 0 and len(minp) == 0 and len(maxp) == 0:
        # 只查書本
        sql = "select * from books where bookname like '%{}%'  order by price {} limit {},28".format(q,sortp,startp*28)
        
    elif len(q) == 0 and len(minp) == 0 and len(maxp) == 0:
         sql = "select * from books order by price {} limit {},28".format(sortp,startp*28)
        
    else:
        #查詢書本、價格
        sql = "select * from books where bookname like '%{}%' and price between {} and {} order by price {} limit {},28".format(q,minp,maxp,sortp,startp*28)

    cursor.execute(sql)
    data = cursor.fetchall()   
    
    pagination = Pagination(page=page,total=count,per_page=28)

    dbclose()

    return render_template('books.html',**locals())

if __name__ == "__main__":
	#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')
    host = "0.0.0.0"
    port = 50

    # 顯示 URL 和 Port
    print(f"Serving on http://{host}:{port}")

    # 使用 logging 來記錄
    logging.info(f"Serving on http://{host}:{port}")

    # 啟動服務
    serve(app, host=host, port=port)