from ast import Assign
from email.headerregistry import Group
from email.policy import default
from enum import unique
from fileinput import filename
from tokenize import group
from flask_sqlalchemy import SQLAlchemy
import flask
from flask import Flask
import os
import json
from flask import Flask, request, flash, url_for, redirect, render_template, jsonify
from datetime import datetime
from flask_marshmallow import Marshmallow
from flask import jsonify, make_response
from flask_cors import CORS
from strenum import StrEnum
from flask_mail import Mail, Message
import random
import string
from  sqlalchemy.sql.expression import func
from cryptography.fernet import Fernet
def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    print("Random string of length", length, "is:", result_str)
    return result_str

def buildEmailAddress(student_id):
   return student_id+'@student.gla.ac.uk'

def return_studentID(EmailAddress):
   result = EmailAddress.split("@")
   return result[0]

app = Flask (__name__)
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///PeerReviewSystem.sqlite3'
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
db = SQLAlchemy(app)
ma = Marshmallow(app)
CORS(app)

# key = Fernet.generate_key()
# fernet = Fernet(key)

key = "azUXsRqV_Wv4ooxceKMTxDMFVxnF36LhD4RCnBFzFRE="
fernet = Fernet(key)
email_temp_password = "gAAAAABjEV5iNOSJtzIbdm97q9HAjkD7thebjUQTT7Z8KkfDDfKYdmz9WWwD-1QWlEs6vRptzZcwg_m0db9eh9y2ItwUPwAz5Hf0wmRhl_zAQna_S5ZraXw="
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'w1234panku@gmail.com'
app.config['MAIL_PASSWORD'] = str(fernet.decrypt(email_temp_password.encode()).decode())
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

class UserTypes(StrEnum):
   student = 'Student',
   teacher = 'Teacher'


class User(db.Model):
   __tablename__ = 'user'
   ID = db.Column('ID', db.Integer, primary_key = True)
   EmailAddress = db.Column(db.String(100),unique=True)
   Password = db.Column(db.String(50))  
   FirstName = db.Column(db.String(200))
   LastName = db.Column(db.String(10))
   UserType = db.Column(db.String(10))

   def __init__(self, EmailAddress, Password=None, FirstName=None,LastName=None,UserType=None):
      self.EmailAddress = EmailAddress
      self.Password = Password
      self.FirstName = FirstName
      self.LastName = LastName
      self.UserType = UserType

   def createStudent(self,EmailAddress):
      self.EmailAddress = EmailAddress
      self.UserType = UserTypes.student
   def setProfile(self,password,firstName,lastName):
      self.Password = password
      self.FirstName = firstName
      self.LastName = lastName   
   def __repr__(self) -> str:
       return super().__repr__()

class UserSchema(ma.Schema):
    class Meta:
        fields = ("ID", "EmailAddress", "Password","FirstName","LastName","UserType")
userSchema = UserSchema()
userSchema_ = UserSchema(many=True)



class Student(db.Model):
   __tablename__ = 'student'
   ID = db.Column('ID', db.Integer, primary_key = True)
   UserId = db.Column(db.Integer,db.ForeignKey('user.ID'),nullable=False) 

   def __init__(self,UserId):
      self.UserId = UserId
class StudentSchema(ma.Schema):
    class Meta:
        fields = ("ID", "UserId")
studentSchema = StudentSchema()
studentSchema_ = StudentSchema(many=True)  

class Lecturers(db.Model):
   __tablename__ = 'professors'
   ID = db.Column('ID', db.Integer, primary_key = True)
   UserId = db.Column(db.Integer,db.ForeignKey('user.ID'),nullable=False) 

   def __init__(self,UserId):
      self.UserId = UserId  

class LecturersSchema(ma.Schema):
    class Meta:
        fields = ("ID", "UserId")
lecturersSchema = LecturersSchema()
lecturersSchema_ = LecturersSchema(many=True)  


class Course(db.Model):
   __tablename__ = 'course'
   ID = db.Column('ID', db.Integer, primary_key = True)
   hasAssignment = db.Column(db.Boolean, default=False)
   LecturerId = db.Column(db.Integer,db.ForeignKey('professors.ID'),nullable=False)
   CourseName = db.Column(db.String(50))  
   Credits = db.Column(db.String(200))
   CreationDate = db.Column(db.DateTime)
   

   def __init__(self, LecturerId, CourseName, Credits):
      self.LecturerId = LecturerId
      self.CourseName = CourseName
      self.Credits = Credits
      self.CreationDate = datetime.now()
      self.hasAssignment = False

   def updateDetails(self, LecturerId, CourseName, Credits):
      self.LecturerId = LecturerId
      self.CourseName = CourseName
      self.Credits = Credits
      self.CreationDate = datetime.now()
   
   def yesAssignment(self):
      self.hasAssignment = True  

   def noAssignment(self):
      self.hasAssignment = False 


class CourseSchema(ma.Schema):
    class Meta:
        fields = ("ID", "LecturerId", "CourseName","Credits","CreationDate","hasAssignment")
courseSchema = CourseSchema()
courseSchema_ = CourseSchema(many=True)


class StudentCourse(db.Model):
   __tablename__ = 'studentcourse'
   CourseID = db.Column('ID', db.Integer, db.ForeignKey('course.ID') , primary_key = True )
   StudentID = db.Column(db.String,db.ForeignKey('student.ID'),primary_key = True) 
   Status = db.Column(db.Boolean)
   def __init__(self,CourseID,StudentID):
      self.StudentID = StudentID  
      self.CourseID = CourseID
      self.Status = False
   def updateStatus(self,Status):
      self.Status = Status

