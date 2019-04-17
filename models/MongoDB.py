# -*- coding: utf-8 -*-
import pymongo
import base64
import os,time
import datetime
from pathlib import Path
from werkzeug.utils import secure_filename
#from bson.binary import Binary

BASE_DIR="D:\\SpyderDev\\FlaskAppGH19\\"
IMAGE_DIR="D:\\SpyderDev\\FlaskAppGH19\\static\\images\\"

class MongoDB(object):
    URI = "mongodb://n30:infy%40123@democluster-shard-00-00-klhmq.mongodb.net:27017,democluster-shard-00-01-klhmq.mongodb.net:27017,democluster-shard-00-02-klhmq.mongodb.net:27017/test?ssl=true&replicaSet=DemoCluster-shard-0&authSource=admin&retryWrites=true"
    DATABASE = None



    def __init__(self):
        self.client = pymongo.MongoClient(self.URI)
        self.DATABASE = self.client.gh19

    def findAll(self, collection):
        #return self.DATABASE[collection].find();
        docs=self.DATABASE[collection].find()
        print(docs)
        return docs

    def find_sort(self, collection):
        #return self.DATABASE[collection].find();
        logs=self.DATABASE[collection].find()
        output = []
        for record in logs:
            output.append(record)
        return str(output)

    def find_one(self, collection,myQuery):
        print("FIND_ONE  :  Running Query :: ",myQuery)
        resultSet = self.DATABASE[collection].find_one(myQuery)
        print("FIND_ONE  :  ResultSet : ",resultSet)
        return str(resultSet)


    def find_one_and_update(self, collection, filterVal, updateVal):
        print("FIND_ONE_AND_UPDATE : Query ", filterVal, updateVal)
        return str(self.DATABASE[collection].find_one_and_update(filterVal,updateVal))

    def saveImageToDB(self, collection, vehicelNumber, file):
        #imageAsBinary = Binary(file)
        #imageAsBase64 = base64.b64encode(file.read())
        #fh.write(str.decode('base64')) #to read back

        with open(file, "rb") as imageFile:
            imageAsBase64 = base64.b64encode(imageFile.read())

        #Form json
        carInfo={
            "vehicleNumber":vehicelNumber,
            "snapShot": imageAsBase64
        }
        self.DATABASE[collection].insert_one(carInfo)


    def saveCarToDB(self, collection, vehicelNumber, speed, fileName,cameraName):
        #print("basename :: ",os.path.basename(file.name))
        #print("basename :: ",os.path.basename(file))
        #fName, ext = os.path.splitext(file.name)
        #print("fName = ",fName)
        #millis = int(round(time.time() * 1000))
        #newFname = fName+'_'+str(millis)+str(ext)
        #print("newFname = ",newFname)
        #finalPathName = BASE_DIR+str("\\uploads\\")+str(newFname)
        pathForMongo="\\static\\images\\"+fileName
        print("PathForMongo:: ",fileName)
        #file.save(os.path.join("uploads/",newFname))
        #file.save(newFname)
        #srcFile=file.name
        #file.close()
        #os.rename(srcFile,newFname)
        #print("Car snapshot saved in server path")
        #Form json
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        print("time",st)
        try:
            if speed!="waiting..." or speed > -1 :
                nSpeed=speed
        except Exception as e:
            print("Invalid speed",str(e))
            nSpeed=0
            
        carInfo={
            "vehicleNumber":vehicelNumber,
            "speed": nSpeed,
            "filePath": pathForMongo,
            "cameraName":cameraName,
            "timestamp": st
        }
        self.DATABASE[collection].insert_one(carInfo)
        print("Car details logged in DB")
       
            

    def dummy(self):
        #print("basename :: ",os.path.basename(("..//",file)))
        p = Path('__file__').parents[1]
        print(p)

    def getViolators(self, collection,speed):
        myquery = { "speed": { "$gt": 25 } }
        docs=self.DATABASE[collection].find(myquery)
        print(docs)
        return docs

    def getfloorLogs(self, collection,floorNumber):
        myquery = { "floorNumber": floorNumber}
        docs=self.DATABASE[collection].find(myquery)
        print(docs)
        return docs


    def addCarToFloor(self, vehicelNumber,fileName,cameraName,floorNumber,entryMode):
        pathForMongo="\\static\\images\\"+fileName
        print("PathForMongo:: ",fileName)
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        print("time",st)
        carInfo={
            "vehicleNumber":vehicelNumber,
            "floorNumber": floorNumber,
            "filePath": pathForMongo,
            "cameraName":cameraName,
            "entryMode":entryMode,
            "timestamp": st
        }
        self.DATABASE['MLCPFloorTraffic'].insert_one(carInfo)
        filterVal = {"floorNumber": str(floorNumber)}
        if entryMode == 1:
            updateVal = {"$inc": {"slotsInUse": 1 }}
        else:
            updateVal = {"$inc": {"slotsInUse": -1 }}
        return str(self.DATABASE["MLCPParking"].find_one_and_update(filterVal,updateVal))
        print("Car details logged in Floor Traffic DB")



#logObj = MongoDB()
#logObj.initialize(logObj)
#logObj.find_sort(logObj,"MLCPParking")