from flask import Flask, request, render_template
from pymongo import MongoClient
import urllib
import json
from bson import json_util, ObjectId
from datetime import datetime, timedelta

app = Flask(__name__)

username = urllib.parse.quote_plus('test-user')
password = urllib.parse.quote_plus('ForIvanAndRussians')
client = MongoClient("mongodb+srv://%s:%s@initial-mined-data.w3ygy.mongodb.net" % (username, password))
db = client.Datathon

@app.route('/form')
def form():
    return render_template('form.html')

@app.route("/data/", methods=["GET", "POST"])
def data():

    if request.method == 'GET':
        return f"The URL /data is accessed directly. Try going to '/form' to submit form"
    if request.method == 'POST':
        form_data = request.form

    student_cache = dict()
    name = dict(request.form)["Name"]
    className = dict(request.form)["Class"]

    with open("./tmp/Student.json", "w") as outfile:
        instance = db["Student"].find_one({"name": name})
        student_cache["Student"] = instance
        student_id = instance['student_id']
        json_line = json.loads(json_util.dumps(instance))
        outfile.write(str(json_line))
        outfile.write("\n")

    course_map = dict()

    with open("./tmp/StudentCourse.json", "w") as outfile:
        student_cache["StudentCourse"] = []
        for doc in db["StudentCourse"].find({"student_id": student_id}):
            json_line = json.loads(json_util.dumps(doc))
            outfile.write(str(json_line))
            outfile.write("\n")
            student_cache["StudentCourse"].append(doc)
            if doc.get("course_id") not in course_map.keys():
                course_map[doc.get("course_id")] = None

    student_cache["Course"] = dict()

    with open("./tmp/Course.json", "w") as outfile:
        for course_id in course_map.keys():
            instance = db["Course"].find_one({"course_id": str(course_id)})
            student_cache["Course"][course_id] = instance
            json_line = json.loads(json_util.dumps(instance))
            outfile.write(str(json_line))
            outfile.write("\n")

    return str(student_cache)

def get_class(student_cache, course_id, db):
    if student_cache.get("Course") is None:
        student_cache["Course"] = dict()
    student_cache["Course"][course_id] = db["Course"].find_one({"course_id": course_id})
    return student_cache

if __name__ == "__main__":
    app.run()
