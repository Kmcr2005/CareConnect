from flask import Flask, render_template, redirect, url_for,request,session,flash

from model import db, Admin, Patient, Doctor, Department,Appointment,Treatment

from datetime import datetime, timedelta

app= Flask(__name__)
app. config["SECRET_KEY"] = "MyKey"
app. config ["SQLALCHEMY_DATABASE_URI" ]= "sqlite:///HMS.db"
app. config ["SQLALCHEMY_TRACK _MODIFICATIONS"] = False
db.init_app(app)

with app.app_context():
    db.create_all()
    if not Admin.query.filter_by(username="Admin"). first():
        admin = Admin(
        aid = 1,
        username="Admin",
        password = "Admin123"
        )
        db. session.add (admin) 
        db.session.commit()
        print ("ADMIN CREATED!")
    else:
        print ("ADMIN EXISTS!")
@app.route('/', methods = ['POST', 'GET'])
def index():
    if request.method == "POST":
        
        users = Patient.query.all()    
        for user in users:
            if request.form["username"] == user.username and request.form["password"] == user.password and user.blacklist==False:
                session['user_id'] = user.pid
                session['role'] = "Patient"
                return redirect(url_for('patientdash', pid=user.pid))
        docs=Doctor.query.all()
        for user in docs:
            if request.form["username"] == user.username and request.form["password"] == user.password and user.blacklist==False:
                session['user_id'] = user.did
                session['role'] = "Doctor"
                return redirect(url_for('docdash', did=user.did))


        return render_template("index.html", again = True)        

    return render_template("index.html", again = False)
@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == "POST":
        users = Patient.query.all()

        for user in users:
            if user.username == request.form["username"]:
                return render_template("register.html", again = True)
        
        db.session.add(Patient(username = request.form["username"], password = request.form["password"], fname = request.form["fname"].lower(), lname = request.form["lname"].lower(),age=int(request.form["age"]),height=int(request.form["height"]),weight=int(request.form["weight"])))
        db.session.commit()

        return render_template("index.html")
    return render_template("register.html", again = False)
@app.route('/adminlogin',methods = ['GET', 'POST'])
def adminlogin():
    if request.method == "POST":
    
        users = Admin.query.all()    
        for user in users:
            if request.form["username"] == user.username and request.form["password"] == user.password:
                session['user_id'] = user.aid
                session['role'] = "Admin"
                return redirect(url_for('admindash'))


        return render_template("adminlogin.html", again = True)        

    return render_template("adminlogin.html", again = False)
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role',None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))
@app.route('/admindash',methods = ['GET', 'POST'])
def admindash():
        if session.get('role')=="Admin":
            
            doctors = Doctor.query.all()
            patients = Patient.query.all()
            appointments = Appointment.query.filter_by(blocked=False,completed=False).all()
            departments=Department.query.all()
            search_query = request.args.get('search', '').lower()
            doctor_dict = {doc.did: f"{doc.fname} {doc.lname}" for doc in doctors}
            patient_dict = {pat.pid: f"{pat.fname} {pat.lname}" for pat in patients}
            
            doctor_matches = {}
            patient_matches = {}

            if search_query:
                for doc in doctors:
                    full_name = f"{doc.fname} {doc.lname}".lower()
                    if search_query in full_name:
                        doctor_matches[doc.did] = True

                for pat in patients:
                    full_name = f"{pat.fname} {pat.lname}".lower()
                    if search_query in full_name:
                        patient_matches[pat.pid] = True
            return render_template('admindash.html',doctors=doctors,patients=patients,appoinments=appointments,departments=departments,search_query=search_query,doctor_matches=doctor_matches,patient_matches=patient_matches,doctor_dict=doctor_dict,
            patient_dict=patient_dict)
        else:
            flash('Admin! Please log in..', 'danger')
            return redirect(url_for('adminlogin'))
