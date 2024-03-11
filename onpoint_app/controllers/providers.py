from onpoint_app import app
from flask import render_template, redirect, session, request, flash
from onpoint_app.models.provider import Provider
from onpoint_app.models.job import Job
from flask_bcrypt import Bcrypt
import random
import math
import smtplib
from .env import ADMINEMAIL
from .env import PASSWORD

bcrypt = Bcrypt(app)

# HR Routes


@app.route('/loginPageProvider')
def loginPageProvider():
    if 'provider_id' in session:
        return redirect('/dashboardProvider')
    return render_template('loginAdmin.html')

@app.route('/loginProvider', methods=['POST'])
def loginProvider():
    if 'provider_id' in session:
        return redirect('/dashboardProvider')
    provider = Provider.get_provider_by_email(request.form)
    if not provider:
        flash('This email does not exist.', 'emailLogin')
        return redirect('/loginPageProvider')
    if not bcrypt.check_password_hash(provider['password'], request.form['password']):
        flash('Your password is wrong!', 'passwordLogin')
        return redirect('/loginPageProvider')
    session['provider_id'] = provider['id']
    return redirect('/dashboardProvider')

@app.route('/registerProvider', methods=['POST'])
def registerProvider():
    if 'provider_id' in session:
        return redirect('/dashboardProvider')
    
    if Provider.get_provider_by_email(request.form):
        flash('This email already exists. Try another one.', 'emailSignUp')
        return redirect('/loginPageProvider')
    
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
        'about': request.form['about'],
        'password': bcrypt.generate_password_hash(request.form['password']),
        'verification_code': verificationCode,
    }
    Provider.create_provider(data)

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
    
    provider = Provider.get_provider_by_email(data)
    session['provider_id'] = provider['id']

    return redirect('/verify/email/provider')

@app.route('/verify/email/provider')
def verifyEmailProvider():
    if 'provider_id' not in session:
        return redirect('/')
    data = {
        'provider_id': session['provider_id']
    }
    provider = Provider.get_provider_by_id(data)

    if provider['is_verified'] == 1:
        return redirect('/dashboard')
    return render_template('verifyProvider.html', loggedProvider = provider)


@app.route('/activate/account/provider', methods=['POST'])
def activateAccountProvider():
    if 'provider_id' not in session:
        return redirect('/')
    data = {
        'provider_id': session['provider_id']
    }
    provider = Provider.get_provider_by_id(data)
    if provider['is_verified'] == 1:
        return redirect('/dashboard')
    
    if not request.form['verification_code']:
        flash('Verification Code is required', 'wrongCode')
        return redirect(request.referrer)
    
    if int(request.form['verification_code']) != int(provider['verification_code']):
        string = '0123456789'
        vCode = ""
        length = len(string)
        for i in range(8) :
            vCode += string[math.floor(random.random() * length)]
        verificationCode = vCode
        dataUpdate = {
            'verification_code': verificationCode,
            'provider_id': session['provider_id']
        }
        Provider.updateVerificationCode(dataUpdate)
        LOGIN = ADMINEMAIL
        TOADDRS  = provider['email']
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
    
    Provider.activateAccount(data)
    return redirect('/dashboardProvider')


@app.route('/dashboardProvider')
def dashboardProvider():
    if 'provider_id' not in session:
        return redirect('/loginPageProvider')
    
    if 'costumer_id' in session:
        return redirect('/logout')
    loggedProviderData = {
        'provider_id': session['provider_id']
    } 
    job = Job.get_job_by_id(loggedProviderData)
    loggedProvider = Provider.get_provider_by_id(loggedProviderData)
    jobs=Job.get_provider_jobs_by_id(loggedProviderData)
    if not loggedProvider:
        return redirect('/logoutProvider')
    return render_template('dashboardAdmin.html', jobs=jobs,job=job)

@app.route('/logoutProvider')
def logoutProvider():
    session.clear()
    return redirect('/')
