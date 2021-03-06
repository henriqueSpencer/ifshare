from flask import Flask, render_template, redirect, url_for
from flask import request
from flask.ext.uploads import UploadSet, configure_uploads, IMAGES

app = Flask(__name__)
photos = UploadSet('photos', IMAGES)


app.config['UPLOADED_PHOTOS_DEST']='static/img'
configure_uploads(app, photos)

@app.route('/upload', methods=[ 'POST','GET'])
def upload():
	if request.method =='POST' and 'photo' in request.files:
		filename = photos.save(request.files['photo'])
		return filename
	return 'Saved' +file.filename + ' to the database!'




if __name__ == '__main__':
	app.run(debug=True)