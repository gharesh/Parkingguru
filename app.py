from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory,Response

from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_pymongo import PyMongo
from models.Users import User
from models.Users import db
from models.MongoDB import MongoDB
from werkzeug.utils import secure_filename
import re
import base64
import io
import cv2
import time
from imageio import imread
import json
import plotly
import plotly.plotly as py
import plotly.graph_objs as go

import numpy as np

from camera import VideoCamera
from utils import vehicle_speed_main
from utils import vehicle_mlpl_main
from utils import slots_lane
from twilio import twiml

import os

#FLASK
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

from flask_ckeditor import CKEditor, CKEditorField, upload_fail, upload_success
basedir = os.path.abspath(os.path.dirname(__file__))

from pathlib import Path

#***************

# setup the app
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = "SuperSecretKey"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

app.config['MONGO_DBNAME'] = 'gh19'
#app.config['MONGO_URI'] = 'mongodb://n30:infy%40123@c:27017,democluster-shard-00-01-klhmq.mongodb.net:27017,democluster-shard-00-02-klhmq.mongodb.net:27017/test?ssl=true&replicaSet=DemoCluster-shard-0&authSource=admin&retryWrites=true'

app.config['MONGO_URI'] = 'mongodb://n30:infy%40123@democluster-shard-00-01-klhmq.mongodb.net'


#FLASK*******

app.config['CKEDITOR_SERVE_LOCAL'] = True
app.config['CKEDITOR_HEIGHT'] = 400
app.config['CKEDITOR_FILE_UPLOADER'] = 'upload'
# app.config['CKEDITOR_ENABLE_CSRF'] = True  # if you want to enable CSRF protect, uncomment this line
app.config['UPLOADED_PATH'] = os.path.join(basedir, 'uploads')

app.secret_key = 'secret string'


#***********

#**** GRAPHS PLOTLY *****

@app.route('/showLineChart')
def line():
    # count = 500
    mongoObj = MongoDB()
    dataa = mongoObj.findAll("MLCPParking")
    floors = []
    slotsinuse = []
    for record in dataa:
        floors.append(record['floorNumber'])
        slotsinuse.append(record['slotsInUse'])
    xScale = floors
    yScale = slotsinuse
    # Create a trace
    trace = go.Scatter(
        x=xScale,
        y=yScale
    )
    data = [trace]
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('lineChart.html',
                           graphJSON=graphJSON, user=current_user)


@app.route('/showMultiChart')
def multiLine():
    mongoObj = MongoDB()
    dataa = mongoObj.findAll("MLCPParking")
    xScale = ['cam1', 'cam2', 'cam3', 'cam4', 'cam5','cam6', 'cam7', 'cam8', 'cam9', 'cam10']
    y0_scale = [13.8, 22.3, 32.5, 37.2, 49.9, 56.1, 57.7, 58.3, 51.2, 42.8, 31.6, 15.9]
    y1_scale = [23.6, 14.0, 27.0, 36.8, 47.6, 57.7, 58.9, 61.2, 53.3, 48.5, 31.0, 23.6]
    y2_scale = [12.7, 14.3, 18.6, 35.5, 49.9, 58.0, 60.0, 58.6, 51.7, 45.2, 32.2, 29.1]

    # Create traces
    trace0 = go.Scatter(
        x=xScale,
        y=y0_scale
    )
    trace1 = go.Scatter(
        x=xScale,
        y=y1_scale
    )
    trace2 = go.Scatter(
        x=xScale,
        y=y2_scale
    )
    data = [trace0, trace1, trace2]
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('multiChart.html',
                           graphJSON=graphJSON, user=current_user)

    
#***************************

ckeditor = CKEditor(app)
db.init_app(app)
bcrypt = Bcrypt(app)
mongo = PyMongo(app)


mongoObj = MongoDB()

# setup the login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# create the db structure
with app.app_context():
    db.create_all()

#FLASK********************


class PostForm(FlaskForm):
    title = StringField('Title')
    body = CKEditorField('Body', validators=[DataRequired()])
    submit = SubmitField()


