import pymongo
import os
import time
import job.goole_search_job as goole_search

mongo_user = os.environ.get('Mongo_User', '')
mongo_pwd = os.environ.get('Mongo_Pwd', '')
client = pymongo.MongoClient(
    "mongodb://" + mongo_user + ":" + mongo_pwd + "@cluster0-shard-00-00-sefrw.gcp.mongodb.net:27017,cluster0-shard-00-01-sefrw.gcp.mongodb.net:27017,cluster0-shard-00-02-sefrw.gcp.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority"
    , connect=False)


def start(_callbackLineMsg):
    db = client.kentDB
    coll = db['jobs']
    # 找状态为0的job
    myquery = {"status": {"$eq": "0"}}
    for dict in coll.find(myquery):
        goole_search.execute(coll, dict, _callbackLineMsg)
        print(dict)
        # 休息0.5秒
        time.sleep(0.5)
