from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask import Flask,flash,redirect
from flask import jsonify
from flask import request
import json
from dataclasses import dataclass
from json import dumps, loads, JSONEncoder, JSONDecoder
import dataclasses, json
from flask_marshmallow import Marshmallow

app = Flask(__name__) 
app.secret_key = "secretkey"
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///users.sqllite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db = SQLAlchemy(app)
ma = Marshmallow(app)
# Defines the classes for database tables, columns and their value types

# from myride import db,login_manager
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin
from datetime import datetime
import random
import enum


class EnhancedJSONEncoder(json.JSONEncoder):
        def default(self, o):
            if dataclasses.is_dataclass(o):
                return dataclasses.asdict(o)
            return super().default(o)


class UserType(enum.Enum):
    NORMAL = "Normal User"
    OPERATOR = "Operator"
    MANAGER = "Manager"



class BikeStatus(enum.Enum):
    YES = "Available"
    NO = "Not Available"
    REPAIR = "In repair"
    DISABLED = "No longer in service"

class LocationNames(enum.Enum):
    HILLHEAD = "Hillhead, Glasgow"
    Bucchannan = "Bucchannan, Glasgow"
    Kelvinbridge = "Kelvinbridge, Glasgow"
    Cowcaddens = "Cowcaddens, Glasgow"


class Pay_status(enum.Enum):
    YES = "Paid"
    NO = "Not Paid"

class Repair_Status(enum.Enum):
    YES = "Repaired"
    NO = "Not Repaired"

class CurrentStatus(enum.Enum):
    YES = "Ride On Going"
    NO = "Ride Ended"




#=========================================#

# @dataclass.dataclass
# User Class for the table users which contains all the user details
class User_Details(db.Model,UserMixin):
    __tablename__ = 'User_Details' # Table name to be mentioned in the database

    # Attributes / Database Columns
    id = db.Column(db.Integer,primary_key=True)

    first_name = db.Column(db.String(16))
    last_name = db.Column(db.String(16))


    contact_number = db.Column(db.Integer)
    email_id = db.Column(db.String(128),unique=True,index=True)
    password1 = db.Column(db.String(128))
    # city = db.Column(db.Enum('GLASGOW'))
    user_type = db.Column(db.String(128)) # Whether a normal user or an employee such as operator or manager
    account_balance = db.Column(db.Float, default=0)



    # relationship with other classes/ database tables
    # rides = db.relationship('Transaction',backref='User_Details',lazy=True)
    # login_log = db.relationship('LoginLog',backref='User_Details',lazy=True)
    # Bike_usage_history = db.relationship('Bike_usage_history',backref='User_Details',lazy=True)
    # reviews = db.relationship('Review',backref='User_Details',lazy=True)
    # repairs = db.relationship('Repair',backref='User_Details',lazy=True)

    # For creating a new user object / table record
    def init(self,first_name, last_name, contact_number, email_id,password,  user_type,account_balance):
        self.first_name = first_name
        self.last_name = last_name

        self.contact_number = contact_number

        self.email_id = email_id.lower()
        self.password1 = generate_password_hash(password)
        self.user_type = user_type
        self.account_balance = account_balance
        
    # For checking the password used while user logs in
    def check_password(self,password):
        return check_password_hash(self.password_hash,password)
    # For adding/deducting balance to/from the wallet
    def add_account_balance(self, balance):
        self.account_balance += balance
    def deduct_account_balance(self, balance):
        self.account_balance -= balance

    def repr(self):
        return "Name {self.first_name} {self.last_name}"
   

class UserSchema(ma.Schema):
    class Meta:
        fields = ('first_name', 'last_name', 'contact_number','email_id', 'password1','user_type','account_balance')


user_schema = UserSchema()
users_schema = UserSchema(many=True)

# db.create_all()




# Transaction Class for the table transactions which contains all the payment records
# class Transaction(db.Model):
#     tablename = 'Transaction' # Table name to be mentioned in the database

#     # Attributes / Database Columns
#     id = db.Column(db.Integer,primary_key=True)
#     tran_id = db.Column(db.Integer,unique=True)
#     user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False) #Linked to users table

#     cc_number = db.Column(db.String(16))
#     amount = db.Column(db.Float)
#     tran_time = db.Column(db.DateTime)
#     Booking_id = db.Column(db.String(64),db.ForeignKey('Bike_usage_history.bike_ride_id'),unique=True) #Linked to ridelogs table
#     pay_status = db.Column(db.Enum(Pay_status)) # YES, NO

