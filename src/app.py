from flask import Flask, render_template, request, url_for,jsonify,redirect
import os,json
from datetime import datetime
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials,db,storage
#import pyrebase

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
@app.route("/")
def index():
    global timestamps
    try:
        blobs_iterator = bucket.list_blobs(prefix="images/")

        # Convert the iterator to a list
        blobs = list(blobs_iterator)

        # Extract URLs and timestamps from the fetched blobs
        new_images = [{'url': blob.public_url, 'timestamp': blob.metadata.get('timestamp')} for blob in blobs if blob.metadata.get('timestamp') not in timestamps]

        if new_images:
            timestamps += [blob.metadata.get('timestamp') for blob in blobs]

        print("Timestamps:", timestamps)  # Add this line for debugging

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
    try:
        file = request.files['file']
        if file:
            # Set metadata properties for the uploaded file
            metadata = {
                'contentType': file.content_type,
                'timestamp': str(datetime.utcnow()),  # Include the current timestamp
            }

            # Upload the file with metadata
            blob = bucket.blob(f"images/{file.filename}")
            blob.upload_from_file(file, content_type=file.content_type)
            
            # Set metadata properties after uploading the file
            blob.metadata = metadata
            blob.patch()

            return redirect(url_for('index'))
    except Exception as e:
        print(f"Error uploading file: {str(e)}")
        return jsonify(status="error", error=str(e))


app.run(debug=True)