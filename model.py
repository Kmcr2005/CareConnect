from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#Admin class
class Admin(db.Model):
    __tablename__ = "admin"
    aid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

#Patient
class Patient(db.Model):
    __tablename__ = "Patient"
    pid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    fname = db.Column(db.String, nullable=False)
    lname = db.Column(db.String, nullable=True)
    age=db.Column(db.Integer,nullable=False)
    height=db.Column(db.Integer,nullable=True)
    weight=db.Column(db.Integer,nullable=True)
    blacklist = db.Column(db.Boolean, default=False)
#Doctor
class Doctor(db.Model):
    __tablename__ = "Doctor"
    did = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    fname = db.Column(db.String, nullable=False)
    lname = db.Column(db.String, nullable=True)
    exp=db.Column(db.Integer,nullable=False)
    desc=db.Column(db.String,nullable=False)
    deptid = db.Column(db.Integer,db.ForeignKey('Dept.deptid'),nullable=False)
    blacklist = db.Column(db.Boolean, default=False)

#Department
class Department(db.Model):
    __tablename__ = "Dept"
    deptid = db.Column(db.Integer, primary_key=True)
    deptname=db.Column(db.String, nullable=False)
    desc=db.Column(db.String,nullable=False)

#Appointment
class Appointment(db.Model):
    __tablename__ = "Appointment"
    apid = db.Column(db.Integer, primary_key=True)
    did = db.Column(db.Integer,db.ForeignKey('Doctor.did'),nullable=False)
    pid = db.Column(db.Integer,db.ForeignKey('Patient.pid'),nullable=True)
    date=db.Column(db.Date,nullable=False)
    shift=db.Column(db.String,nullable=False)
    completed=db.Column(db.Boolean, default=False)
    blocked = db.Column(db.Boolean, default=False)

#Treatment
class Treatment(db.Model):
    __tablename__ = "Treatment"
    tid = db.Column(db.Integer, primary_key=True)
    date=db.Column(db.Date,nullable=False)
    did = db.Column(db.Integer,db.ForeignKey('Doctor.did'),nullable=False)
    pid = db.Column(db.Integer,db.ForeignKey('Patient.pid'),nullable=False)
    test=db.Column(db.String,nullable=True)
    diagnosis=db.Column(db.String,nullable=True)
    prescription=db.Column(db.String,nullable=True)