#     # For creating a new pending payment object / table record
#     def init(self, user_id, amount, cc_number,Booking_id, tran_time,pay_status):
#         self.user_id = user_id
#         self.cc_number = cc_number
#         self.amount = amount
#         self.tran_id = str(user_id)
#         self.Booking_id = Booking_id
#         self.pay_status = pay_status
#         self.tran_time = tran_time
#     # For updating the payment details
#     def update_payment(self, cc_number=''):
#         self.cc_number = cc_number
#         self.pay_status = 'YES'
#         self.time = datetime.utcnow()
# class TransactionSchema(ma.Schema):
#     class Meta:
#         fields = ('tran_id', 'user_id', 'cc_number','email_id', 'amount','tran_time','Booking_id','pay_status')


# user_schema = TransactionSchema()
# users_schema = TransactionSchema(many=True)

# # Topup Class for the table topup_logs which contains all the wallet topup records
# class Payment_history(db.Model):
#     tablename = 'Payment_history' # Table name to be mentioned in the database

#     # Attributes / Database Columns
#     id = db.Column(db.Integer,primary_key=True)
#     tran_id = db.Column(db.String(64),unique=True)
#     user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False) #Linked to users table
#     cc_number = db.Column(db.String(16))
#     balance = db.Column(db.Float)


#     # For creating a new wallet top up object / table record
#     def init(self, user_id, cc_number, balance):
#         self.user_id = user_id
#         self.cc_number = cc_number
#         self.balance = balance


# class User_history(db.Model):
#     tablename = 'User_history' # Table name to be mentioned in the database

#     # Attributes / Database Columns
#     id = db.Column(db.Integer,primary_key=True)

#     user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False) #Linked to users table
#     user_type = db.Column(db.Enum(UserType))
#     login_time =  db.Column(db.DateTime)


#     # For creating a new wallet top up object / table record
#     def init(self, user_id,user_type,login_time):
#         self.user_id = user_id
#         self.user_type = user_type
#         self.login_time = login_time


class Bike_usage_history(db.Model):
    tablename = 'Bike_usage_history' # Table name to be mentioned in the database

    # Attributes / Database Columns
    id = db.Column(db.Integer, primary_key=True)
    bike_ride_id = db.Column(db.String(64),unique=True)
    user_id = db.Column(db.Integer,db.ForeignKey('User_Details.id'),nullable=False) #Linked to users table
    start_location = db.Column(db.String(64)) # HILLHEAD, PARTICK, FINNIESTON, GOVAN, LAURIESTON
    end_location = db.Column(db.String(64))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)


    # relationship with other classes/ database tables
    # transaction = db.relationship('Transaction',backref='ride',lazy=True)

    # For creating a new ride log object / table record
    def init(self,user_id,start_location):
        self.user_id = user_id
        self.start_location = start_location
        self.start_time = datetime.utcnow()
        self.bike_ride_id = str(user_id)  + str(self.start_time)
        print(self.bike_ride_id, self.start_time)
 
    # Get the duration of the ride
    def get_minutes(self, end_time):
        time_delta = (end_time - self.start_time)
        total_seconds = time_delta.total_seconds()
        return 1 + int(total_seconds/60)
    # Update the ride details at end of the ride
    def end_ride(self, end_location):
        self.end_location = end_location
        self.end_time = datetime.utcnow()
        self.current = 'NO'

class Bike_usage_history_Schema(ma.Schema):
    class Meta:
        fields = ('bike_ride_id', 'user_id', 'start_location','end_location', 'start_time','end_time')


Bike_usage_history_schema = Bike_usage_history_Schema()
Bike_usages_history_schema = Bike_usage_history_Schema(many=True)
db.create_all()
# class station(db.Model):
#     tablename = 'station' # Table name to be mentioned in the database

#     # Attributes / Database Columns
#     id = db.Column(db.Integer, primary_key=True)
#     station_id = db.Column(db.Integer, unique=True,index=True)
#     pin = db.Column(db.Integer)

#     location = db.Column(db.Enum(LocationNames)) # HILLHEAD, PARTICK, FINNIESTON, GOVAN, LAURIESTON



#     # For creating a new bike object / table record
#     def init(self, station_id, pin, location):
#         self.station_id = station_id
#         self.pin = random.randint(1000,9999)
 
