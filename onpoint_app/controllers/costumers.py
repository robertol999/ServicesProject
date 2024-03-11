from onpoint_app import app
from flask import render_template, redirect, session, request, flash
import random
import math
import smtplib
from .env import ADMINEMAIL
from .env import PASSWORD
from onpoint_app.models.costumer import Costumer
from onpoint_app.models.provider import Provider
from onpoint_app.models.job import Job
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

# Employee Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/loginPage')
def loginPage():
    if 'costumer_id' in session:
        return redirect('/dashboard')
    return render_template('loginClient.html')

@app.route('/login', methods=['POST'])
def login():
    if 'costumer_id' in session:
        return redirect('/dashboard')
    costumer = Costumer.get_costumer_by_email(request.form)
    if not costumer:
        flash('This email does not exist.', 'emailLogin')
        return redirect('/loginPage')
    if not bcrypt.check_password_hash(costumer['password'], request.form['password']):
        flash('Your password is wrong!', 'passwordLogin')
        return redirect('/loginPage')
    session['costumer_id'] = costumer['id']
    return redirect('/dashboard')

@app.route('/register', methods=['POST'])
def register():
    if 'costumer_id' in session:
        return redirect('/dashboard')
    
    if Costumer.get_costumer_by_email(request.form):
        flash('This email already exists. Try another one.', 'emailSignUp')
        return redirect('/loginPage')
    string = '0123456789'
    vCode = ""
    length = len(string)
    for i in range(8) :
        vCode += string[math.floor(random.random() * length)]
    verificationCode = vCode

    data = {
        'first_name': request.form['first_name'],
        'last_name': request.form['last_name'],
        'email': request.form['email'],
        'password': bcrypt.generate_password_hash(request.form['password']),
        'verification_code': verificationCode,
    }
    
    Costumer.create_costumer(data)
    
    LOGIN = ADMINEMAIL
    TOADDRS  = request.form['email']
    SENDER = ADMINEMAIL
    SUBJECT = 'Verify Your Email'
    msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n"
        % ((SENDER), "".join(TOADDRS), SUBJECT) )
    msg += f'Use this verification code to activate your account: {verificationCode}'
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.set_debuglevel(1)
    server.ehlo()
    server.starttls()
    server.login(LOGIN, PASSWORD)
    server.sendmail(SENDER, TOADDRS, msg)
    server.quit()
    
    costumer = Costumer.get_costumer_by_email(data)
    
    session['costumer_id'] = costumer['id']

    return redirect('/verify/email')

@app.route('/verify/email')
def verifyEmail():
    if 'costumer_id' not in session:
        return redirect('/')
    data = {
        'costumer_id': session['costumer_id']
    }
    costumer = Costumer.get_costumer_by_id(data)
    if costumer['is_verified'] == 1:
        return redirect('/dashboard')
    return render_template('verify.html', loggedCostumer = costumer)


@app.route('/activate/account', methods=['POST'])
def activateAccount():
    if 'costumer_id' not in session:
        return redirect('/')
    data = {
        'costumer_id': session['costumer_id']
    }
    costumer = Costumer.get_costumer_by_id(data)
    if costumer['is_verified'] == 1:
        return redirect('/dashboard')
    
    if not request.form['verification_code']:
        flash('Verification Code is required', 'wrongCode')
        return redirect(request.referrer)
    
    if int(request.form['verification_code']) != int(costumer['verification_code']):
        string = '0123456789'
        vCode = ""
        length = len(string)
        for i in range(8) :
            vCode += string[math.floor(random.random() * length)]
        verificationCode = vCode
        dataUpdate = {
            'verification_code': verificationCode,
            'costumer_id': session['costumer_id']
        }
        Costumer.updateVerificationCode(dataUpdate)
        LOGIN = ADMINEMAIL
        TOADDRS  = costumer['email']
        SENDER = ADMINEMAIL
        SUBJECT = 'Verify Your Email'
        msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n"
            % ((SENDER), "".join(TOADDRS), SUBJECT) )
        msg += f'Use this verification code to activate your account: {verificationCode}'
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.set_debuglevel(1)
        server.ehlo()
        server.starttls()
        server.login(LOGIN, PASSWORD)
        server.sendmail(SENDER, TOADDRS, msg)
        server.quit()

        flash('Verification Code is wrong. We just sent you a new one', 'wrongCode')
        return redirect(request.referrer)
    
    Costumer.activateAccount(data)
    return redirect('/dashboard')



@app.route('/dashboard')
def dashboard():
    if 'costumer_id' not in session:
        return redirect('/loginPage')
    if 'provider_id' in session:
        return redirect('/logout')
    loggedCostumerData = {
        'costumer_id': session['costumer_id']
    } 
    
    loggedCostumer = Costumer.get_costumer_by_id(loggedCostumerData)
    job = Job.get_all_jobs()
    jobposted=Job.count_jobs()
    
    if not loggedCostumer:
        return redirect('/logout')
  
    return render_template('dashboardClient.html',job=job, jobposted=jobposted)

@app.route('/results', methods=['GET', 'POST'])
def search():
    if 'costumer_id' not in session:
        return redirect('/')

    search_query = request.args.get('searchfield', default='')

    jobs = []

    if search_query:
        jobs = Job.search(search_query)
    return render_template('results.html', jobs=jobs)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

