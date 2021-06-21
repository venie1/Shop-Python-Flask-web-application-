from flask.json import JSONEncoder
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from flask import Flask, request, jsonify, redirect, Response
import json
import uuid
import time
from bson import ObjectId,json_util, objectid
class JSONEncoder(json.JSONEncoder):
        def default(self,o):
            if isinstance(o,ObjectId):
                return str(o)
            return json.JSONEncoder.default(self, o)

# Connect to our local MongoDB
client = MongoClient('mongodb://localhost:27017/')

# Choose database
db = client['DSMarkets']
# Choose collections
Users = db['Users']
Products = db['Products']
cart= db['cart']
app2 = Flask(__name__)
users_sessions = {}
def create_session(username):
    user_uuid = str(uuid.uuid1())
    users_sessions[user_uuid] = (username, time.time())
    return user_uuid  

def is_session_valid(user_uuid):
    return user_uuid in users_sessions

@app2.route('/createUser', methods=['POST'])
def create_user():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data or not  "name" in data or not "password" in data:
        return Response("Information incomplete",status=500,mimetype='application/json')
    
    
     
    if Users.count_documents({'email':data['email']})>0:
         return Response("A user with the given email already exists", mimetype='application/json',status=400) 
    else:
        data["category"]="user"
        data["cart"]={}
        Users.insert_one(data)
        return Response(data['name']+" was added to the Users", mimetype='application/json',status=200) 
@app2.route('/login', methods=['POST'])
def login():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data or not "password" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")
    if Users.count_documents( { '$and': [{'email':data['email']}, {'password':data['password']}]})>0:
        user_uuid=create_session(data['email'])
        res = {"uuid": user_uuid, "email": data['email']}
        return Response(json.dumps(res), mimetype='application/json',status=200) # ΠΡΟΣΘΗΚΗ STATUS
    else:
        return Response("Wrong username or password.",mimetype='application/json',status=400) # ΠΡΟΣΘΗΚΗ STATUS


@app2.route('/createProduct', methods=['POST'])
def create_product():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data or not "category" in data or not  "name" in data or not "stock" in data or not "des" in data or not "price" in data:
        return Response("Information incomplete",status=500,mimetype='application/json')
    uuid = request.headers.get('Authorization')
    if  is_session_valid(uuid):
      u=Users.find_one({"email":data['email']})
      if u['category']=="Admin":
        Products.insert_one(data)
        Products.update_many({},{"$unset": {"email":""}})
        return Response(JSONEncoder().encode(data), mimetype='application/json',status=200)       
      else:
                          return Response("Needs to be admin to do this operation", mimetype='application/json',status=400)       

    else:
                return Response("NOT AUTHENTICATED", mimetype='application/json',status=400)       

@app2.route('/deleteProduct', methods=['DELETE'])
def delete_Product():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",s5tatus=00,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "_id" in data or not "email" in data :
        return Response("Information incomplete",status=500,mimetype='application/json')
    
    uuid = request.headers.get('Authorization')
    if  is_session_valid(uuid):
      u=Users.find_one({"email":data['email']})
      if u['category']=="Admin":
        if Products.count_documents({'_id':ObjectId(data['_id'])})==0:
         return Response("Product dosn't exist", mimetype='application/json',status=400) 
        else:
            Products.delete_one({'_id':ObjectId(data['_id'])})
            return Response("Product was deleted", mimetype='application/json',status=200) 
      else:
                                    return Response("Needs to be admin to do this operation", mimetype='application/json',status=400)       

    else:
                return Response("NOT AUTHENTICATED", mimetype='application/json',status=400)       

@app2.route('/updateProduct', methods=['PATCH'])
def update_Product():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "_id" in data or not("name" in data or "price" in data or "des" in data ) :
        return Response("Information incomplete",status=500,mimetype='application/json')
    
    
    uuid = request.headers.get('Authorization')
    if  is_session_valid(uuid):
     u=Users.find_one({"email":data['email']})
     if u['category']=="Admin":
        if Products.count_documents({'_id':ObjectId(data['_id'])})==0:
         return Response("Product dosn't exist", mimetype='application/json',status=400) 
        else:
            if "name" in data:
                Products.update_one({'_id':ObjectId(data['_id'])},{"$set": {"name":data['name']}})
            if "price" in data:
                Products.update_one({'_id':ObjectId(data['_id'])},{"$set": {"price":data['price']}})
            if "des" in data:
                Products.update_one({'_id':ObjectId(data['_id'])},{"$set": {"dec":data['des']}})

            return Response("Product was deleted", mimetype='application/json',status=200) 
     else:
                                             return Response("Needs to be admin to do this operation", mimetype='application/json',status=400)       

    else:
                return Response("NOT AUTHENTICATED", mimetype='application/json',status=400)       

@app2.route('/getProducts', methods=['GET'])
def get_Products():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if "name" in data:
      uuid = request.headers.get('Authorization')
      if  is_session_valid(uuid):
        if Products.count_documents({'name':data['name']})>0:
            pr=list(Products.find({'name':data['name']}))
            spr=sorted(pr,key=lambda k: k['category'])
      
            return Response(JSONEncoder().encode(spr), status=200, mimetype='application/json')
        else:             
            return Response("Products were not found " ,status=400, mimetype='application/json')
      else:
                return Response("NOT AUTHENTICATED", mimetype='application/json',status=400)       

          
    elif "category" in data: 
      uuid = request.headers.get('Authorization')
      if  is_session_valid(uuid):
        if Products.count_documents({'category':data['category']})>0:
            pr=list(Products.find({'category':data['category']}))
            spr=sorted(pr,key=lambda k: k['price'])
            return Response(JSONEncoder().encode(pr), status=200, mimetype='application/json')
        else:             
            return Response("Products were not found " ,status=400, mimetype='application/json')
      else:
                return Response("NOT AUTHENTICATED", mimetype='application/json',status=400)       

    elif "_id" in data:
      uuid = request.headers.get('Authorization')
      if  is_session_valid(uuid):
        if Products.count_documents({'_id':ObjectId(data['_id'])})>0:
            pr=list(Products.find({'_id':ObjectId(data['_id'])}))
      
            return Response(JSONEncoder().encode(pr), status=200, mimetype='application/json')
        else:             
            return Response("Products were not found " ,status=400, mimetype='application/json')       
      else:
                return Response("NOT AUTHENTICATED", mimetype='application/json',status=400)       

    else: 
            return Response("Information incomplete",status=500,mimetype='application/json')
