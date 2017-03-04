import json, pymongo
from datetime import datetime
from titlecase import titlecase

EMPTY_DATUM = "None"


# read data from file
data_json = json.load(open('input/building-permits.json'))


def validate(date, pattern):
    try:
        return datetime.strptime(date, pattern)
    except ValueError:
        return


def title_case(line):
    return titlecase(line)


# put in mongoDB
mongo_client = pymongo.MongoClient()
mongo_collection = mongo_client.building.permit
mongo_collection.drop()  # throw out what's there


for data in data_json:
    wData = {}
    wData["date"] = datetime.strptime(data["date_issued"], '%Y-%m-%dT%H:%M:%S')
    wData["description"] = data["permit_subtype_description"]
    wData["zip"] = data["zip"]

    if "purpose" in data.keys():
        wData["purpose"] = data["purpose"]
    else:
        wData["purpose"] = ""

    wData["contact"] = data["contact"]

    if "state" in data.keys():
        wData["state"] = data["state"]
    else:
        wData["state"] = ""

    if "city" in data.keys():
        wData["city"] = data["city"]
    else:
        wData["city"] = ""

    if "address" in data.keys():
        wData["address"] = data["address"]
    else:
        wData["address"] = ""

    if "latitude" in data["mapped_location"].keys():
        wData["latitude"] = float(data["mapped_location"]["latitude"])
        wData["longitude"] = float(data["mapped_location"]["longitude"])

    for key in wData.keys():
        if wData[key] == "" or wData[key] is None:
            wData[key] = "None"
        elif isinstance(wData[key], unicode) and key != "purpose":
            wData[key] = title_case(wData[key])

    mongo_collection.insert_one(wData)


# create index by specific columns
mongo_collection.create_index('date')
mongo_collection.create_index('description')
mongo_collection.create_index('state')


# close connection
mongo_client.close()