#         self.location = location
# # BikeInfo Class for the table bike_info which contains all the bike records
class bike_info(db.Model):
    tablename = 'bike_info' # Table name to be mentioned in the database

    # Attributes / Database Columns
    id = db.Column(db.Integer, primary_key=True)
    bike_id = db.Column(db.Integer, unique=True,index=True)
    bike_pin = db.Column(db.Integer)
    bike_status = db.Column(db.String(64)) # YES, NO, REPAIR, DISABLED
    left_location = db.Column(db.String(64)) # HILLHEAD, PARTICK, FINNIESTON, GOVAN, LAURIESTON

    # relationship with other classes/ database tables
    Bike_usage_history = db.relationship('Bike_usage_history',backref='bike',lazy=True)

    # For creating a new bike object / table record
    def init(self, bike_id, bike_status, left_location):
        self.bike_id = bike_id
        self.bike_pin = random.randint(1000,9999)
        self.bike_status = bike_status
        self.left_location = left_location
    # To check if a bike is available
    def check_available(self):
        if self.bike_status == 'YES':
            return True
        else:
            return False
    # To ruturn a bike after a ride
    def place_back(self, left_location):
        self.bike_pin = random.randint(1000,9999) # Change the bike pin to new random number
        self.left_location = left_location # Update the location to where it is being returned
        self.status = 'YES' # Update the status to available







# # Repair Class for the table repairs which contains all the user reports and operator repair records
# class Repair(db.Model):
#     tablename = 'repairs' # Table name to be mentioned in the database

#     # Attributes / Database Columns
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False) #Linked to users table
#     bike_id = db.Column(db.Integer, db.ForeignKey('bike_info.bike_id'),nullable=False) #Linked to biekinfo table
#     reported_tmp = db.Column(db.DateTime)
#     description = db.Column(db.Text)
 
#     status =  db.Column(db.Enum(Repair_Status)) # YES, NO
   
#     repaired_tmp = db.Column(db.DateTime)

#     comment = db.Column(db.Text)

#     # For creating a new defective bike user report object / table record
#     def init(self, user_id, bike_id, description, urgency):
#         self.user_id = user_id
#         self.bike_id = bike_id
#         self.description = description
#         self.urgency = urgency
#         self.repaired_tmp = datetime.utcnow()
#         self.repair_status = 'NO'
#     # For updating the records with operator repair details
#     def repaired(self, comment):
      
#         self.comment = comment
#         self.repair_status = 'YES'
#         self.repaired_at = datetime.utcnow()

#  self.user_id = user_id
#         self.cc_number = cc_number
#         self.amount = amount
#         self.tran_id = str(user_id)
#         self.Booking_id = Booking_id
#         self.pay_status = pay_status
#         self.tran_time = tran_time

#  id = db.Column(db.Integer,primary_key=True)
#     tran_id = db.Column(db.Integer,unique=True)
#     user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False) #Linked to users table

#     cc_number = db.Column(db.String(16))
#     amount = db.Column(db.Float)
#     tran_time = db.Column(db.DateTime)
#     Booking_id = db.Column(db.String(64),db.ForeignKey('Bike_usage_history.bike_ride_id'),unique=True) #Linked to ridelogs table






# user_id,start_location,start_time
@app.route('/Bike_usage_history', methods=['POST'])
def Bike_use_history():   
   start_location = request.json["start_location"]
   user_id = request.json["user_id"]
   history = Bike_usage_history(start_location=start_location,
                    user_id=user_id) 
   print(history.start_time)
   db.session.add(history)
   db.session.commit()
   
   return Bike_usage_history_schema.jsonify(history)   
@app.route('/newTrans', methods=['POST'])
def newTrans():
    
   tran_id = request.json["tran_id"]
   user_id = request.json["user_id"]
   cc_number = request.json["cc_number"]
   tran_time = request.json["tran_time"]
   password = request.json["password1"]
   user_type = request.json["user_type"]
   amount = request.json["amount"]
#    db.session.add(user)
   db.session.commit()
   
   return user_schema.jsonify("hello") 
 
@app.route('/addUser', methods=['POST'])
def check():
    
   first_name = request.json["first_name"]
   last_name = request.json["last_name"]
   contact_number = request.json["contact_number"]
   email = request.json["email_id"]
   password = request.json["password1"]
   user_type = request.json["user_type"]
   account_balance = request.json["account_balance"]
   user = User_Details(first_name=first_name,
                    last_name=last_name,
                    contact_number=contact_number,
                    email_id=email,
                    password1=password,
                    # city=city,
                    user_type=user_type,
                    account_balance=account_balance) 
   db.session.add(user)
   db.session.commit()
   
   return user_schema.jsonify(user)
  


@app.route('/getUsers')
def hello_admin():
    l = db.session.query(User_Details).all()
    

    return(users_schema.jsonify(l))

   
