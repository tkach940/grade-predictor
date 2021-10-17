from flask import Flask, request, render_template
from pymongo import MongoClient
import urllib
import json
from bson import json_util, ObjectId
from datetime import datetime, timedelta
import json
import re
from datetime import date
import math
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.feature_selection import RFE

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
    class_name = dict(request.form)["Class"]

    curr_course_instance = db["Course"].find_one({"course_name": class_name})
    curr_course_id = curr_course_instance.get("course_id")

    with open("./tmp/Student.json", "w") as outfile:
        instance = db["Student"].find_one({"name": name})
        json_line = json.loads(json_util.dumps(instance))
        student_cache["Student"] = json_line
        student_id = json_line['student_id']
        outfile.write(str(json_line))
        outfile.write("\n")

    course_map = dict()

    with open("./tmp/StudentCourse.json", "w") as outfile:
        student_cache["StudentCourse"] = []
        for doc in db["StudentCourse"].find({"student_id": student_id}):
            json_line = json.loads(json_util.dumps(doc))
            outfile.write(str(json_line))
            outfile.write("\n")
            student_cache["StudentCourse"].append(json_line)
            if doc.get("course_id") not in course_map.keys():
                course_map[doc.get("course_id")] = None

    student_cache["Course"] = dict()

    with open("./tmp/Course.json", "w") as outfile:
        for course_id in course_map.keys():
            if course_id == curr_course_id:
                continue
            instance = db["Course"].find_one({"course_id": str(course_id)})
            json_line = json.loads(json_util.dumps(instance))
            if json_line is None:
                continue
            student_cache["Course"][course_id] = json_line
            outfile.write(str(json_line))
            outfile.write("\n")

    with open("./tmp/sample.json", "w") as outfile:
        outfile.write(str(student_cache))

    stud_list = student_cache["Student"]
    course_list = student_cache["Course"]
    sc_list = student_cache["StudentCourse"]
    course = curr_course_instance

    #return create_train_data(stud_list, course_list, sc_list, course)
    X_train, y_train = create_train_data(stud_list, course_list, sc_list, course)
    return str(predict_grade(X_train, y_train)[0]) + "%"

def construct_season():
    today = date.today()
    m = today.strftime("%m")
    y = today.strftime("%y")
    if (12 >= int(m) > 8):
        season = 'f'
    elif (6 > int(m) >= 1):
        season = 's'
    term = season + y
    return term

def subtract_seasons(curr, query):
    temp = re.compile("([\sa-zA-Z]+)([0-9]+)")
    term1 = temp.match(curr).groups()
    term2 = temp.match(query).groups()
    if (term1[0] == term2[0]):
        diff = 2*(int(term1[1]) - int(term2[1]))
    else:
        diff = 2*(int(term1[1]) - int(term2[1])) - 1
    return diff

def create_train_data(stud_list, course_list, sc_list, course):
    needed_course_id = course['course_id']

    current_term = construct_season()

    # Splitting text and number in string
    form = re.compile("([\sa-zA-Z]+)([0-9]+)")
    res = form.match(course['course_name']).groups()
    course_subject = res[0].strip().lower()
    course_no = res[1]

    major_list = stud_list.get('major_list')
    major_list = [major.lower() for major in major_list]

    course_credits = course['credits']

    i = 0
    s = ""
    for sc in sc_list:
        X1 = 5/(abs(subtract_seasons(current_term, sc['term_id'])))

        iter_course_name = course_list.get(sc.get('course_id')).get("course_name")
        subjectMatch = 6 if course_subject == form.match(iter_course_name).groups()[0].strip().lower() else 0

        numMatch = 4/(math.ceil(abs(int(course_no) - int(form.match(iter_course_name).groups()[1]))/100))

        X2 = subjectMatch + numMatch

        X3 = 5 if course_subject in major_list else 0

        X4 = 2/(abs(int(course_credits) - int(course_list.get(sc.get('course_id')).get('credits'))) + 1)

        y = round(int(sc['performance'])/10)*10


        if (i == 0):
            X_train = np.array([X1, X2, X3, X4])
            y_train = np.array([y])
            i = 1
        else:
            X_train = np.vstack([X_train,[X1, X2, X3, X4]])
            y_train = np.vstack([y_train,[y]])
    return X_train, y_train

def predict_grade(X_train, y_train):
    X_test = np.array([[5, 10, 5, 2]])

    logreg = LogisticRegression(multi_class='multinomial', solver='lbfgs')

    logreg.fit(X_train, y_train)
    y_pred=logreg.predict(X_test)
    return y_pred

if __name__ == "__main__":
    app.run()
