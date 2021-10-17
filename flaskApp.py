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
#ef home(wanted_student_id):
    student_cache = dict()

    wanted_student_id = "1"

    list = db.list_collection_names()
    print(list)
    for coll in list:
        collection = db[coll]
        with open("./tmp/" + coll + ".json", "w") as outfile:
            for doc in collection.find():
                json_line = json.loads(json_util.dumps(doc))
                if json_line.get("student_id")==wanted_student_id:
                    if student_cache.get(coll) is None:
                        student_cache[coll] = []
                    if coll == "StudentCourse":
                        course_id = json_line.get("course_id")
                        student_cache = get_class(student_cache, course_id, db)
                    student_cache[coll].append(json_line)
                outfile.write(str(json_line))
                outfile.write("\n")
    return str(student_cache)

def get_class(student_cache, course_id, db):
    if student_cache.get("Course") is None:
        student_cache["Course"] = []
    student_cache["Course"].append(db["Course"].find_one({"course_id": course_id}))
    return student_cache

if __name__ == "__main__":
    app.run()
