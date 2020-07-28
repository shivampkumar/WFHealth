from flask import Flask
from flask import jsonify
from flask import request
import pymongo
from bson.json_util import dumps
app = Flask(__name__)
import bson
import json
from flask import Response
from datetime import datetime
from flask import render_template
from passlib.hash import pbkdf2_sha256

mongo  = None
db = None
rider = None 
consignments = None 
manifest = None
products = None
users = None

@app.before_first_request
def activate_things():
    
    

@app.route("/")
def index():
    return "<h1>This is a logistic tracking dashboard page!</h1>"

#get version of the app for checking for updates

    
#add a new consignment
@app.route("/addConsignments", methods = ['POST'])
def addConsignments():
    global db
    global consignments
    global users
    requestJson = json.loads(dumps(request.json))
    
    #{"items":[{"id":"6","name":"Rhydon","quantity":{"$numberInt":"4"},"percost":{"$numberDouble":"50"}}],"currentLocation":"","lastMile":false,"latitude":"","longitude":"","address":{"name":"Saurav","contact":{"$numberLong":"83245"},"addressLine1":"","addressLine2":"","city":"Wuhan","pincode":{"$numberInt":"459322"}},"cost":{"$numberDouble":"200"},"isDelivered":false}
    result_Id = consignments.insert_one(requestJson['consignment']).inserted_id
    
    users.update({'username':requestJson['username']}, {'$push' : {'orders':{'consignmentId' : (str)(result_Id), 'isActive': True}} } )

    return (str)(result_Id)

@app.route("/emptyCart", methods = ['PUT'])
def emptyCart():
    global db
    global users
    users.update({'username':request.form['username']}, {'$set' : {'cart': [] }} )
    return "emptied cart"
    

#add a new rider
@app.route("/addRider", methods = ['POST'])
def addRider():
    global db
    global rider
    #{"items":[{"id":"6","name":"Rhydon","quantity":{"$numberInt":"4"},"percost":{"$numberDouble":"50"}}],"currentLocation":"","lastMile":false,"latitude":"","longitude":"","address":{"name":"Saurav","contact":{"$numberLong":"83245"},"addressLine1":"","addressLine2":"","city":"Wuhan","pincode":{"$numberInt":"459322"}},"cost":{"$numberDouble":"200"},"isDelivered":false}
    
    result_Id = rider.insert_one(json.loads(dumps(request.json))).inserted_id
    return (str)(result_Id)

#add a new product
@app.route("/addProduct", methods = ['POST'])
def addProduct():
    global db
    global products
    #{"_id":{"$oid":"5e784d1e1c9d440000cddcf1"},"Name":"Pencil Box","Description":"","Price":{"$numberInt":"25"},"DiscountPrice":"23","In Stock":true,"minCount":"10","Images":["https://rukminim1.flixcart.com/image/832/832/jjrgosw0/pencil-box/j/8/u/calculator-design-dual-side-open-pencil-box-technochitra-original-imaf797zzgt2agct.jpeg","https://5.imimg.com/data5/UR/SM/MY-23291425/1-500x500.jpg"],"Category":"Stationary"}
    
    ##########Add logic for category detection#############
    
    result_Id = products.insert_one(json.loads(dumps(request.json))).inserted_id
    return (str)(result_Id)


#search for a product
@app.route("/searchProduct", methods = ['GET'])
def searchProduct():
    global db
    global products
    keyword = request.args.get('keyword')
    results = products.find({'Description':{'$regex': '.*' + keyword + '.*', '$options':'i'}}).limit(6)
    results = json.loads(dumps(results))
    resp = jsonify(results)
    resp.status_code = 200
    return resp

#list of featured products
@app.route("/featuredProducts", methods = ['GET'])
def featuredProducts():
    global db
    global products
    results = products.find({}).sort('Modified', -1).limit(16)
    #print(results)
    results = json.loads(dumps(results))
    #print(results)
    resp = jsonify(results)
    resp.status_code = 200
    return resp

#assign a consignment to a rider
@app.route("/assignorder", methods = ['PUT'])
def assignOrder():
    global db
    global rider
    global consginments
    consignmentJson = json.loads(dumps(consignments.find_one({"_id": bson.ObjectId(request.form['_id'])})))
    cost = (float)(consignmentJson['cost'])
    isDelivered = (bool)(consignmentJson['isDelivered'])
    
    rider.update_one({"userId": request.form['userId']},
                      {"$push": {"Consignments": {"Id":request.form["_id"],
                                                  "Cost":cost,
                                                  "isDelivered":isDelivered}}}
    )
    result = rider.find({"userId": request.form['userId']})
    result = json.loads(dumps(result))
    resp = jsonify(result)
    resp.status_code = 200
    return resp
    
