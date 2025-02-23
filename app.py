from flask import Flask,render_template,request
from flask_paginate import Pagination,get_page_parameter
from urllib.request import Request,urlopen
from bs4 import BeautifulSoup
from datetime import datetime,timedelta
import mysql.connector
import requests
import json
import ssl
import re
from waitress import serve
import logging

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
    #print(data.status_code)
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
        
    return render_template('index.html',**locals())

@app.route('/aqi')
def aqi():

    ST1ID = request.args.get('station1')
    ST2ID = request.args.get('station2')

    maplist = {
    "1": "二林",
    "2": "三重",
    "3": "三義",
    "4": "土城",
    "5": "士林",
    "6": "大同",
    "7": "大里",
    "8": "大園",
    "9": "大寮",
    "10": "小港",
    "11": "中山",
    "12": "中壢",
    "13": "仁武",
    "14": "斗六",
    "15": "冬山",
    "16": "古亭",
    "17": "左營",
    "18": "平鎮",
    "19": "永和",
    "20": "安南",
    "21": "朴子",
    "22": "汐止",
    "23": "竹山",
    "24": "竹東",
    "25": "西屯",
    "26": "沙鹿",
    "27": "宜蘭",
    "28": "忠明",
    "29": "松山",
    "30": "板橋",
    "31": "林口",
    "32": "林園",
    "33": "花蓮",
    "34": "金門",
    "35": "前金",
    "36": "前鎮",
    "37": "南投",
    "38": "屏東",
    "39": "恆春",
    "40": "美濃",
    "41": "苗栗",
    "42": "埔里",
    "43": "桃園",
    "44": "馬公",
    "45": "馬祖",
    "46": "基隆",
    "47": "崙背",
    "48": "淡水",
    "49": "麥寮",
    "50": "善化",
    "51": "復興",
    "52": "湖口",
    "53": "菜寮",
    "54": "陽明",
    "55": "新竹",
    "56": "新店",
    "57": "新莊",
    "58": "新港",
    "59": "新營",
    "60": "楠梓",
    "61": "萬里",
    "62": "萬華",
    "63": "嘉義",
    "64": "彰化",
    "65": "臺西",
    "66": "臺東",
    "67": "臺南",
    "68": "鳳山",
    "69": "潮州",
    "70": "線西",
    "71": "橋頭",
    "72": "頭份",
    "73": "龍潭",
    "74": "豐原",
    "75": "關山",
    "76": "觀音",
    "84": "彰化（員林）",
    "85": "高雄（湖內）",
    "86": "臺南（麻豆）",
    "87": "屏東（琉球）",
    "91": "新北(樹林)",
    "92": "花蓮（美崙）",
    "93": "屏東(枋山)",
    "96": "富貴角",
    "136": "大城"
    }

    if ST1ID==None or ST2ID==None:
        da="請選擇測站"
        aqi1=[]
        aqi2=[]
        date=[]
        stname1=None
        stname2=None

    else:
        dbegin()
        
        stname1 = maplist[ST1ID]
        stname2 = maplist[ST2ID]
        """
        today=datetime.now()
        delta=timedelta(hours=1)
        n=today-delta
        hour = 72
        n=n-timedelta(hours=hour)

        header={
            "user-agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        }

        for i in range(hour):

            w=n.strftime("%Y%m%d%H")
            vv=n.strftime("%Y/%m/%d %H時")

            url = "https://airtw.moenv.gov.tw/json/AQI/Taiwan_{}.json".format(w)

            resp = requests.get(url,headers=header)
            resp.encoding = "utf-8"
            data = resp.json()

            aqi=[]
            for row in data:    
                txt = row['txt'].split()[1]
                aqi.append("'"+txt+"'")

            sql = "show columns from aqi"
            cursor.execute(sql)
            coldata = cursor.fetchall()

            sqlhead="insert into aqi("

            col=[]
            a=0
            for row in coldata:
                if a!=0:
                    col.append(row[0])
                a+=1

            sqlcol=','.join(col)

            sqlbody=") values('{}',".format(vv)

            sqlvalue=",".join(aqi)

            sqlend=")"

            sql = "select * from aqi where datehour='{}'".format(vv)
            cursor.execute(sql)
            if cursor.rowcount==0:
                sql = sqlhead + sqlcol + sqlbody + sqlvalue + sqlend
                cursor.execute(sql)
                conn.commit()

            n+=delta
        """
        sql = "select datehour,st{},st{} from aqi order by id desc limit 96".format(ST1ID,ST2ID)
        cursor.execute(sql)
        dataa=cursor.fetchall()

        finaldata = zip(*dataa)
        finaldata = list(finaldata)
        date = list(finaldata[0])
        st1 = list(finaldata[1])
        st2 = list(finaldata[2])

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

        dbclose()

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
        da="請選擇測站"
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
	logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')
	serve(app,host="0.0.0.0",port=50)