@app.route('/toggle_blacklist/<int:did>', methods=['POST'])
def toggle_blacklist(did):
    if session.get('role')=="Admin":
        doc = Doctor.query.get(did)
        if not doc:
            return "Doctor not found", 404
        doc.blacklist = not doc.blacklist 
        db.session.commit()
        return redirect(request.referrer) 
    else:
        flash('Admin! Please log in..', 'danger')
        return redirect(url_for('adminlogin')) 
@app.route('/toggle_blacklist_patient/<int:pid>', methods=['POST'])
def toggle_blacklist_patient(pid):
    if session.get('role')=="Admin":
        patient = Patient.query.get(pid)
        if not patient:
            return "Doctor not found", 404
        patient.blacklist = not patient.blacklist 
        db.session.commit()
        return redirect(request.referrer)  
    else:
        flash('Admin! Please log in..', 'danger')
        return redirect(url_for('adminlogin')) 


@app.route('/doctorreg',methods = ['GET','POST'])
def doctorreg():
    if session.get('role')=="Admin":
       if request.method == "POST":
       
            users = Doctor.query.all()

            for user in users:
                if user.username == request.form["username"]:
                    return render_template("doctorreg.html", again = True)
            
            db.session.add(Doctor(username = request.form["username"], password = request.form["password"], fname = request.form["fname"].lower(), lname = request.form["lname"].lower(),exp=(request.form["exp"]),desc=(request.form["desc"]),deptid=(request.form["deptid"])))
            db.session.commit() 
            return redirect(url_for('admindash'))
       return render_template("doctorreg.html", again = False)
    else:
            flash('Admin! Please log in..', 'danger')
            return redirect(url_for('adminlogin'))

@app.route('/doctoredit/<int:did>',methods = ['GET','POST'])
def doctoredit(did):
    if session.get('role')=="Admin": 
        doctor = Doctor.query.get(did)

        if request.method == "POST":
            doctor.fname = request.form["fname"]
            doctor.lname = request.form["lname"]
            doctor.exp = request.form["exp"]
            doctor.desc = request.form["desc"]
            doctor.deptid = request.form["deptid"]
            doctor.password=request.form["password"]

            db.session.commit()


            return redirect(url_for('admindash'))

        return render_template("doctoredit.html", doctor=doctor)
    
    else:
            flash('Admin! Please log in..', 'danger')
            return redirect(url_for('adminlogin'))

@app.route('/doctordelete/<int:did>', methods=['POST','GET'])
def doctordelete(did):
    if session.get('role')=="Admin": 
        doctor = Doctor.query.get(did)
        if doctor:
            db.session.delete(doctor)
            db.session.commit()
            return redirect(url_for('admindash'))
        return "Doctor not found"   
    else:
        flash('Admin! Please log in..', 'danger')
        return redirect(url_for('adminlogin'))

@app.route('/patientedit/<int:pid>', methods=['GET', 'POST'])
def patientedit(pid):
    if session.get('role')=="Admin": 
        patient = Patient.query.get(pid)
    
        if request.method == "POST":
            patient.fname = request.form["fname"].lower()
            patient.lname = request.form["lname"].lower()
            patient.age = int(request.form["age"])
            patient.height = int(request.form["height"])
            patient.weight = int(request.form["weight"])
            patient.password = request.form["password"]

            db.session.commit()
            return redirect(url_for('admindash'))

        return render_template("patientedit.html", patient=patient)
    else:
        flash('Admin! Please log in..', 'danger')
        return redirect(url_for('adminlogin'))
@app.route('/patientremove/<int:pid>')
def patientremove(pid):
    if session.get('role')=="Admin": 
        patient = Patient.query.get_or_404(pid)
        db.session.delete(patient)
        db.session.commit()
        return redirect(url_for('admindash'))
    else:
        flash('Admin! Please log in..', 'danger')
        return redirect(url_for('adminlogin'))
@app.route('/deptremove/<int:deptid>')
def deptremove(deptid):
    if session.get('role')=="Admin": 
        depatrtment = Department.query.get_or_404(deptid)
        db.session.delete(depatrtment)
        db.session.commit()
        return redirect(url_for('admindash'))
    else:
        flash('Admin! Please log in..', 'danger')
        return redirect(url_for('adminlogin'))