class StudentCourseSchema(ma.Schema):
    class Meta:
        fields = ("CourseID", "StudentID","Status")
studentcourseSchema = StudentCourseSchema()
studentcourseSchema_ = StudentCourseSchema(many=True)

class QuestionareTemplate(db.Model):
   __tablename__ = 'questionaretemplate'
   ID = db.Column('ID', db.Integer, primary_key = True)
   Name = db.Column(db.String(50), unique=True)  
   Description = db.Column(db.String(200))
   TemplateType = db.Column(db.String)
   CreationDate = db.Column(db.DateTime)
   

   def __init__(self, Name,Description,TemplateType):
      self.Name = Name
      self.Description = Description
      self.TemplateType = TemplateType
      self.CreationDate = datetime.now()
   
   def updateInformation(self, Name,Description,TemplateType):
      self.Name = Name
      self.Description = Description
      self.TemplateType = TemplateType
      self.CreationDate = datetime.now()

class QuestionareTemplateSchema(ma.Schema):
    class Meta:
        fields = ("ID", "LecturerId", "Name","Description","TemplateType","CreationDate")
QTSchema = QuestionareTemplateSchema()
QTSchema_ = QuestionareTemplateSchema(many=True)

class Questionare(db.Model):
   __tablename__ = 'questionare'
   ID = db.Column('ID', db.Integer, primary_key = True)
   TemplateID = db.Column(db.Integer , db.ForeignKey('questionaretemplate.ID'))
   Sequence = db.Column(db.Integer)
   Question = db.Column(db.String(200))
   CreationDate = db.Column(db.DateTime)
   

   def __init__(self, TemplateID, Sequence, Question):
      self.TemplateID = TemplateID
      self.Question = Question
      self.Sequence = Sequence
      self.CreationDate = datetime.now()

   def updateQuestions(self, Question):
      self.Question = Question
      self.CreationDate = datetime.now()

class QuestionareSchema(ma.Schema):
    class Meta:
        fields = ("ID", "TemplateID", "Sequence","Question","CreationDate")

quSchema = QuestionareSchema()
quSchema_ = QuestionareSchema(many=True)   


class GroupWork(db.Model):
   __tablename__ = 'GroupWork'
   ID = db.Column('ID', db.Integer, primary_key = True)
   AssignmentID = db.Column(db.Integer,db.ForeignKey('assignment.AssignmentID') )
   GroupID = db.Column('GroupID',db.Integer)
   UserID = db.Column(db.String(200), db.ForeignKey('user.ID'))

   def __init__(self,AssignmentID=None,GroupID=None,UserID=None) -> None:
       super().__init__()
       self.UserID = UserID
       self.GroupID = GroupID
       self.AssignmentID = AssignmentID
   def updateID(self,GroupID):
      self.GroupID = GroupID
       
class Assignment(db.Model):
   __tablename__ = 'assignment'
   ID = db.Column('ID', db.Integer, primary_key = True)
   AssignmentID = db.Column(db.Integer)
   CourseID = db.Column(db.Integer , db.ForeignKey('course.ID'))
   TemplateID = db.Column(db.String(200), db.ForeignKey('questionare.ID'))
   GroupSubmission = db.Column(db.Integer, db.ForeignKey('GroupWork.GroupID'))
   GroupSize = db.Column(db.Integer)
   Weightage = db.Column(db.Integer)
   TaskName = db.Column(db.String(200))
   Explaination = db.Column(db.String(200))
   CreationDate = db.Column(db.DateTime)
   SubmissionDate = db.Column(db.DateTime)
   PeerReviewDate = db.Column(db.DateTime)
   SubmissionEndDate = db.Column(db.DateTime)
   PeerReviewEndDate = db.Column(db.DateTime)

   def __init__(self,AssignmentID, CourseID, TemplateID,TaskName,Explaination,Weightage,SubmissionDate,PeerReviewDate,SubmissionEndDate,PeerReviewEndDate,GroupSubmission=None,GroupSize=None):
      self.AssignmentID =AssignmentID
      self.CourseID = CourseID
      self.TemplateID = TemplateID
      self.TaskName = TaskName
      self.Explaination = Explaination
      self.GroupSubmission = GroupSubmission
      self.CreationDate = datetime.now()
      self.Weightage = Weightage
      self.SubmissionDate = SubmissionDate
      self.PeerReviewDate = PeerReviewDate
      self.GroupSize = GroupSize
      self.PeerReviewEndDate = PeerReviewEndDate
      self.SubmissionEndDate = SubmissionEndDate
   def updateAssignment(self,CourseID,TemplateID,TaskName,SubmissionDate,PeerReviewDate,Explaination,Weightage,SubmissionEndDate,PeerReviewEndDate):
      self.CourseID = CourseID
      self.TemplateID = TemplateID
      self.TaskName = TaskName
      self.Explaination = Explaination
      self.GroupSubmission = None
      self.CreationDate = datetime.now()
      self.Weightage = Weightage
      self.SubmissionDate = SubmissionDate
      self.PeerReviewDate = PeerReviewDate
      self.SubmissionEndDate = SubmissionEndDate
      self.PeerReviewEndDate = PeerReviewEndDate

class AssignmentSchema(ma.Schema):
    class Meta:
        fields = ("ID","AssignmentID","CourseID", "TemplateID","GroupSubmission","TaskName","ID", "Explaination","Weightage", "SubmissionDate","PeerReviewDate","isSubmitted","isPeerReviewed","GroupSize","SubmissionEndDate","PeerReviewEndDate")

