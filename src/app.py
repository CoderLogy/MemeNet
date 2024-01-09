"""
    This is a Flask web application that allows users to upload and view memes.
    
    :param response: The `response` parameter is the hCaptcha response that is sent from the client-side
    when the user completes the hCaptcha challenge. It is used to validate the user's response and
    ensure that the challenge was successfully completed
    :return: The Flask app is being run in debug mode.
    """

from flask import Flask, render_template, request, url_for,jsonify,redirect,make_response,flash
import os,json
from datetime import datetime
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials,db,storage
#import pyrebase
from flask_wtf import FlaskForm
from wtforms import StringField, FileField
from wtforms.validators import DataRequired, ValidationError
import requests

load_dotenv()
firebase_cred = json.loads(os.getenv("firebase_cred"))
cred = credentials.Certificate(firebase_cred)
firebase_app = firebase_admin.initialize_app(cred, {"databaseURL": "https://memenetted-default-rtdb.firebaseio.com/",'storageBucket': 'memenetted.appspot.com'})
#firebase = pyrebase.initialize_app(configs)
database=db.reference()
bucket=storage.bucket(app=firebase_app)
#storages = firebase.storage()
timestamps=[]
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
'''database = db.reference("memes")
new_meme_data = {
    'title': 'New Funny Meme',
    'url': 'https://example.com/new_meme.jpg',
    'ratings': {
        'total': 0,
        'count': 0
    },
    'comments': {
        'comment1': {
            'user': 'user123',
            'text': 'Awesome!'
        }
    }
}

# Add the new meme using push to generate a unique key
new_meme_ref = database.push(new_meme_data)

r = database.get()
print(r)
'''
class MemeForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    tags = StringField('Tags', validators=[DataRequired()])
    file = FileField('File', validators=[DataRequired()])
    hcaptcha_response = StringField('hCaptcha Response', validators=[DataRequired()])

    def validate_hcaptcha_response(self, field):
        # Validate hCaptcha response here
        secret_key = os.getenv('captcha_key')
        response = field.data

        data = {
            'secret': secret_key,
            'response': response
        }

        verification_response = requests.post('https://hcaptcha.com/siteverify', data=data)
        result = verification_response.json()

        if not result['success']:
            raise ValidationError('hCaptcha verification failed')
        else:
            return True
        
@app.after_request
def add_cache_control(response):
    response.headers['Cache-Control'] = 'public, max-age=3600'  # Adjust max-age as needed
    return response

@app.route("/")
def index():
    global timestamps
    try:
        blobs_iterator = bucket.list_blobs(prefix="images/")

        # Convert the iterator to a list
        blobs = list(blobs_iterator)

        # Extract URLs and timestamps from the fetched blobs
        new_images = [{'url': blob.public_url, 'timestamp': blob.metadata.get('timestamp'), 'tags': blob.metadata.get('tags', []),
               'title': blob.metadata.get('title', '')} for blob in blobs if blob.metadata.get('timestamp') is not None]

        if new_images:
            for blob in blobs:
                timestamp = blob.metadata.get('timestamp')
                print(f"Blob: {blob.name}, Timestamp: {timestamp}")
                if timestamp is not None and timestamp not in timestamps:
                    timestamps.append(timestamp)

        print("Timestamps:", timestamps)

        return render_template('index.html', images=new_images)
    except Exception as e:
        print(f"Error loading more images: {str(e)}")
        return jsonify(error=str(e))

@app.route("/search")
def search():
    # Your search route logic here
    return render_template('search.html')

@app.route("/post")
def post():
    # Your post route logic here
    return render_template('post.html')

@app.route("/upload", methods=["POST"])
def upload():
    form = MemeForm()

    # Check if the hCaptcha challenge is successfully completed
    response = request.form.get('h-captcha-response')
    if response:
        try:
            file = request.files['file']
            title = request.form['title']
            tags = request.form['tags']

            # Split tags only if it is not empty or contains only spaces
            tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]

            if file:
                # Set metadata properties for the uploaded file
                metadata = {
                    'contentType': file.content_type,
                    'timestamp': str(datetime.utcnow()),
                    'title': title,
                    'tags': tag_list,
                }

                # Upload the file with metadata
                blob = bucket.blob(f"images/{file.filename}")
                blob.upload_from_file(file, content_type=file.content_type)

                # Set metadata properties after uploading the file
                blob.metadata = metadata
                blob.patch()

                # Store data in the Firebase Realtime Database
                database = db.reference("memes")
                new_meme_data = {
                    'title': title,
                    'url': blob.public_url,
                    'tags': tag_list,
                }

                # Add the new meme to the database
                new_meme_ref = database.push(new_meme_data)

                flash('Meme successfully uploaded!', 'success')
                return redirect(url_for('index'))
        except Exception as e:
            print(f"Error uploading file: {str(e)}")
            flash(f"Error uploading file: {str(e)}", 'error')
    else:
        flash('Please complete the hCaptcha challenge.', 'error')

    return render_template('post.html', form=form)
