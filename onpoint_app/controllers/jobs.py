
from onpoint_app import app

from flask import render_template, redirect, session, request, flash,url_for


from onpoint_app.models.costumer import Costumer
from onpoint_app.models.provider import Provider
from onpoint_app.models.job import Job

from .env import UPLOAD_FOLDER
from .env import UPLOAD_FOLDER_LOGOS
from .env import ALLOWED_EXTENSIONS
app.config['job_images'] = UPLOAD_FOLDER
app.config['job_images_logo'] = UPLOAD_FOLDER_LOGOS
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import paypalrestsdk

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/jobs')
def jobs_index():
    return render_template('results.html')


@app.route('/postajob')
def postajob():
    if 'provider_id' not in session:
        return redirect('/')
    loggedProviderData = {
        'provider_id': session['provider_id']
    }
    return render_template('postServices.html',loggedUser = Provider.get_provider_by_id(loggedProviderData))


@app.route('/createjob', methods=['POST'])
def create_job():
    if 'provider_id' not in session:
        return redirect('/')

    images = request.files.getlist('job_post_image')
    image_filenames = []

    for image in images:
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            time = datetime.now().strftime("%d%m%Y%S%f")
            time += filename
            filename = time
            image.save(os.path.join(app.config['job_images'], filename))
            image_filenames.append(filename)

    # Get the company logo image and save it
    logos = request.files.getlist('company_logo')
    logo_filenames = []

    for logo in logos:
        if logo and allowed_file(logo.filename):
            filename = secure_filename(logo.filename)
            time = datetime.now().strftime("%d%m%Y%S%f")
            time += filename
            filename = time
            logo.save(os.path.join(app.config['job_images_logo'], filename))
            logo_filenames.append(filename)

    # Construct the data dictionary for creating the job
    data = {
        'title': request.form['title'],
        'description': request.form['description'],
        'address': request.form['address'],
        'education_experience': request.form['education_experience'],
        'city': request.form['city'],
        'employment_status': request.form.get('employment_status'),
        'experience': request.form['experience'],
        'deadline': request.form['deadline'],
        'job_post_image': ','.join(image_filenames),
        'provider_id': session['provider_id']
    }
    
    # Create the job using your Job class
    Job.create_job(data)

    return redirect('/dashboardProvider')


@app.route('/job/<int:id>')
def viewjob(id):
    if 'provider_id' in session:
        data = {
            'provider_id': session.get('provider_id'),
            'job_id': id
        }
        loggedProvider = Provider.get_provider_by_id(data)
        job = Job.get_job_by_id(data)
        jobcreator = Job.get_job_creator(data)
        return render_template('jobdisplay.html', job=job, loggedProvider=loggedProvider, jobcreator=jobcreator)

    elif 'costumer_id' in session:
        data = {
            'costumer_id': session.get('costumer_id'),
            'job_id': id
        }
        loggedProvider = Provider.get_provider_by_id(data)
        loggedUser  = Costumer.get_costumer_by_id(data)
        job = Job.get_job_by_id(data)
        jobcreator = Job.get_job_creator(data)
        return render_template('jobdisplay.html', job=job, loggedUser=loggedUser , jobcreator=jobcreator,loggedProvider=loggedProvider)

    else:
        return redirect('/')
    
@app.route('/all_professions')
def view_all_professions():
    professions = Provider.get_all_professions()
    return render_template('dashboard.html', professions=professions)

@app.route('/job/edit/<int:id>')
def editJob(id):
    if 'provider_id' not in session:
        return redirect('/')
    data = {
        'provider_id': session.get('provider_id'),
        'job_id': id
    }
    job = Job.get_job_by_id(data)
    if job and job['provider_id'] == session['provider_id']:
        return render_template('editjob.html', job=job)
    return redirect('/dashboarProvider')


@app.route('/job/update/<int:id>', methods = ['POST'])
def updateJob(id):
    if 'provider_id' not in session:
        return redirect('/')
    data = {
        'provider_id': session.get('provider_id'),
        'job_id': id
    }
    job = Job.get_job_by_id(data)
    if job and job['provider_id'] == session['provider_id']:
        data = {
            'description': request.form['description'],
            'address': request.form['address'],
            'education_experience': request.form['education_experience'],
            'city': request.form['city'],
            'experience': request.form['experience'],
            'employment_status': request.form['employment_status'],
            'id': id
        }
        Job.update(data)
        return redirect('/job/'+ str(id))
    return redirect('/dashboarProvider')