@app.route('/up', methods=['GET', 'POST'])
def indexUpload():
    form = PostForm()
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        # You may need to store the data in database here
        return render_template('post.html', title=title, body=body)
    return render_template('indexUpload.html', form=form)



@app.route('/files/<filename>')
def uploaded_files(filename):
    path = app.config['UPLOADED_PATH']
    return send_from_directory(path, filename)


@app.route('/upload', methods=['POST'])
def upload():
    f = request.files.get('upload')
    extension = f.filename.split('.')[1].lower()
    if extension not in ['jpg', 'gif', 'png', 'jpeg']:
        return upload_fail(message='Image only!')
    f.save(os.path.join(app.config['UPLOADED_PATH'], f.filename))
    url = url_for('uploaded_files', filename=f.filename)
    return upload_success(url=url)

#**********************
####  setup routes  ####
@app.route('/')
@login_required
def index():
    cars = mongoObj.findAll("MLCPParking")
    calcCars = mongoObj.findAll("MLCPParking")
    totalSlots= 0
    slotsInUse = 0
    #TotalVehicles = len(cars)
    #TotalVehicles = 0
    for x in calcCars:
        #print(" total slots = ",x)
        totalSlots=x['totalSlots']+totalSlots
        slotsInUse=x['slotsInUse']+slotsInUse
    slotsAvailable = totalSlots - slotsInUse
    overspeed=mongoObj.findAll("SpeedCam1")
    violaters = 0
    for o in overspeed:
        if float(o['speed']) >25:
            violaters = violaters+1
    return render_template('index.html', cars=cars, totalSlots=totalSlots, slotsInUse=slotsInUse, slotsAvailable=slotsAvailable,violaters=violaters,user=current_user)


@app.route("/login", methods=["GET", "POST"])
def login():

    # clear the inital flash message
    session.clear()
    if request.method == 'GET':
        return render_template('login.html')

    # get the form data
    username = request.form['username']
    password = request.form['password']

    remember_me = False
    if 'remember_me' in request.form:
        remember_me = True

    # query the user
    registered_user = User.query.filter_by(username=username).first()

    # check the passwords
    if registered_user is None and bcrypt.check_password_hash(registered_user.password, password) == False:
        flash('Invalid Username/Password')
        return render_template('login.html')

    # login the user
    login_user(registered_user, remember=remember_me)
    return redirect(request.args.get('next') or url_for('index'))


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'GET':
        session.clear()
        return render_template('register.html')

    # get the data from our form
    password = request.form['password']
    conf_password = request.form['confirm-password']
    username = request.form['username']
    email = request.form['email']

    # make sure the password match
    if conf_password != password:
        flash("Passwords do not match")
        return render_template('register.html')

    # check if it meets the right complexity
    check_password = password_check(password)

    # generate error messages if it doesnt pass
    if True in check_password.values():
        for k,v in check_password.iteritems():
            if str(v) is "True":
                flash(k)

        return render_template('register.html')

    # hash the password for storage
    pw_hash = bcrypt.generate_password_hash(password)

    # create a user, and check if its unique
    user = User(username, pw_hash, email)
    u_unique = user.unique()

    # add the user
    if u_unique == 0:
        db.session.add(user)
        db.session.commit()
        flash("Account Created")
        return redirect(url_for('login'))

    # else error check what the problem is
    elif u_unique == -1:
        flash("Email address already in use.")
        return render_template('register.html')

    elif u_unique == -2:
        flash("Username already in use.")
        return render_template('register.html')

    else:
        flash("Username and Email already in use.")
        return render_template('register.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/addImage')
def addImage():
    return render_template('addImage.html', user=current_user)


@app.route('/livestream')
def live_stream():
    return render_template('livestream.html', user=current_user)

@app.route('/speedcam', methods=["GET", "POST"])
def speedcam():
    if request.method == 'POST':
        cam_no = request.form['cam_no']
        vehicle_speed_main.object_detection_function(cam_no)
    return render_template('speedcam.html', user=current_user)