assSchema = AssignmentSchema()
assSchema_ = AssignmentSchema(many=True)  


class Submission(db.Model):
   __tablename__ = 'submission'
   ID = db.Column('ID', db.Integer, primary_key = True)
   GroupID = db.Column(db.Integer, db.ForeignKey('GroupWork.GroupID'))
   StudentID = db.Column(db.Integer , db.ForeignKey('questionaretemplate.ID'))
   AssignmentID = db.Column(db.Integer , db.ForeignKey('assignment.AssignmentID'))
   FileName = db.Column(db.String)
   FileSubmission = db.Column(db.LargeBinary)
   SubmissionDate = db.Column(db.DateTime)
   isMarked = db.Column(db.Boolean,default= False)

   

   def __init__(self,GroupID, StudentID, AssignmentID, FileSubmission,FileName):
      self.GroupID = GroupID
      self.StudentID = StudentID
      self.AssignmentID = AssignmentID
      self.FileSubmission = FileSubmission
      self.FileName = FileName
      self.SubmissionDate = datetime.now()
      self.isMarked = False


class SubmissionSchema(ma.Schema):
    class Meta:
        fields = ("ID","GroupID","StudentID", "AssignmentID","FileSubmission","SubmissionDate","isMarked","FileName")

subSchema = SubmissionSchema()
subSchema_ = SubmissionSchema(many=True) 

class PeerReview(db.Model):
   __tablename__ = 'PeerReview'
   ID = db.Column('ID', db.Integer, primary_key = True)
   SubmissionID =  db.Column(db.Integer , db.ForeignKey('submission.ID'))
   reviewerStudentID = db.Column(db.Integer , db.ForeignKey('student.ID'))
   submissionStudentID = db.Column(db.Integer, db.ForeignKey('student.ID'))
   GroupID = db.Column(db.Integer, db.ForeignKey('GroupWork.GroupID'))
   AssignmentID = db.Column(db.Integer, db.ForeignKey('assignment.AssignmentID'))
   TemplateID = db.Column(db.Integer, db.ForeignKey('questionaretemplate.ID'))
   Sequence = db.Column(db.Integer)
   Answer = db.Column(db.String)
   isPeerReview = db.Column(db.Boolean)
   SubmissionDate = db.Column(db.DateTime)
   Rating = db.Column(db.Integer)

   def __init__(self, SubmissionID,GroupID,reviewerStudentID, submissionStudentID,Sequence,AssignmentID,Answer):
    self.reviewerStudentID = reviewerStudentID
    self.submissionStudentID = submissionStudentID
    self.AssignmentID = AssignmentID
    self.Sequence = Sequence
    self.Answer = Answer
    self.isPeerReview = True
    self.reviewerStudentID = reviewerStudentID
    self.SubmissionDate = datetime.now()
    self.GroupID = GroupID
    self.SubmissionID = SubmissionID


class PeerSchema(ma.Schema):
    class Meta:
        fields = ("ID", "Rating","GroupID","reviewerStudentID", "submissionStudentID","AssignmentID","TemplateID","Answer", "isPeerReview","Sequence","SubmissionDate")

peerSchema = PeerSchema()
peerSchema_ = PeerSchema(many=True)  




@app.route('/post/peer/review', methods = ['POST'])
def peerReviewSubmission():
   data = request.get_json()
   SubmissionID = data["SubmissionID"]
   reviewerStudentID = data['reviewerStudentID']
   submissionStudentID = data['submissionStudentID']
   GroupID = data['GroupID']
   Sequence = data['Sequence']
   Answer = data['Answer']
   AssignmentID = data['AssignmentID']
   submission = Submission.query.filter(Submission.ID == SubmissionID).first()
   submission.isMarked = True
   db.session.add(submission)
   if GroupID is 0 :
      obj = PeerReview(SubmissionID=SubmissionID,GroupID=GroupID,reviewerStudentID=reviewerStudentID,submissionStudentID=submissionStudentID,Sequence=Sequence,AssignmentID=AssignmentID,Answer=Answer)
      db.session.add(obj)
      db.session.commit()
      return make_response(peerSchema.jsonify(obj),200)
   gp = GroupWork.query.filter(GroupWork.AssignmentID == AssignmentID, GroupWork.UserID == reviewerStudentID ).all()
   result = []
   for stud in gp :
      obj = PeerReview(SubmissionID=SubmissionID,GroupID=stud.GroupID,reviewerStudentID=stud.UserID,submissionStudentID=submissionStudentID,Sequence=Sequence,AssignmentID=AssignmentID,Answer=Answer)  
      result.append(obj)
      db.session.add(obj)
   db.session.commit()  
   return make_response(assSchema_.jsonify(result),200)   

   

@app.route('/add/course/', methods = ['POST'])
def addCourse():
   data = request.get_json()
   LecturerId = data['LecturerId']
   CourseName = data['CourseName']
   Credits = data['Credits']
   if int(Credits) < 0 or int(Credits)>60 :
      return {
         "message" : "Credits out of range exception" ,
         "StatusCode" : 401 ,
         "Body" : None
      }  
   duplicate_check = Course.query.filter(Course.CourseName == CourseName).all()  
   if len(duplicate_check) is not 0 :
       return make_response({
         "message" : "Subject Already present, choose some other name" ,
         "StatusCode" : 401 
      } ) 
   newCourse = Course(LecturerId=LecturerId, CourseName=CourseName,Credits=Credits)
   db.session.add(newCourse)
   db.session.commit()
   return make_response(courseSchema.jsonify(newCourse),200)

