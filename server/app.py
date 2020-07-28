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
import numpy as np
import pandas as pd
import sklearn as
import tensorflow as tf

@app.before_first_request
def activate_things():
    
    

@app.route("/")
def index():
    return "<h1>This is a logistic tracking dashboard page!</h1>"



#search for a product
@app.route("/entryPoint", methods = ['POST'])
def searchProduct():

    resp = jsonify(results)
    resp.status_code = 200
    return resp

'''
if __name__ == '__main__':
    app.run(debug=True)
'''

    
    
    
    
    
    
    
    