#update the location of the delivery
@app.route("/deliveryUpdate", methods = ['PUT'])
def deliveryUpdate():
    global db
    global rider
    global consignments
    myquery = {"userId": request.form['userId']}
    newvalues = {"$set": {
                       "latitude": request.form['latitude'],
                       "longitude": request.form['longitude']}} 
    rider.update_one(myquery, newvalues)
    
    riderJson = json.loads(dumps(rider.find_one({"userId": request.form['userId']})))

    for item in riderJson['Consignments']:
        myquery = {"_id": bson.ObjectId(item['Id'])}
        newvalues = {"$set": {
                       "latitude": request.form['latitude'],
                       "longitude": request.form['longitude']}}
        consignments.update_one(myquery, newvalues)
        print("Updated " + item['Id'] )
    
    resp = jsonify(riderJson)
    resp.status_code = 200
    return resp

#update the product details
@app.route("/productUpdate", methods = ['PUT'])
def productUpdate():
    global db
    global products
    myquery = {"_id": bson.ObjectId(request.args.get('_id'))}
    newvalues = {"$set": json.loads(dumps(request.json))}
    products.update_one(myquery, newvalues)
    result = json.loads(dumps(products.find_one(myquery)))
    return result
    

#update the status of delivery
@app.route("/orderUpdate", methods = ['PUT'])
def orderUpdate():
    global db
    global rider
    global consignments
    myquery = {"_id": bson.ObjectId(request.form['_id'])}
    newvalues = {"$set": {
                       "isDelivered": (bool)(request.form['isDelivered']),
                       "isClosed": (bool)(request.form['isClosed']),
                       "message":request.form['message']
                       }} 
    consignments.update_one(myquery, newvalues)
    
    if((bool)(request.form['isDelivered'])):
        #print('Changing delivery details')
        riderJson = json.loads(dumps(rider.find_one({"userId": request.form['userId']})))
        cost = (float)(riderJson['TotalCollected'])
        print('Initial driver value'+ (str)(cost))
        index = 0
        #optimize this way of getting cost
        flag = 0
        for item in riderJson['Consignments']:
            if(item['Id']== request.form['_id']):
                if((bool)(item['isDelivered']) == True ): #item is already delivered
                    flag = 1
                    break
                cost += (int)(item['Cost'])
                break
            index+=1
        #print("index" + (str)(index))
        if(not(flag ==1)): 
            myquery = {"userId": request.form['userId']}
            newvalues = {"$set": {
                       "Consignments."+(str)(index)+ ".isDelivered": (bool)(request.form['isDelivered']),
                       "TotalCollected": cost
                       }} 
            rider.update_one(myquery, newvalues)
    
    
    result = consignments.find({"_id": bson.ObjectId(request.form['_id'])});
    result = json.loads(dumps(result))
    resp = jsonify(result)
    resp.status_code = 200
    return resp


@app.route("/cancelOrder", methods = ['DELETE'])
def cancelOrder():
    global db
    global rider
    global consignments
    global users
    
    #update consignment
    
    myquery = {"_id": bson.ObjectId(request.form['_id'])}
    newvalues = {"$set": {
                       "isDelivered": False,
                       "isClosed": True,
                       "message": "Order cancelled by user"
                       }} 
    consignments.update_one(myquery, newvalues)
    consignments.update({'_id': bson.ObjectId(request.form['_id']) }, {'$push' : {'trackingHistory':{'status' : "Order Cancelled by user", 'time': (int)(datetime.utcnow().timestamp()*100000) }} } )
    
    #update user
    
    users.update({'username':request.form['username']}, {'$pull' : {'orders':{'consignmentId' : request.form['_id']}} } )
    users.update({'username':request.form['username']}, {'$push' : {'orders':{'consignmentId' : request.form['_id'], 'isActive':False}} } )    
    #update rider
    
    consignmentJson = json.loads(dumps(consignments.find_one({"_id": bson.ObjectId(request.form['_id'])})))
    if not(consignmentJson["rider"]  == ""):
        #print('Changing delivery details')
        riderJson = json.loads(dumps(rider.find_one({"userId": consignmentJson['rider']})))
        index = 0
        #optimize this way of getting cost
        for item in riderJson['Consignments']:
            if(item['Id']== request.form['_id']):
                myquery = {"userId": request.form['userId']}
                newvalues = {"$set": {
                       "Consignments."+(str)(index)+ ".isDelivered":False,
                       "Consignments."+(str)(index)+ ".isClosed":True
                       }} 
                rider.update_one(myquery, newvalues)
                break
            index+=1
        #print("index" + (str)(index))
        
    
    
    result = consignments.find({"_id": bson.ObjectId(request.form['_id'])});
    result = json.loads(dumps(result))
    resp = jsonify(result)
    resp.status_code = 200
    return resp

#close connection
@app.route("/connectionClose", methods = ['GET'])
def connectionClose():
    global mongo
    mongo.close()
    return "Connection Closed"

'''
if __name__ == '__main__':
    app.run(debug=True)
'''

    
    
    
    
    
    
    
    
