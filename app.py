from flask import Flask,render_template,request,flash,redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user,UserMixin,logout_user
from sqlalchemy.sql import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SECRET_KEY'] = "qwertyuiopasdfghjklzxcvbnm"
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    db.relationship('Note')
    def __repr__(self):
        return '<User %r>' % self.username

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['GET', 'POST'])
def  register():
    if request.method == 'POST':
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        # print(fname, lname, email, username, password)
        user= User(first_name=fname, last_name=lname,username=username, password=password,email=email)
        db.session.add(user)
        db.session.commit()
        flash(f'Welcome to Free Ink {username}.', 'success')
        return redirect('/login')
    return render_template('register.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')
        user =User.query.filter_by(username=username).first()
        if user and password==user.password:
            login_user(user, remember=True)
            return redirect('/')
        else:
            flash(f'No user has registered with "{username}"', 'danger')
            return redirect('/login')
    return render_template("login.html")

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')

@app.route('/')
def home():
    return render_template("index.html")

@app.route("/user")
def user():
    return render_template('user.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/danger')
def danger():
    return render_template('danger.html')

@app.route("/delete", methods=['GET', 'POST'])
def delete():
    if request.method == 'POST':
        username = request.form.get("username")
        passwordAttempt = request.form.get("password")
        user =User.query.filter_by(username=username).first()
        password = user.password
        if passwordAttempt == password:
            db.session.delete(user)
            db.session.commit()
            flash("Your account has been deleted. Thank you for using our app.", "success")
            return redirect("/login")
        else:
            flash("Invalid Password", "danger")
    return render_template('delete.html')

if __name__ =="__main__":
    db.create_all()
    app.run(debug=True)