@app.route('/mlplcam', methods=["GET", "POST"])
def mlplcam():
    if request.method == 'POST':
        cam_no = request.form['cam_no']
        vehicle_mlpl_main.object_detection_function(cam_no)
    return render_template('mlplcam.html', user=current_user)

@app.route('/slotslane', methods=["GET", "POST"])
def slots():
    if request.method == 'POST':
        cam_no = request.form['slots_no']
        slots_lane.slots_lane()
    return render_template('slotslane.html', user=current_user)

@app.route('/speedcamlive')
def speedcamlive():
    return render_template('speedcamlive.html', user=current_user)

@app.route('/mlplcamlive')
def mlplcamlive():
    return render_template('mlplcamlive.html', user=current_user)

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_vehicle_speed')
def video_feed_vehicle_speed():
    return Response(gen(vehicle_speed_main.object_detection_function("data/vid1.mp4")),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
'''
@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    """Respond to incoming calls with a simple text message."""
    # Start our TwiML response
    resp = twiml.Response()

    # Add a message
    resp.message("The Robots are coming! Head for the hills!")

    return str(resp)
'''

@app.route('/profile')
def profile():
    return render_template('profile.html', user=current_user)


@app.route('/settings')
def settings():
    return render_template('settings.html', user=current_user)


@app.route('/newImageAdded')
def newImageAddedList():
    return render_template('newImageAdded.html', user=current_user)


#*********************************#
#### MONGO ROUTES - REST Calls ####
#*********************************#

@app.route('/mongoDemo', methods=['GET'])
def demo():
    #mongoObj = MongoDB()
    #mongoObj.initialize()
    output = mongoObj.find_sort("MLCPParking")
    print("respOUTPUT",output)
    #return  jsonify({'result' : output})
    return  jsonify(output)

@app.route('/MLCP', methods=['GET'])
def get_all_carDetails_OfFloors():
    output = mongoObj.find_sort("MLCPParking")
    print("respOUTPUT",output)
    return  jsonify(output)


@app.route('/speedCam1', methods=['GET'])
def get_all_carDetails_FromSpeedCam1():
    try:
        carsAll = mongoObj.findAll("SpeedCam1")
        #print(len(carsAll),"---outer")
        #for x in carsAll:
        #    print(len(x),"---outer")
        return render_template('showCars.html', cars=carsAll, user=current_user)
    except Exception as e:
        print("Error getting all car details from cam #1")
        return jsonify({'error' : str(e)})

@app.route('/violations', methods=['GET'])
def violationsToday():
    try:
        violators = mongoObj.getViolators("SpeedCam1",25)
        return render_template('violators.html', violators=violators, user=current_user)
    except Exception as e:
        print("Error getting all violator details")
        return jsonify({'error' : str(e)})

@app.route('/floor1', methods=['GET'])
def floorOnes():
    try:
        floor1 = mongoObj.getfloorLogs("MLCPFloorTraffic","1")
        return render_template('floor1.html', floor1=floor1, user=current_user)
    except Exception as e:
        print("Error getting  floor details")
        return jsonify({'error' : str(e)})



@app.route('/MLCP/<floorNumber>', methods=['GET'])
def get_one_FloorDetail(floorNumber):
    myquery = { "floorNumber": str(floorNumber) }
    output = mongoObj.find_one("MLCPParking",myquery)
    if output:
        print("outPut for one =", output)
    else:
        output = "Incorrect Floor Number"
    return jsonify({'result' : output})

@app.route('/MLCPFloorInbound', methods=['POST'])
def add_carDetails_ToFloor():
    floorNumber = request.json['floorNumber']
    print("fn POST =",floorNumber)
    vehicleNumber = request.json['vehicleNumber']
    print("vn POST =",vehicleNumber)

    #Increment vehicle count in DB
    filterVal = {"floorNumber": str(floorNumber)}
    updateVal = {"$inc": {"slotsInUse": 1 }}
    output = mongoObj.find_one_and_update("MLCPParking",filterVal,updateVal)

    #Add vehicle number in DB
    filterVal ={"floorNumber": str(floorNumber)}
    updateVal= { "$push": { "vehiclesOnFloor": str(vehicleNumber) }}
    output = mongoObj.find_one_and_update("MLCPParking",filterVal,updateVal)

    print("floorNumber----",floorNumber)
    filterVal ={"floorNumber": str(floorNumber)}
    conditionVal= { '_id':0, 'floorNumber':1,'totalSlots':1, 'slotsInUse':1, 'vehiclesOnFloor':1 }
    responseMongo = mongoObj.find_one("MLCPParking",filterVal,conditionVal)
    return jsonify({'result' : responseMongo})

@app.route('/Upload', methods=['POST'])
def saveCarSnapshot():
   # filename = secure_filename(file.filename)
     if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            print('No selected file')
            return redirect(request.url)
        #p = Path("/a/b/c.txt")
        #millis = int(round(time.time() * 1000))
        #(os.path.splitext(os.path.basename(file))[0])
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        print("File saved in folder...")
        return render_template('index.html', user=current_user,msg="File Saved")


@app.route('/add_image', methods=['GET'])
def showImagesFromDB():
    print("Base Directory = ",basedir)
    try:
        cars = mongoObj.findAll("MLCPFloorInbound")
        """for x in cars:
            print(len(x),"---outer")
            print(x['vehicleNumber'],"---vehicle num")
        """

        for x in cars:
            print(len(x),"---outer")
            print(x['vehicleNumber'],"---vehicle num")
            #img = base64.b64decode(x['snapShot'])
            decode=x['snapShot'].decode()
            img_tag = '<img alt="sample" src="data:image/jpeg;base64,{0}"/>'.format(decode)
            #img = x['snapShot']
            return render_template('newImageAdded.html', car = x['vehicleNumber'],img=img_tag, user=current_user)
            #img=base64.decode(x['snapShot'])
            #img = base64.b64decode(x['snapShot'])
        #img = imread(io.BytesIO(base64.b64decode(cars["snapShot"])))
        #print("cars:",cars)
        #return render_template('newImageAdded.html', cars = cars, img=img, user=current_user)



        #return render_template('newImageAdded.html', cars = cars, user=current_user)
    except Exception as e:
        print("errx")
        return jsonify({'error' : str(e)})
    #file = request.files['file']
    #filename = secure_filename(file.filename)
    #file = open("uploads/car1.jpg")
     #mongoObj.saveImageToDB("MLCPFloorInbound","INA6069","uploads\car1.jpg")
     #return render_template('newImageAdded.html', user=current_user)

"""
@app.route('/add_newCar', methods=['GET'])
def addCarToDB():
    file = request.files['file']
    mongoObj.saveImageToDB("MLCPFloorInbound","INA6069","uploads\car1.jpg")
    return render_template('newImageAdded.html', user=current_user)
"""
####  end routes  ####

# required function for loading the right user
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

# check password complexity
def password_check(password):
    """
    Verify the strength of 'password'
    Returns a dict indicating the wrong criteria
    A password is considered strong if:
        8 characters length or more
        1 digit or more
        1 symbol or more
        1 uppercase letter or more
        1 lowercase letter or more
        credit to: ePi272314
        https://stackoverflow.com/questions/16709638/checking-the-strength-of-a-password-how-to-check-conditions
    """

    # calculating the length
    length_error = len(password) <= 8

    # searching for digits
    digit_error = re.search(r"\d", password) is None

    # searching for uppercase
    uppercase_error = re.search(r"[A-Z]", password) is None

    # searching for lowercase
    lowercase_error = re.search(r"[a-z]", password) is None

    # searching for symbols
    symbol_error = re.search(r"[ !@#$%&'()*+,-./[\\\]^_`{|}~"+r'"]', password) is None

    ret = {
        'Password is less than 8 characters' : length_error,
        'Password does not contain a number' : digit_error,
        'Password does not contain a uppercase character' : uppercase_error,
        'Password does not contain a lowercase character' : lowercase_error,
        'Password does not contain a special character' : symbol_error,
    }

    return ret

if __name__ == "__main__":
    # change to app.run(host="0.0.0.0"), if you want other machines to be able to reach the webserver.
    app.run()