# self, StudentID, AssignmentID, submission,FileName

@app.route('/add/submission/', methods = ['POST'])
def addSubmission():
   StudentID = request.form['StudentID']
   AssignmentID = request.form['AssignmentID']
   FileSubmission = request.files['file']
   GroupID = int(request.form['GroupID'])
   FileName = request.files['file'].filename
   filename = FileName.split(".")
   if GroupID > 0 :
      studs = GroupWork.query.filter(GroupWork.GroupID == GroupID, GroupWork.AssignmentID == AssignmentID).all()
      for stud in studs :    
         path = "files/Assignment"+AssignmentID+"Student"+stud.UserID+"."+filename[1]
         FileSubmission.save(path)
         sub = Submission(GroupID =  stud.GroupID,StudentID=stud.UserID,AssignmentID=AssignmentID,FileSubmission=None,FileName=path)
         db.session.add(sub)
         db.session.commit()
      return make_response({
         "message":"Submitted successfully"
      },200)
   print("Invidual Assignment")   
   FileName = request.files['file'].filename
   filename = FileName.split(".")
   path = "files/Assignment"+AssignmentID+"Student"+StudentID+"."+filename[1]
   FileSubmission.save(path)
   sub = Submission(GroupID=GroupID,StudentID=StudentID,AssignmentID=AssignmentID,FileSubmission=None,FileName=path)
   db.session.add(sub)
   db.session.commit()
   return make_response(subSchema.jsonify(sub),200)

@app.route('/get/submission/<assignment_id>/<student_id>', methods = ['GET'])
def getSubmission(assignment_id,student_id):
   subs = Submission.query.filter(Submission.AssignmentID == assignment_id,Submission.StudentID == student_id).first()
   return make_response(subSchema.jsonify(subs),200)

@app.route('/get/peer/<assignment_id>/<student_id>', methods = ['GET'])
def getPeerReview(assignment_id,student_id):
   res = PeerReview.query.filter(PeerReview.AssignmentID == assignment_id, PeerReview.submissionStudentID == student_id).all()
   return make_response(peerSchema_.jsonify(res),200)

@app.route('/get/submissions/<assignment_id>/<student_id>', methods = ['GET'])
def getSubmissions(assignment_id,student_id):
   user = GroupWork.query.filter(GroupWork.AssignmentID == assignment_id, GroupWork.UserID == student_id).first()
   if user is None :
      print("Individual Submission")
      subs = Submission.query.filter(Submission.AssignmentID == assignment_id, Submission.isMarked == False, Submission.StudentID != student_id).order_by(func.random()).limit(1).all()
   else :
      subs = Submission.query.filter(Submission.AssignmentID == assignment_id, Submission.isMarked == False,Submission.GroupID != user.GroupID).order_by(func.random()).limit(1).all()
   return make_response(subSchema_.jsonify(subs),200)

from flask import send_file

@app.route('/download/<dir>/<file_name>', methods = ['GET'])
def downloadFile(dir,file_name):
   return send_file(dir+'/'+file_name, as_attachment=True)

@app.route('/login', methods = ['POST'])
def login():
   data = request.get_json()
   print(data)
   username = data['username']
   password = data['password']
   EmailAddress = buildEmailAddress(username)
   user = db.session.query(User).filter(User.EmailAddress == EmailAddress).first()
   if user is not None and user.Password == password :
      return make_response(
         userSchema.jsonify(user),200
      )
   return make_response({
      "message":"Something went wrong, please enter a valid username and password",
      "errorCode":"404"
   })

@app.route('/get/courses/', methods = ['GET'])
def getCourses():
   Courses = db.session.query(Course).all()
   return make_response(courseSchema_.jsonify(Courses),200)

@app.route('/get/course/<course_id>', methods = ['GET'])
def getCourse(course_id):
   course = Course.query.filter(Course.ID == course_id).first()
   if course is None :
      return make_response({
         "messsage" : "No course found"
      }, 401)
   return make_response(courseSchema.jsonify(course),200)
   
@app.route('/put/course/<course_id>', methods = ['PUT'])
def updateCourse(course_id):
   data = request.get_json()
   LecturerId = data['LecturerId']
   CourseName = data['CourseName']
   Credits = data['Credits']
   course = Course.query.filter(Course.ID == course_id).first()
   course.updateDetails(LecturerId,CourseName,Credits)
   db.session.add(course)
   db.session.commit()
   if course is None :
      return make_response({
         "messsage" : "No course found"
      }, 401)

   return make_response(courseSchema.jsonify(course),200)
   
@app.route('/delete/course/<course_id>', methods = ['DELETE'])
def deleteCourse(course_id):
   course = Course.query.filter(Course.ID == course_id).first()
   enrolledStudents = StudentCourse.query.filter(StudentCourse.CourseID == course_id).all()
   assigned = Assignment.query.filter(Assignment.CourseID == course_id).all()
   for s in enrolledStudents :
    db.session.delete(s) 
   for i in assigned :
      db.session.delete(i)
   db.session.delete(course)
   db.session.commit()
   return make_response(courseSchema.jsonify(course),200)


@app.route('/set/profile/<user_id>', methods = ['PUT'])
def setProfile(user_id):
   data = request.get_json()
   print(data)
   password_ = data['Password']
   fn = data['FirstName']
   ln = data['LastName']
   user = User.query.filter(User.ID == user_id).first()
   user.setProfile(password_,fn,ln)
   courses = StudentCourse.query.filter(StudentCourse.StudentID == user_id).all()
   print(courses)
   for i in courses :
      i.Status = True
      print(i)
      db.session.add(i)
   db.session.add(user)
   db.session.commit()
   return make_response({
      "message":"Record Added successfully"
   })

