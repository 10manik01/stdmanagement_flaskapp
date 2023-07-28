from flask import Flask,redirect,render_template,request,session,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_login import logout_user,login_manager,login_user,LoginManager
from flask_login import login_required,current_user


local_server=True
app=Flask(__name__)
app.secret_key="syangtan"

login_manager=LoginManager(app)
login_manager.login_view='home'

@login_manager.user_loader
def load_user(user_id):
        return Studenttable.query.get(user_id)

# app.config['SQLALCHEMY_DATABASE_URI']='mysql://username:password@localhost/databasename'
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/student'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)

class Studenttable(UserMixin,db.Model):
        roll=db.Column(db.String(15),primary_key=True)
        name=db.Column(db.String(50),nullable=False)
        email=db.Column(db.String(100),unique=True,nullable=False)
        semester=db.Column(db.String(4),nullable=False)
        address=db.Column(db.String(100),nullable=False)

        def get_id(self):
                print("get_id method called!")
                return str(self.roll)

@app.route("/",methods=['POST','GET'])
def home():
        if request.method =="POST":
                roll=request.form.get('roll')
                email=request.form.get('email')
                existing_studentemail=Studenttable.query.filter_by(email=email).first()
                # existing_studentroll=Studenttable.query.filter_by(roll=roll).first()


                if existing_studentemail and  roll==existing_studentemail.roll:
                        login_user(existing_studentemail)
                        flash("Login successful!","primary")
                        return redirect(url_for('profile'))
                elif existing_studentemail and roll!=existing_studentemail.roll:
                        flash("College roll mismatched!","danger")
                        return render_template('index.html')
                # elif  existing_studentemail==False:
                else:
                        flash("THE STUDENT HAS NOT SIGNED UP YET!","warning")
                        return render_template('index.html')


        return render_template("index.html")

@app.route("/signup", methods=['POST','GET'])
def signup():
        if request.method =="POST":
                roll=request.form.get('roll')
                name=request.form.get('name')
                email=request.form.get('email')
                semester=request.form.get('semester')
                address=request.form.get('address')
                existing_email=Studenttable.query.filter_by(email=email).first()
                existing_roll=Studenttable.query.filter_by(roll=roll).first()
                if existing_email:
                        flash("EMAIL ALREADY EXISTS!","warning")
                        return render_template('signup.html')
                if existing_roll:
                        flash("COLLEGE ROLL ALREADY EXISTS!","warning")
                        return render_template('signup.html')
                # new_user=db.engine.execute(f"INSERT INTO 'studenttable' ('roll','name','email','semester','address') VALUES ('{roll}','{name}','{email}',{semester},'{address}')")
                # return render_template("index.html")
                new_student = Studenttable(roll=roll, name=name, email=email, semester=semester, address=address)
                db.session.add(new_student)
                db.session.commit()
                flash("SIGN UP SUCCESSFUL! PLEASE LOGIN.","success")
                return render_template("index.html")
                
        return render_template("signup.html")

@app.route("/edit/<string:roll>",methods=['POST','GET'])
@login_required
def edit(roll):
         posts=Studenttable.query.filter_by(roll=roll).first()
         if request.method =="POST":
                name=request.form.get('name')
                email=request.form.get('email')
                semester=request.form.get('semester')
                address=request.form.get('address')
                
                db.session.execute(f"UPDATE studenttable SET `roll` = '{roll}', `name` = '{name}', `email` = '{email}', `address` = '{address}' WHERE studenttable.roll = '{roll}'")

                db.session.commit()
                flash("YOUR DATA IS UPDATED.","success")
                return redirect(url_for('profile'))
        
         return render_template("edit.html",posts=posts)

@app.route("/delete/<string:roll>",methods=['POST','GET'])
def delete(roll):
        db.session.execute(f"DELETE FROM studenttable WHERE studenttable.roll = '{roll}'")
        db.session.commit()
        flash("DELETED SUCCESSFULLY!","danger")
        return redirect(url_for('home'))

@app.route("/profile")
def profile():
        if not current_user.is_authenticated:
                return redirect(url_for('home'))
        else:
                # em = current_user.email
                # query = db.session.execute(f"SELECT * FROM studenttable WHERE email='{em}'")

                # user_data=query.fetchall()

                # return render_template('profile.html', name=current_user.name, user_data=user_data)
                return render_template('profile.html', user=current_user)
                

@app.route("/logout")
@login_required
def logout():
        logout_user()
        flash("LOGOUT SUCCESSFUL!","warning")
        return redirect(url_for('home'))

@app.route("/search", methods=['POST', 'GET'])
def search():
    searched = request.form.get('search')
    user_data = None

    roll = Studenttable.query.filter_by(roll=searched).first()
    if roll:
        query = db.session.execute("SELECT * FROM studenttable WHERE roll=:roll", {"roll": roll.roll})
        user_data = query.fetchall()

    if not user_data:
        name = Studenttable.query.filter_by(name=searched).first()
        if name:
            query = db.session.execute("SELECT * FROM studenttable WHERE name=:name", {"name": name.name})
            user_data = query.fetchall()

    if not user_data:
        city = Studenttable.query.filter_by(address=searched).first()
        if city:
            query = db.session.execute("SELECT * FROM studenttable WHERE address=:address", {"address": city.address})
            user_data = query.fetchall()

    if user_data:
        return render_template('search.html', user_data=user_data)
    
    flash("USER NOT FOUND","danger")
    return redirect(url_for('home'))


app.run(debug=True)