from flask import Flask,jsonify,make_response,Response,request, render_template,send_from_directory
import xml.etree.cElementTree as etree
import config
import os
from flask_cors import CORS
import fileinput
import subprocess
from subprocess import call
import requests 
import datetime
from base64 import b64encode    
from flask_jwt_extended import (
    JWTManager, jwt_required, get_jwt_identity,
    create_access_token, create_refresh_token,
    jwt_refresh_token_required, get_raw_jwt
)


app = Flask(__name__, static_folder="build", template_folder="build")
app.config['JWT_TOKEN_LOCATION'] = ['headers']
CORS(app)

# Enable blacklisting and specify what kind of tokens to check
# against the blacklist
app.config['JWT_SECRET_KEY'] = "Mobigesture"  # Change this!
#app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
jwt = JWTManager(app)
blacklist = set()



def xml_parser(files):
    xml=""
    with open(files,"r") as outfile:
       for line in outfile:
           xml=xml+line
    return xml


@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400
    expires = datetime.timedelta(minutes=5)
    ret = {
        'access_token': create_access_token(identity=username,expires_delta=expires),
        'refresh_token': create_refresh_token(identity=username)
    }
    return jsonify(ret), 200

'''
@app.route('/')
#@jwt_required
def home():
   #return send_from_directory(app.static_folder, 'index.html')
   return render_template('index.html')'''


@app.route('/getxml',methods=['GET',"POST"])
@jwt_required
def xml_data():
    if request.method=="GET":
        xmlDoc = open(config.vars_xml, 'r')
        xmlDocData = xmlDoc.read()
        xmlDocTree = etree.XML(xmlDocData)
        list_data = []
        c=0
        for i in xmlDocTree.iter('X-PRE-PROCESS'):
            d={}
            c=c+1
            try:
                text = i.get("data").split("=")
            except Exception as e:
                print("e:",e)
            d["name"]= text[0]
            d["value"] = text[1]
            d["key"] = c
            list_data.append(d)
        return jsonify(list_data)
    if request.method == "POST":    
        req = request.get_json()
        try:
            f = open(config.vars_xml,'r')
            filedata = f.read()
            f.close()
            for i in req:
                newdata = filedata.replace(i['value'],i['newValue'])
            f = open(config.vars_xml,'w')
            f.write(newdata)    
            f.close()   
            return jsonify(req),200
        except Exception as e:
            return jsonify({"message":"error is occurred"}),500

@app.route("/updatexml",methods=["POST"])
@jwt_required
def update_xml_content():
    req = request.get_json()
    try:
        f = open(config.vars_xml,'r')
        filedata = f.read()
        f.close()
        for i in req:
            newdata = filedata.replace(i['value'],i['newValue'])
        f = open(config.vars_xml,'w')
        f.write(newdata)    
        f.close()   
        reget = requests.get(config.get_xml)
        return jsonify(reget.content.decode('utf-8')),200
    except Exception as e:
        return jsonify({"message":"error is occurred"}),500

@app.route('/xmldataupdate',methods=['GET','POST'])
@jwt_required
def update_xml():
    if request.method == "GET":
        return jsonify({"xml":xml_parser(config.default_xml)}),200
    
  
@app.route('/cmd',methods=["GET","POST"])
@jwt_required
def commands_execute():     
    std = subprocess.check_output(["fs_cli"], shell=True)
    print(std)
    return jsonify({"hi":'name'}),200
        
@app.route('/xmlfiles',methods=['GET'])
@jwt_required
def render_xmls():
    list_files =[]
    files = os.listdir(config.xmls_path)
    for name in files:    
        if name.startswith("1"):
            d={}
            d["file_name"] = name.split(".")[0]
            d["file_content"] = xml_parser(config.xmls_path+"/"+name)
            list_files.append(d)
    return jsonify({"xml":list_files}),200


if __name__ == "__main__":
    app.run(host="0.0.0.0",use_reloader=True,threaded=True,port=5000,debug=True)