@app2.route('/addToCart', methods=['POST'])
def addToCart():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "id" in data or not  "count" in data  or not "email" in data:
        return Response("Information incomplete",status=500,mimetype='application/json')
    
    
    uuid = request.headers.get('Authorization')
    if  is_session_valid(uuid):
        if Products.count_documents({'$and': [{'_id':ObjectId(data['id'])},{'stock':{ '$gte':data['count']}}]})!=0:
            pr=Products.find_one({'$and': [{'_id':ObjectId(data['id'])},{'stock':{ '$gte':data['count']}}]})
            pr['email']=data['email']
            pr['count']=data['count']
            pr['pid']=data['id']
            pr['_id']=ObjectId()
            cart.insert_one(pr)
            c=list(cart.find({'$and': [{'pid':data['id']},{'email':data['email']}]}))
            return Response(JSONEncoder().encode(c), status=200, mimetype='application/json')
        else:             
            return Response("Products were not found or we haven't that amount in stock" ,status=400, mimetype='application/json')     
    else:
                return Response("NOT AUTHENTICATED", mimetype='application/json',status=400)       

@app2.route('/deleteCart', methods=['DELETE'])
def delete_Cart():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "id" in data or not "email" in data:
        return Response("Information incomplete",status=500,mimetype='application/json')
    
    uuid = request.headers.get('Authorization')
    if  is_session_valid(uuid):
     
     if cart.count_documents({'$and': [{'pid':data['id']},{'email':data['email']}]})==0:

         return Response("Product isn't on the cart", mimetype='application/json',status=400) 
     else:
        cart.delete_many({'$and': [{'pid':data['id']},{'email':data['email']}]})
        return Response("Product was deleted from the cart", mimetype='application/json',status=200) 
    else:
                return Response("NOT AUTHENTICATED", mimetype='application/json',status=400)       

@app2.route('/showCart', methods=['GET'])
def show_cart():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not  "email" in data:
        return Response("Information incomplete",status=500,mimetype='application/json')
    uuid = request.headers.get('Authorization')
    if  is_session_valid(uuid):
        if cart.count_documents({'email':data['email']})!=0:
            pri =0
            jasons=[] 
            for i in cart.find({'email':data['email']}):
                jason=json.dumps(i,default=json_util.default)
                pri+=i['price']*i['count']
                jasons.append(jason)
            pric=("the total price is", pri)
            pric=json.dumps(pric)
            jasons.append(pric)

            return Response(jasons , status=200, mimetype='application/json')
        else:
            return Response("user has no items in cart" ,status=400, mimetype='application/json')
    else:
                return Response("NOT AUTHENTICATED", mimetype='application/json',status=400)       

@app2.route('/Buy', methods=['DELETE'])
def Buy():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not  "email" in data or not "code" in data:
        return Response("Information incomplete",status=500,mimetype='application/json')
    uuid = request.headers.get('Authorization')
    if  is_session_valid(uuid):
      if len(data['code'])==16:
        if cart.count_documents({'email':data['email']})!=0:
            pri =0
            for i in cart.find({'email':data['email']}):
                pri+=i['price']*i['count']
                Products.update_one({'_id':ObjectId(i['pid'])},{"$inc": {"stock":-i['count']}})
            pric=("Order completed! the total price is:", pri)
            pric=json.dumps(pric)
            cart.delete_many({'email':data['email']})
            return Response(pric, status=200, mimetype='application/json')
        else:
            return Response("the user has no items in cart" ,status=400, mimetype='application/json')
      else:
        return Response(" please put a 16 digits code " ,status=400, mimetype='application/json')
    else:
                return Response("NOT AUTHENTICATED", mimetype='application/json',status=400)       

@app2.route('/deleteUser', methods=['DELETE'])
def deleteUser():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not  "email" in data:
        return Response("Information incomplete",status=500,mimetype='application/json')
    uuid = request.headers.get('Authorization')
    if  is_session_valid(uuid):
     if Users.count_documents({'email':data['email']})!=0:
            
            cart.delete_many({'email':data['email']})
            Users.delete_one({'email':data['email']})
            return Response("user was deleted", status=200, mimetype='application/json')
     else:
            return Response("the user Dosn't exist" ,status=400, mimetype='application/json')
    else:
                return Response("NOT AUTHENTICATED", mimetype='application/json',status=400)       

@app2.route('/createAdmin', methods=['POST'])
def create_admin():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data or not  "name" in data or not "password" in data:
        return Response("Information incomplete",status=500,mimetype='application/json')
    
    
     
    if Users.count_documents({'email':data['email']})>0:
         return Response("A user with the given email already exists", mimetype='application/json',status=400) 
    else:
        data["category"]="Admin"
        data["cart"]={}
        Users.insert_one(data)
        return Response(data['name']+" was added to the Users", mimetype='application/json',status=200) 
if __name__ == '__main__':
    app2.run(debug=True, host='0.0.0.0', port=5000)