@app.route('/job/delete/<int:id>')
def deleteJob(id):
    if 'provider_id' not in session:
        return redirect('/')
    data = {
        'job_id': id
    }
    Job.delete(data)
    return redirect(request.referrer)

@app.route('/rate_job/<int:job_id>', methods=['POST'])
def rate_job(job_id):
    if 'costumer_id' not in session:
        return redirect('/')
    
    if 'provider_id' in session:
        return redirect('/logout')

    rating = int(request.form.get('rating', 0))

    if 1 <= rating <= 5:
        Job.update_star_rating(job_id, rating)
        flash('Rating submitted successfully!', 'success')
    else:
        flash('Invalid rating value. Please choose a value between 1 and 5.', 'error')

    return redirect('/dashboard')
@app.route('/checkout/paypal')
def checkoutPaypal():
    if 'costumer_id' not in session:
            return redirect('/')
    cmimi = 100
    ora = 2
    totalPrice = round(cmimi * ora)

    try:
        paypalrestsdk.configure({
            "mode": "sandbox", # Change this to "live" when you're ready to go live
            "client_id": "AfJFDDdf4p2iTRu7AUMcyC3G7D9rOJL26DqChJ3SnGuKIzIKNnzRQ6Xy7bjZG-MQNwgoSQrPOBDhL9x0",
            "client_secret": "EHfue1ecmGryKAy9qYp9S1yjNG5HloMaJItptFCqooNUuRGc0wvZz9fv5WoYq-KFJAwpYIgvJCvYF23m"
        })

        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "transactions": [{
                "amount": {
                    "total": totalPrice,
                    "currency": "USD"  # Adjust based on your currency
                },
                "description": f"Pagese per kontaktin {ora} orë!"
            }],
            "redirect_urls": {
                "return_url": url_for('paymentSuccess', _external=True, totalPrice=totalPrice),
                "cancel_url": "http://example.com/cancel"
            }
        })

        if payment.create():
            approval_url = next(link.href for link in payment.links if link.rel == 'approval_url')
            return redirect(approval_url)
        else:
            flash('Something went wrong with your payment', 'creditCardDetails')
            return redirect(request.referrer)
    except paypalrestsdk.ResourceNotFound as e:
        flash('Something went wrong with your payment', 'creditCardDetails')
        return redirect(request.referrer)






@app.route("/success", methods=["GET"])
def paymentSuccess():
    payment_id = request.args.get('paymentId', '')
    payer_id = request.args.get('PayerID', '')
    try:
        paypalrestsdk.configure({
            "mode": "sandbox", # Change this to "live" when you're ready to go live
            "client_id": "AfJFDDdf4p2iTRu7AUMcyC3G7D9rOJL26DqChJ3SnGuKIzIKNnzRQ6Xy7bjZG-MQNwgoSQrPOBDhL9x0",
            "client_secret": "EHfue1ecmGryKAy9qYp9S1yjNG5HloMaJItptFCqooNUuRGc0wvZz9fv5WoYq-KFJAwpYIgvJCvYF23m"
        })
        payment = paypalrestsdk.Payment.find(payment_id)
        if payment.execute({"payer_id": payer_id}):
            
            
            ammount = request.args.get('totalPrice')
            status = 'Paid'
            job_id = session['costumer_id']
            data = {
                'ammount': ammount,
                'status': status,
                'job_id': job_id
            }
            Job.createPayment(data)
           
            flash('Your payment was successful!', 'paymentSuccessful')
            return redirect('/dashboard')
        else:
            flash('Something went wrong with your payment', 'paymentNotSuccessful')
            return redirect('/dashboard')
    except paypalrestsdk.ResourceNotFound as e:
        flash('Something went wrong with your payment', 'paymentNotSuccessful')
        return redirect('/dashboard')


@app.route("/cancel", methods=["GET"])
def paymentCancel():
    flash('Payment was canceled', 'paymentCanceled')
    return redirect('/dashboard')