from flask import Flask, render_template, redirect, url_for, request, send_file
from flask_sqlalchemy import SQLAlchemy
from io import BytesIO

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///filestorage.db'
db = SQLAlchemy(app)


#db.create_all()

class FileContents(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(300))
	data =	db.Column(db.LargeBinary)




#@app.route('/')
#	def index():
#		return render_template('index.html')

@app.route('/uploadtodos', methods=['POST','GET'])
def uploadtodos():
	if request.method =='POST':
		file= request.files['inputFile']

		newFile = FileContents(name=file.filename, data= file.read())
		db.session.add(newFile)
		db.session.commit()
		return 'Saved ' +file.filename + ' to the database!'
	return render_template('uploadtodos.html')

	#return '<h1> Salvo </h1>'

@app.route('/download')
def download():
	file_data = FileContents.query.filter_by(id=2).first()
	return send_file(BytesIO(file_data.data), attachment_filename='radial-blade-engine.jpg', as_attachment =True)

#@app.route('/return-file')
#def return_file():	
#	return send_file() 


#@app.route('/file-downloads')
#def file_downloads():	
#	return render_template('downloads.html')





if __name__ == '__main__':
	app.run(debug=True)