@app.route('/reset/password/<user_id>', methods = ['POST'])
def resetPassword(user_id):
   EmailAddress = buildEmailAddress(user_id)
   user =User.query.filter(User.EmailAddress == EmailAddress).first()
   pass_ = get_random_string(7)
   msg = Message('Reset Password for Peer Review Application', sender = 'w1234panku@@gmail.com', recipients = [EmailAddress])
   msg.body = "Hi  You have requested to reset the password for Peer Review Application" +". Your new password is "+pass_
   user.Password = pass_
   db.session.add(user)
   db.session.commit()
   res = mail.send(msg)
   return make_response({
      "message":"Send Successfully"
   })
   

@app.route('/add/student/<course_id>', methods = ['POST'])
def addStudentCourse(course_id):
   # can add a function to get the student id from the email address 
   data = request.get_json()
   studentID = data['StudentID']
   EmailAddress = buildEmailAddress(studentID)
   user = User.query.filter(User.EmailAddress == EmailAddress).first()
   print(user)
   if user is None :
      user = User(EmailAddress=EmailAddress)
      user.createStudent(EmailAddress=EmailAddress)
      # can add a status column in student table to confirm if they have joined 
      db.session.add(user)
      db.session.commit()  
   student = Student(user.ID) 
   db.session.add(student)
   db.session.commit()  

   course_added = Course.query.filter(Course.ID == course_id).first()  
   msg = Message('Module assigned', sender = 'w1234panku@@gmail.com', recipients = [EmailAddress])
   msg.html = "You have been added to "+ course_added.CourseName +", Click here to join the course" + "<a href='https://peer-review-system-uog.herokuapp.com/setProfile?ID={}'> Link </a>".format(user.ID)
   res = mail.send(msg)
   studentCourse = StudentCourse.query.filter(StudentCourse.CourseID == course_id, StudentCourse.StudentID==user.ID).first()
   if studentCourse is not None :
      return make_response({
         "message" : "Student already enrolled in course",
         "statusCode" : "403"
      })

   enrolled_student = StudentCourse(course_id,user.ID) 
   db.session.add(enrolled_student)
   db.session.commit()  
   return make_response(studentcourseSchema.jsonify(enrolled_student),200)

@app.route('/get/all/students/', methods = ['GET'])
def getAllStudents():
   allStudents = User.query.filter(User.UserType == UserTypes.student).all()
   if len(allStudents) is 0 :
      return make_response({
         "message" : "No students",
         "statusCode":"404"
      })
   return make_response(userSchema_.jsonify(allStudents),200)

@app.route('/get/students/<course_id>', methods = ['GET'])
def getStudentsCourse(course_id):
   # can add a function to get the student id from the email address 
   allStudentsCourse = StudentCourse.query.filter(StudentCourse.CourseID == course_id).all()
   if len(allStudentsCourse) is 0 :
      return make_response({
         "message" : "No students enrolled in this course",
         "statusCode":"404"
      })
   return make_response(studentcourseSchema_.jsonify(allStudentsCourse),200)

@app.route('/delete/student/<course_id>', methods = ['DELETE'])
def deleteStudentsCourse(course_id):
   data = request.get_json()
   EmailAddress = data['EmailAddress']
   student = StudentCourse.query.filter(StudentCourse.CourseID == course_id, StudentCourse.StudentID == EmailAddress).first()
   if student is None :
      return make_response({
         "body":"Student is not enrolled in this course",
         "statusCode":"401"
      })
   db.session.delete(student)
   db.session.commit()
   return make_response(studentcourseSchema.jsonify(student),200)


@app.route('/add/template/', methods = ['POST'])
def addTemplate():
   data = request.get_json()
   Name = data['Name']
   Description = data['Description']
   TemplateType = data['Format']
   existingTemplate = QuestionareTemplate.query.filter(QuestionareTemplate.Name == Name).first()
   if existingTemplate is not None :
      return make_response({
         "message" : "Course Already exists" ,
         "statusCode" : "403"
      })
   newTemplate = QuestionareTemplate(Name=Name,Description=Description,TemplateType=TemplateType)
   db.session.add(newTemplate)
   db.session.commit()
   return make_response(QTSchema.jsonify(newTemplate),200)

@app.route('/get/templates/', methods = ['GET'])
def getTemplates():
   existingTemplates = QuestionareTemplate.query.filter().all() 
   if existingTemplates is  None :
      return make_response({
         "message" : "No Templates found",
         "statusCode" : "403"
      })
   
   return make_response(QTSchema_.jsonify(existingTemplates),200)
   
@app.route('/get/template/<template_id>', methods = ['GET'])
def getTemplate(template_id):
   existingTemplates = QuestionareTemplate.query.filter(QuestionareTemplate.ID == template_id).first() 
   if existingTemplates is  None :
      return make_response({
         "message" : "No Templates found",
         "statusCode" : "403"
      })
   
   return make_response(QTSchema.jsonify(existingTemplates),200)