@app.route('/deptedit/<int:deptid>', methods=['GET', 'POST'])
def deptedit(deptid):
    if session.get('role')=="Admin": 
        department = Department.query.get(deptid)
    
        if request.method == "POST":
            department.deptname = request.form["name"]
            department.desc = request.form["desc"]

            db.session.commit()
            return redirect(url_for('admindash'))

        return render_template("deptedit.html", department=department)
    else:
        flash('Admin! Please log in..', 'danger')
        return redirect(url_for('adminlogin'))
@app.route('/patientdash/<int:pid>')
def patientdash(pid):
        if session.get('role')=="Patient" and session.get('user_id')==pid: 
            patient=Patient.query.get(pid)
            departments=Department.query.all()
            appointments=Appointment.query.filter_by(pid=pid,completed=False).all()
            doctors = {d.did: d.fname for d in Doctor.query.all()}
            
            return render_template("patientdash.html", patient=patient,departments=departments,doctors=doctors,appointments=appointments)
        else:
            return redirect(url_for('index'))
    
@app.route("/cancel/<int:apid>", methods=["POST"])
def cancel_appointment(apid):
    ap = Appointment.query.get(apid)

    if not ap:
        return "Appointment not found", 404

    db.session.delete(ap)
    db.session.commit()
    if session.get('role')=="Patient" and session.get('user_id')==ap.pid: 
        return redirect(url_for('patientdash',pid=ap.pid))
    elif session.get('role')=="Doctor" and session.get('user_id')==ap.did: 
         return redirect(url_for('docdash',did=ap.did))
