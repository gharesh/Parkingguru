import pymongo
import datetime
import json

# -*- coding: utf-8 -*-
class CheckParkingMLCP(object):
    type = "2 wheeleer" # class attribute

    def __init__(self, name): # special method
        self.name = name # instance attribute
        self.client = pymongo.MongoClient("mongodb://n30:infy%40123@democluster-shard-00-00-klhmq.mongodb.net:27017,democluster-shard-00-01-klhmq.mongodb.net:27017,democluster-shard-00-02-klhmq.mongodb.net:27017/test?ssl=true&replicaSet=DemoCluster-shard-0&authSource=admin&retryWrites=true")
        self.db = self.client.gh19 #gh19 is db name

    def __str__(self): # special method
        """This method is run when Python tries to cast the object to a string. Return
        this string when using print(), etc.
        """
        return self.name

    def rename(self, renamed): # regular method
        """Reassign and print the name attribute."""
        self.name = renamed
        print("Now my name is {}".format(self.name))

    def insertRecords(self,collectionName,val):
        #myCollection=self.db.log
        print(self.db.list_collection_names()) #Should print ['log']
        self.db[collectionName].insert_one(val)

    def getAllRecordsFromCollection(self,collectionName):
        print("getting All records from collection : ",collectionName)
        logs=self.db[collectionName].find()
        for record in logs:
            print(record)

    def addSampleRecordToLogCollection(self):
        logVal = {"app":"dummy5",
                  "value":"this a a saple log2",
                  "time":datetime.datetime.utcnow()
                  }
        self.insertLogRecord(logVal)

    def checkParkingStatus(self,floorNumber):
        #Use caching to get details

        slotsAvailable = CheckParkingMLCP.getParkingStatusOnFloor(self,floorNumber)
        if slotsAvailable < 1 :
            print("No parking on current floor")
            #Update displays on floor
        else:
             print ("Total Slots Available on floor #"+str(floorNumber)+" = "+str(slotsAvailable))


    def getParkingStatusOnFloor(self,floorNumber):
        #qry='floorNumber' +':'+ str(floorNumber)
        #print(qry)
        myquery = { "floorNumber": str(floorNumber) }
        print(myquery)
        resultDoc = self.db['MLCPParking'].find_one(myquery,{ "_id":0, "totalSlots":1, "slotsInUse":1 })
        for x in resultDoc:
            v_totalSlots=resultDoc['totalSlots']
            #print(resultDoc['slotsInUse'])
            v_inUse=resultDoc['slotsInUse']
            available=v_totalSlots-v_inUse
            #print(available)
        return available

    def addNewVehicleToFLoor(self,vehicleNumber,floorNumber):
        myquery = "{'floorNumber':" + str(floorNumber)+ "},{$inc: {'slotsInUse': 1 }}"
        self.db['MLCPParking'].find_one_and_update(myquery)
        #self.db['MLCPParking'].find_one_and_update({"floorNumber": str(floorNumber)},{"$inc": {"slotsInUse": 1 }})
        self.db['MLCPParking'].find_one_and_update({"floorNumber": str(floorNumber)}, { "$push": { "vehiclesOnFloor": str(vehicleNumber) }})

    def addNewVehicleToFLoor2(self,filterVal,updateVal):
        self.db['MLCPParking'].find_one_and_update(filterVal,updateVal)


logObj = CheckParkingMLCP("SampleClass")
#logObj.getAllRecordsFromCollection("log")

#logObj.checkParkingStatus(2)
#logObj.addNewVehicleToFLoor(222022,2)

floorNumber=1
filterVal = {"floorNumber": str(floorNumber)}
updateVal = {"$inc": {"slotsInUse": 1 }}
logObj.addNewVehicleToFLoor2(filterVal,updateVal)