@app.route('/put/stars/<ID>', methods = ['PUT'])
def putStars(ID):
   data = request.get_json()
   stars = int(data['Stars'])
   assignment_id = data['AssignmentID']
   sub = Submission.query.filter(Submission.AssignmentID == assignment_id, Submission.StudentID == ID).first()
   if sub.GroupID is not 0 :
      gps = GroupWork.query.filter(GroupWork.AssignmentID == assignment_id , GroupWork.GroupID == sub.GroupID).all()
      for i in gps :
         res = PeerReview.query.filter(PeerReview.AssignmentID == assignment_id, PeerReview.submissionStudentID == i.UserID).all()
         if len(res) is not 0 :
            break
      for k in res :
         k.Rating = stars
         db.session.add(k)
         db.session.commit()
      return make_response(peerSchema_.jsonify(res),200)
   else :
      res = PeerReview.query.filter(PeerReview.AssignmentID == assignment_id,
                           PeerReview.submissionStudentID == ID).all()
      for k in res :
         k.Rating = stars
         db.session.add(k)
         db.session.commit()
      return make_response(peerSchema_.jsonify(res),200)

@app.route('/put/template/<template_id>', methods = ['PUT'])
def putTemplate(template_id):
   data = request.get_json()
   Name = data['Name']
   Description = data['Description']
   Format = data['Format']
   existingTemplate = QuestionareTemplate.query.filter(QuestionareTemplate.Name == Name).first() 
   if existingTemplate is not None :
      print(existingTemplate)
      return make_response({
         "message" : "Course name already present,Try a unique name" ,
         "statusCode" : "403"
      })
   existingTemplate = QuestionareTemplate.query.filter(QuestionareTemplate.ID == template_id).first() 
   existingTemplate.updateInformation(Name,Description,Format)
   db.session.add(existingTemplate)
   db.session.commit()
   return make_response(QTSchema.jsonify(existingTemplate),200)

@app.route('/delete/template/<template_id>', methods = ['DELETE'])
def deleteTemplate(template_id):
   existingTemplate = QuestionareTemplate.query.filter(QuestionareTemplate.ID == template_id).first() 
   allQuestions = Questionare.query.filter(Questionare.TemplateID == existingTemplate.ID).all()
   for i in allQuestions :
      db.session.delete(i)
   db.session.delete(existingTemplate)
   db.session.commit()
   return make_response(QTSchema.jsonify(existingTemplate),200)


@app.route('/add/question/', methods = ['POST'])
def addQuestion():
   data = request.get_json()
   TemplateID = data['TemplateID']
   Question = data['Question']
   Sequence = 0
   allQuestions = Questionare.query.filter(Questionare.TemplateID == TemplateID).all()
   Sequence = len(allQuestions) + 1
   newQuestion = Questionare(TemplateID=TemplateID,Question=Question,Sequence = Sequence)
   db.session.add(newQuestion)
   db.session.commit()
   return make_response(quSchema.jsonify(newQuestion),200)

@app.route('/get/questions/<template_id>', methods = ['GET'])
def getQuestions(template_id):
   allQuestions = Questionare.query.filter(Questionare.TemplateID == template_id).all()
   return make_response(quSchema_.jsonify(allQuestions),200)

@app.route('/put/question/<ID>', methods = ['PUT'])
def updateQuestion(ID):
   data = request.get_json()
   Question = data['Question']
   newQuestion = Questionare.query.filter(Questionare.ID == ID).first()
   if newQuestion is None :
      return make_response({
         "message" : "No questions found",
         "statusCode": "401"
      })
   newQuestion.updateQuestions(Question)
   db.session.add(newQuestion)
   db.session.commit()
   return make_response(quSchema.jsonify(newQuestion),200)

@app.route('/get/questions/<ID>', methods = ['GET'])
def getQuestion(ID):
   question = Questionare.query.filter(Questionare.ID == ID).first()
   return make_response(quSchema.jsonify(question),200)

@app.route('/delete/question/<ID>/<TemplateID>', methods = ['DELETE'])
def deleteQuestion(ID,TemplateID):
   existingQuestion = Questionare.query.filter(Questionare.ID == ID).first() 
   if existingQuestion is None :
      return make_response({
         "message":"No Question Found",
         "statusCode":"401"
      })
   sequence = existingQuestion.Sequence
   existingQuestions = Questionare.query.filter(Questionare.TemplateID == TemplateID, Questionare.Sequence > int(sequence)).all()
   print(existingQuestions)
   if existingQuestions is None :
      return make_response({
         "message":"No Questions found",
         "statusCode":"200"
      })
   for i in existingQuestions:
      i.Sequence -= 1
   
   db.session.delete(existingQuestion)
   db.session.commit()
   return make_response(QTSchema.jsonify(existingQuestion),200)
