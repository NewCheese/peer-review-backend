import requests
import json

Dev_url = "http://192.168.0.6:82/"
Prod_url = "https://peer-review-backend.herokuapp.com/"


def test_CreateCourse() :
    myobj = {'LecturerId': 1 , "CourseName" : "Mock Test" , "Credits":10}
    response = requests.post(Dev_url+"/add/course/", json = myobj)
    assert response.status_code == 200


def test_getCourses() :
    response = requests.get(Dev_url+"/get/courses/")
    assert response.status_code == 200

def test_Rating() :
    stars = 3
    assignment_id = 4715730
    student_id = 3
    myobj = {'AssignmentID': assignment_id , "Stars" : stars}
    response = requests.put(Dev_url+"/put/stars/{}".format(student_id), json = myobj)
    assert response.status_code == 200

def test_getTemplates() :
    response = requests.get(Dev_url+"/get/templates/")
    assert response.status_code == 200

def test_deleteModule() :
    response = requests.delete(Dev_url+"/delete/course/2")
    assert response.status_code == 200


def test_enrolledCourses() :
    response = requests.get(Dev_url+"/get/enrolledCourses/2")
    assert response.status_code == 200


def test_studentsCourse() :
    response = requests.get(Dev_url+"/get/students/1")
    assert response.status_code == 200

def test_addTemplate() :
    Name = "Formative assessment"
    Description = "DEEP"
    TemplateType = "1"
    myobj = {'Name': Name , "Description" : Description, "Format":TemplateType}
    response = requests.post(Dev_url+"/add/template/", json = myobj)
    assert response.status_code == 200

def test_getAssignments() :
    response = requests.get(Dev_url+"/get/assignments/")
    assert response.status_code == 200

def test_getAssignments() :
    response = requests.get(Dev_url+"/get/assignments/")
    assert response.status_code == 200

def test_getCourse() :
    response = requests.get(Dev_url+"/get/course/1")
    assert response.status_code == 200

def test_getTemplate() :
    response = requests.get(Dev_url+"/get/template/1")
    assert response.status_code == 200

def test_getQuestions() :
    response = requests.get(Dev_url+"/get/questions/1")
    assert response.status_code == 200

def test_getQuestion() :
    response = requests.get(Dev_url+"/get/questions/1")
    assert response.status_code == 200

def test_getCourseAssignment() :
    response = requests.get(Dev_url+"/get/course/assignment/1")
    assert response.status_code == 200

def test_getAllStudents():
    response = requests.get(Dev_url+"/get/all/students/")
    assert response.status_code == 200