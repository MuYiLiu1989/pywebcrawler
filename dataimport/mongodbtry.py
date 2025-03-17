import pymongo

try:
	client = pymongo.MongoClient("mongodbaqi:27017")
except:
	print("mongodb連接失敗")
else:
	print("mongodb連接成功")

db = client.crawlerdisplay