@app.route('/add/assignment/', methods = ['POST'])
def addAssignment():
   data = request.get_json()
   AssignmentID = data['AssignmentID']
   CourseID = data['CourseID']
   TemplateID = data['TemplateID']
   TaskName = data['TaskName']
   Explaination = data['Explaination']
   Weightage = data['Weightage']
   GroupSize = data['GroupSize']
   SubmissionDate = datetime.strptime(data['SubmissionDate'], "%m/%d/%Y").date()
   PeerReviewDate = datetime.strptime(data['PeerReviewDate'], "%m/%d/%Y").date()
   SubmissionEndDate = datetime.strptime(data['SubmissionEndDate'], "%m/%d/%Y").date()
   PeerReviewEndDate = datetime.strptime(data['PeerReviewEndDate'], "%m/%d/%Y").date()
   if int(GroupSize) > 0 :
      allStudents = StudentCourse.query.filter(StudentCourse.CourseID == CourseID).all()
      # print(len(allStudents))
      c = 0
      g_size = int(GroupSize)
      groupkey = 0
      while len(allStudents) > 0 :
         if c==g_size :
            c = 0
         if c==0:
            print("New group formed")
            stud = random.choice(allStudents)
            print(stud.StudentID)
            gp = GroupWork(AssignmentID=AssignmentID,UserID=stud.StudentID)
            db.session.add(gp)
            db.session.commit()
            groupkey = gp.ID
            gp.updateID(GroupID=groupkey)
            db.session.add(gp)
            db.session.commit()
            newAssignment = Assignment(AssignmentID=AssignmentID,CourseID=CourseID,TemplateID=TemplateID,TaskName=TaskName,Explaination=Explaination,Weightage=Weightage,SubmissionDate=SubmissionDate,PeerReviewDate=PeerReviewDate,GroupSubmission=groupkey,GroupSize=int(GroupSize),SubmissionEndDate=SubmissionEndDate,PeerReviewEndDate=PeerReviewEndDate)
            db.session.add(newAssignment)  
         else :
            stud = random.choice(allStudents)
            gp = GroupWork(AssignmentID=AssignmentID,GroupID=groupkey,UserID=stud.StudentID) 
            db.session.add(gp)
            db.session.commit()
         allStudents.remove(stud)
         c += 1
      
      
   else :
      newAssignment = Assignment(AssignmentID=AssignmentID,CourseID=CourseID,TemplateID=TemplateID,TaskName=TaskName,Explaination=Explaination,Weightage=Weightage,SubmissionDate=SubmissionDate,PeerReviewDate=PeerReviewDate,SubmissionEndDate=SubmissionEndDate,PeerReviewEndDate=PeerReviewEndDate) 
   allCourses = Course.query.filter(Course.ID == CourseID).all()
   for i in allCourses:
      i.yesAssignment()
      db.session.add(i)
   db.session.add(newAssignment)
   db.session.commit()
   return make_response(assSchema.jsonify(newAssignment),200)

@app.route('/get/assignments/', methods = ['GET'])
def getAssignments():
   assignments = Assignment.query.group_by(Assignment.AssignmentID).all()
   return make_response(assSchema_.jsonify(assignments),200)   


@app.route('/get/assignment/<ass_id>', methods = ['GET'])
def getAssignment(ass_id):
   assignment = Assignment.query.filter(Assignment.ID == ass_id).first()
   if assignment is None :
      return make_response({
         "message" : "No Assignment found" ,
         "statusCode": "403"
      })
   return make_response(assSchema.jsonify(assignment),200) 

@app.route('/get/course/assignment/<course_id>', methods = ['GET'])
def getAssignmentByCourseId(course_id):
   assignment = Assignment.query.filter(Assignment.CourseID == course_id).group_by(Assignment.AssignmentID).all()
   if assignment is None :
      return make_response({
         "message" : "No Assignment found" ,
         "statusCode": "403"
      })
   return make_response(assSchema_.jsonify(assignment),200)    

@app.route('/get/course/assignment/<course_id>/<user_id>', methods = ['GET'])
def getGroupAssignmentByCourseId(course_id,user_id):
   assignment = Assignment.query.filter(Assignment.CourseID == course_id).all()
   result = []
   for ass in assignment :
     g_id = ass.GroupSubmission
     if g_id is None :
      result.append(ass)
      continue
     gp = GroupWork.query.filter(GroupWork.GroupID == g_id, GroupWork.UserID == user_id, GroupWork.AssignmentID == ass.AssignmentID).first()
     if gp is not None :
      result.append(ass)
   return make_response(assSchema_.jsonify(result),200)   

@app.route('/put/assignment/<ass_id>', methods = ['PUT'])
def updateAssignment(ass_id):
   assignment = Assignment.query.filter(Assignment.ID == ass_id).first()
   if assignment is None :
      return make_response({
         "message" : "No Assignment found" ,
         "statusCode": "403"
      })
   data = request.get_json()
   CourseID = data['CourseID']
   TemplateID = data['TemplateID']
   TaskName = data['TaskName']
   Explaination = data['Explaination']
   Weightage = data['Weightage']
   SubmissionDate = datetime.strptime(data['SubmissionDate'], "%m/%d/%Y").date()
   PeerReviewDate = datetime.strptime(data['PeerReviewDate'], "%m/%d/%Y").date()
   SubmissionEndDate = datetime.strptime(data['SubmissionEndDate'], "%m/%d/%Y").date()
   PeerReviewEndDate = datetime.strptime(data['PeerReviewEndDate'], "%m/%d/%Y").date()
   assignment.updateAssignment(CourseID,TemplateID,TaskName,SubmissionDate,PeerReviewDate,Explaination,Weightage,SubmissionEndDate,PeerReviewEndDate)  
   db.session.add(assignment)
   db.session.commit() 
   return make_response(assSchema.jsonify(assignment),200)  

@app.route('/delete/assignment/<ID>', methods = ['DELETE'])
def deleteAssignment(ID):
   existingAssignment = Assignment.query.filter(Assignment.AssignmentID == ID).all() 
   for d in existingAssignment :
      db.session.delete(d)
   db.session.commit()
   return make_response(assSchema.jsonify(existingAssignment),200)     

# Get and post for submissions



# Get Enrolled Courses
@app.route('/get/enrolledCourses/<student_id>', methods = ['GET'])
def enrolledCourses(student_id):
   enrolledCourses = StudentCourse.query.filter(StudentCourse.StudentID == student_id).all()
   return make_response(studentcourseSchema_.jsonify(enrolledCourses),200)  


