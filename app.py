import sys
import os
import shutil
import time
import traceback
import json
from datetime import datetime

## database and server
import pymongo
from flask import Flask
from flask import request, render_template, send_from_directory, jsonify

## global variables
CUSTOM_STATIC_DIRECTORY = "/public/"
STATIC_FOLDER = "public"
EMPTY_DATUM = "None"

## setup mongodb access
client = pymongo.MongoClient()
crime_db = client.building.permit

## serve index.html
app = Flask(__name__, static_folder=STATIC_FOLDER, static_path=CUSTOM_STATIC_DIRECTORY)


@app.route("/")
def index():
    return app.send_static_file('index.html')


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('public/js/', path)


@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('public/css/', path)


@app.route('/images/<path:path>')
def send_images(path):
    return send_from_directory('public/images/', path)


## wrap return data in a json structure
def wrapData(query, data):
    msgObject = {}
    msgObject["query"] = query
    msgObject["content"] = data
    return json.dumps(msgObject)


## adjust the datetime variables from ISO strings to python compatible variable
def fix(query):
    if "$and" not in query.keys():
        return query

    for obj in query["$and"]:
        if "date" in obj.keys():
            for date_range in obj["date"]["$in"]:
                date_range = datetime.strptime(date_range, '%Y-%m-%dT%H:%M:%S.%fZ')

        if "$or" in obj.keys():
            for obj2 in obj["$or"]:
                if "date" in obj2.keys():
                    obj2["date"]["$gte"] = datetime.strptime(obj2["date"]["$gte"], '%Y-%m-%dT%H:%M:%S.%fZ')
                    obj2["date"]["$lte"] = datetime.strptime(obj2["date"]["$lte"], '%Y-%m-%dT%H:%M:%S.%fZ')

    return query


## read query from client and return data
@app.route("/data", methods=['POST'])
def get_data():
    raw_query = request.get_json()
    query = fix(raw_query)

    try:
        cursor = crime_db.find(query, {"_id": False})

        documents = []

        for document in cursor:
            document["date"] = document["date"].strftime("%c")
            documents.append(document)

        return wrapData({}, documents)

    except Exception, e:
        print "Error: Retrieving Data from MongoDB"
        return jsonify({'error': str(e), 'trace': traceback.format_exc()})


## run the server app
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000, debug=True)
