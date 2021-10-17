import flask
from pymongo import MongoClient
import urllib
import json
from bson import json_util, ObjectId
from datetime import datetime, timedelta

app = flask.Flask(__name__)

username = urllib.parse.quote_plus('test-user')
password = urllib.parse.quote_plus('ForIvanAndRussians')
client = MongoClient("mongodb+srv://%s:%s@initial-mined-data.w3ygy.mongodb.net" % (username, password))
db = client.Datathon

@app.route("/collect_data")
def home():
    list = db.list_collection_names()
    for coll in list:
        collection = db[coll]
        with open("./tmp/" + coll + ".json", "w") as outfile:
            for doc in collection.find():
                outfile.write(str(json.loads(json_util.dumps(doc))))
                outfile.write("\n")
    return "OK"

def get_current_term():
    curr_date =


if __name__ == "__main__":
    app.run()