@app.route('/get/questionare/<assignment_id>', methods = ['GET'])
def getQuestionare(assignment_id):
   assignment = Assignment.query.filter(Assignment.ID == assignment_id).first()
   if assignment is None :
      return make_response({
         "message":"No Assignments found",
         "errorCode": "404"
      })
   templateID = assignment.TemplateID
   print(templateID)  
   template = QuestionareTemplate.query.filter(QuestionareTemplate.ID == templateID).first() 
   if template is None :
      return make_response({
         "message":"No Templates found",
         "errorCode": "404"
      })
   questions = Questionare.query.filter(Questionare.TemplateID == templateID).all()
   print(questions)
   return make_response(quSchema_.jsonify(questions),200)  




def getStudentID(ID):
   user = User.query.filter(User.ID == ID).first()
   email = user.EmailAddress
   emails = email.split("@")
   return emails[0]

#  ID = db.Column('ID', db.Integer, primary_key = True)
#    GroupID = db.Column(db.Integer, db.ForeignKey('GroupWork.GroupID'))
#    StudentID = db.Column(db.Integer , db.ForeignKey('questionaretemplate.ID'))
#    AssignmentID = db.Column(db.Integer , db.ForeignKey('assignment.AssignmentID'))
#    FileName = db.Column(db.String)
#    FileSubmission = db.Column(db.LargeBinary)
#    SubmissionDate = db.Column(db.DateTime)
#    isMarked = db.Column(db.Boolean)
def getOutcome(res):
   marks = 0
   feedback = ""
   resultType = True
   for i in res :
      if i.Answer.isnumeric() :
         marks += int(i.Answer)
      else :
         feedback += i.Sequence + ') ' +i.Answer + ','
         resultType = False

   if resultType : 
      return marks/len(res);  
   return feedback

def getReviewID(res):
   return getStudentID(res[0].reviewerStudentID)

class DownloadSchema(ma.Schema):
    class Meta:
        fields = ("SubmissionStudentID","FileName", "SubmissionDate","AssignmentID","PeerReview","ReviewedStudentID","PeerReviewStudentIDS","SubmissionGroupStudents","Rating")

downSchema = DownloadSchema()
downSchema_ = DownloadSchema(many=True)    
@app.route('/get/results/<assignment_id>', methods = ['GET'])
def getResults(assignment_id):
   result = []
   subs = Submission.query.filter(Submission.AssignmentID == assignment_id).all()
   if subs is None :
      return make_response({
         "message":"No Submissions found",
         "errorCode": "404"
      })
   answer = {}  
   for i in subs :
      answer["SubmissionStudentID"] = getStudentID(i.StudentID)
      answer["FileName"] = i.FileName
      answer["SubmissionDate"] = i.SubmissionDate
      answer["AssignmentID"] = assignment_id
      submissionID = i.ID
      peerResults = PeerReview.query.filter(PeerReview.SubmissionID == submissionID).all()
      if len(peerResults) == 0:
         continue
      answer["PeerReview"] = getOutcome(peerResults)
      answer["ReviewedStudentID"] = getReviewID(peerResults)
      print("Submission group ids")
      print(i.GroupID)
      if i.GroupID is not 0 :
         users = GroupWork.query.filter(GroupWork.GroupID == i.GroupID, GroupWork.AssignmentID == assignment_id).all()
         groupUsers = ""
         for u in users :
            groupUsers += getStudentID(u.UserID) +' ,'
         answer["SubmissionGroupStudents"] = groupUsers
         answer["AssignmentType"] = "Group"
      else :
         answer["AssignmentType"] = "Individual"
      
      PeerUsers = ""
      if peerResults[0].GroupID is not 0 :
         g_id = peerResults[0].GroupID 
         print("Peer reviewed ID is ")
         print(g_id)
         users = GroupWork.query.filter(GroupWork.GroupID == g_id, GroupWork.AssignmentID == assignment_id).all()
         print(users)
         for u in users :
            PeerUsers += getStudentID(u.UserID) +' ,'
         answer["PeerReviewStudentIDS"] = PeerUsers
      # print(answer)
      result.append(answer)
      answer = {}
   return make_response(downSchema_.jsonify(result),200)  


@app.route('/get/reviews/<assignment_id>/<student_id>', methods = ['GET'])
def getPeerReviews(assignment_id,student_id):
   sub = Submission.query.filter(Submission.AssignmentID == assignment_id, Submission.StudentID == student_id).first()
   if sub.GroupID is not 0 :
      gps = GroupWork.query.filter(GroupWork.AssignmentID == assignment_id , GroupWork.GroupID == sub.GroupID).all()
      for i in gps :
         res = PeerReview.query.filter(PeerReview.AssignmentID == assignment_id, PeerReview.submissionStudentID == i.UserID).all()
         print(res)
         if len(res) is not 0 :
            break
      return make_response(peerSchema_.jsonify(res),200)
   else :
      res = PeerReview.query.filter(PeerReview.AssignmentID == assignment_id,
                           PeerReview.submissionStudentID == student_id).all()

      return make_response(peerSchema_.jsonify(res),200)
    

@app.route('/get/results/<assignment_id>/<student_id>', methods = ['GET'])
def getPeerResults(assignment_id,student_id):
   res = PeerReview.query.filter(PeerReview.AssignmentID == assignment_id,
                           PeerReview.reviewerStudentID == student_id).all()

   if len(res) >0 :
      print(len(res))
      return make_response(peerSchema_.jsonify(res),200)
   
   return make_response({
      "message" : 1
   },200)

    















if __name__ == '__main__':
   db.create_all()
   # host='0.0.0.0', port=88,debug=True
   app.run(host='0.0.0.0', port=82,debug=True)