@app.route('/department/<int:pid>/<int:deptid>', methods=['GET', 'POST'])
def department(pid, deptid):
    if session.get('role')=="Patient" and session.get('user_id')==pid: 
        selected_did = request.args.get('did')

        department = Department.query.get(deptid)
        doctors = Doctor.query.filter_by(deptid=deptid,blacklist=False).all()
        patient = Patient.query.get(pid)

        dates = [(datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]

        appointments = None
        doctor = None
        blocked_slots = set()

        if selected_did:
            did_int = int(selected_did)

            doctor = Doctor.query.get(did_int)
            appointments = Appointment.query.filter_by(did=did_int, blocked=False).all()
            blocked = Appointment.query.filter_by(did=did_int).all()
            blocked_slots = {f"{b.date.strftime('%Y-%m-%d')}|{b.shift}" for b in blocked}

        return render_template(
            "department.html",
            doctors=doctors,
            department=department,
            patient=patient,
            doctor=doctor,
            appointments=appointments,
            blocked_slots=blocked_slots,
            dates=dates
        )
    else:
            return redirect(url_for('index'))

@app.route('/bookslot/<int:pid>/<int:deptid>/<int:did>', methods=['POST'])
def bookslot(pid, deptid, did):
    slot = request.form['slot']
    date, shift = slot.split("|")
    date_obj = datetime.strptime(date, '%Y-%m-%d').date()

    existing = Appointment.query.filter_by(did=did, date=date, shift=shift).first()
    if existing:
        return "Slot already booked or blocked!", 400

    new_slot = Appointment(
        did=did,
        pid=pid,
        date=date_obj,
        shift=shift,
        completed=False,
        blocked=False
    )

    db.session.add(new_slot)
    db.session.commit()

    return redirect(url_for("department", pid=pid, deptid=deptid, did=did))

@app.route('/adddepartment',methods = ['GET','POST'])
def adddepartment():
    if session.get('role')=="Admin":
       if request.method == "POST":
       
            users = Department.query.all()

            for user in users:
                if user.deptname== request.form["deptname"]:
                    return render_template("doctorreg.html", again = True)
            
            db.session.add(Department(deptname = request.form["deptname"], desc = request.form["desc"]))
            db.session.commit() 
            return redirect(url_for('admindash'))
       return render_template("adddepartment.html", again = False)
    else:
            flash('Admin! Please log in..', 'danger')
            return redirect(url_for('adminlogin'))
@app.route('/docdash/<int:did>',methods = ['GET','POST'])
def docdash(did):
    if session.get('role')=="Doctor" and session.get('user_id')==did: 
        dates = [(datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
        doc=Doctor.query.get(did)
        patients = Patient.query.all()
        appointments = Appointment.query.filter_by(did=did,blocked=False,completed=False).all()
        block = Appointment.query.filter_by(did=did).all()
        blocked=Appointment.query.filter_by(did=did,blocked=True).all()
        patient_dict = {pat.pid: f"{pat.fname} {pat.lname}" for pat in patients}

        blocked_slots = {f"{b.date.strftime('%Y-%m-%d')}|{b.shift}" for b in block}
        return render_template("docdash.html", doc=doc,patients=patients,appoinments=appointments,dates=dates,blocked_slots=blocked_slots,patient_dict=patient_dict,blocked=blocked)
    else:
            return redirect(url_for('index'))
@app.route("/completed/<int:apid>", methods=["POST"])
def completed(apid):
    ap = Appointment.query.get(apid)
    if session.get('role')=="Doctor" and session.get('user_id')==ap.did: 
        if not ap:
            return "Appointment not found", 404

        ap.completed=True
        db.session.commit()

        return redirect(url_for('docdash',did=ap.did))
    else:
            return redirect(url_for('index'))
@app.route('/blockslot/<int:did>', methods=['POST'])
def blockslot(did):
    slot = request.form['slot']
    date, shift = slot.split("|")
    date_obj = datetime.strptime(date, '%Y-%m-%d').date()

    existing = Appointment.query.filter_by(did=did, date=date, shift=shift).first()
    if existing:
        return "Slot already booked or blocked!", 400

    slot = Appointment(
        did=did,
        pid=None,         
        date=date_obj,
        shift=shift,
        completed=False,
        blocked=True      
    )

    db.session.add(slot)
    db.session.commit()
    return redirect(url_for("docdash", did=did))
@app.route('/patienthistory/<int:pid>', methods=['GET', 'POST'])
def patienthistory(pid):
    if session.get('role') in ["Admin","Doctor","Patient"] and session.get('user_id')==pid: 
        
        patient = Patient.query.get(pid)
        treatments=Treatment.query.filter_by(pid=pid).all()
        doctors = {d.did: d.fname for d in Doctor.query.all()}

        return render_template(
            "patienthistory.html",patient=patient,treatments=treatments,doctors=doctors)
    else:
            return redirect(url_for('index'))
@app.route('/treatment/<int:pid>/<int:did>',methods = ['GET','POST'])
def treatment(pid,did):
    if session.get('role')=="Doctor" and session.get('user_id')==did: 
        doctor = Doctor.query.get(did)
        patient=Patient.query.get(pid)
    
        if request.method == "POST":
                date_str = request.form['date']
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                db.session.add(Treatment(test = request.form["test"], diagnosis = request.form["diagnosis"], prescription = request.form["prescription"], pid = patient.pid,did=doctor.did,date=date_obj))
                db.session.commit() 
                return redirect(request.referrer)  

        return render_template("treatment.html",patient=patient,doctor=doctor)
    else:
            return redirect(url_for('index'))
@app.route('/ppatientedit/<int:pid>', methods=['GET', 'POST'])
def ppatientedit(pid):
    if session.get('role')=="Patient" and session.get('user_id')==pid: 
        patient = Patient.query.get(pid)

        if request.method == "POST":
            patient.fname = request.form["fname"].lower()
            patient.lname = request.form["lname"].lower()
            patient.age = int(request.form["age"])
            patient.height = int(request.form["height"])
            patient.weight = int(request.form["weight"])
            patient.password = request.form["password"]

            db.session.commit()
            return redirect(url_for('patientdash',pid=pid))
    else:
            return redirect(url_for('index'))

    return render_template("ppatientedit.html", patient=patient)
if __name__ =='__main__':
    app.run(debug=True)