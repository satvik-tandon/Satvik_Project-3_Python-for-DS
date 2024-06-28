from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import pickle
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
import MySQLdb.cursors
import bcrypt

app: Flask = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://satvik:satvik@localhost:3306/flaskApp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your secret key'
app.app_context().push()
db = SQLAlchemy(app)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'satvik'
app.config['MYSQL_PASSWORD'] = 'satvik'
app.config['MYSQL_DB'] = 'flaskApp'

mysql = MySQL(app)
model = pickle.load(open('model.pkl', 'rb'))


class loan_users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255))
    userpwd = db.Column(db.String(255))
    email = db.Column(db.String(255))

    def __init__(self, username, userpwd, email):
        self.username = username
        self.userpwd = userpwd
        self.email = email


db.create_all()


@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM loan_users WHERE username = % s', (username,))
        account = cursor.fetchone()
        if account:
            hashed_password = account['userpwd']
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                msg = 'Logged in successfully !'
                return render_template('predict.html', msg=msg)
            else:
                msg = 'Incorrect username / password !'
    return render_template('login.html', msg=msg)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO loan_users VALUES (NULL, % s, % s, % s)', (username, hashed_password, email,))
        mysql.connection.commit()
        msg = 'You have successfully registered !'
        return render_template('login.html', msg=msg)
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg=msg)


@app.route("/predict", methods=['POST'])
def predict():
    if request.method == 'POST':
        Gender = int(request.form['gender'])
        Married = int(request.form['married'])
        Dependents = float(request.form['dependents'])
        Education = int(request.form['education'])
        Self_Employed = int(request.form['self_employed'])
        Applicantincome = int(request.form['applicant_income'])
        Coapplicantincome = float(request.form['coapplicant_income'])
        Loan_Amount = float(request.form['loan_amount'])
        Loan_Term = float(request.form['loan_term'])
        Credit_History = int(request.form['credit_history'])
        Property_Area = int(request.form['property_area'])

        prediction = model.predict([[Gender, Married, Dependents, Education, Self_Employed, Applicantincome,Coapplicantincome, Loan_Amount, Loan_Term, Credit_History, Property_Area]])
        if prediction[0] >= 0.50:
            ptext = "Congrats!!! You are eligible for the Loan"
        else:
            ptext = "Sorry!!! Not eligible for the loan"


        return render_template('predict.html', prediction_text=ptext)  


if __name__ == '__main__':
    app.run(debug= False, host= '0.0.0.0', port= 5000)
