from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from io import BytesIO

from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms.widgets import TextArea
from wtforms.validators import InputRequired, Email, Length
#o sqlalchema cria uma interface entre o banco e uma class python
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisisupposedtobesecret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ifshare.db'
db = SQLAlchemy(app)
Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#db.create_all()
###################################################### TEM DE RESETAR O BANCO DOS ARQUIVOS!!!!!!!!!!!!!!!!!!!!!!!
class FileContents(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(40))
	data =	db.Column(db.LargeBinary)

class MetaFile(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	idautor = db.Column(db.Integer)
	idFile = db.Column(db.Integer)
	titulo = db.Column(db.String(30), unique= True) # falta colocar unique= True
	curso = db.Column(db.Integer)
	professor = db.Column(db.String(20))
	ano = db.Column(db.String(5))
	turno = db.Column(db.String(10)) 
	


class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(15), unique= True)
	email = db.Column(db.String(50), unique= True)
	password = db.Column(db.String(80))
	matricula= db.Column(db.String(14))

#####################################                    #########################################

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class LoginForm(FlaskForm):
	username = StringField('username', validators=[InputRequired(), Length(min=4, max =15)])
	password = PasswordField('password', validators=[InputRequired(), Length(min=8, max =80)])
	remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
	email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'),Length(max=50)])
	username = StringField('username', validators=[InputRequired(), Length(min=4, max =15)])
	password = PasswordField('password', validators=[InputRequired(), Length(min=8, max =80)])
	matricula = StringField('matricula',validators=[InputRequired(), Length(max =14)])

class RegisterArquivo(FlaskForm):
	titulo = StringField('titulo', validators=[InputRequired(),Length(max=30)])
	#curso = StringField('curso', validators=[InputRequired(),Length(max=20)])
	curso = SelectField('Curso', choices=[('1', 'Informatica'), ('2', 'Jogos Digitais'), ('3','Equipamentos Biometicos'),('4','Manutencao e Suporte')], validators=[InputRequired()])
	professor = StringField('profesor', validators=[InputRequired(), Length(min=4, max =20)])
	ano = StringField('ano', validators=[InputRequired(), Length(min=2, max =4)])
	#turno = StringField('turno', validators=[InputRequired(),Length(max=20)])
	turno = SelectField('Turno', choices=[('man', 'Manha'), ('tar','Tarde'), ('noi', 'Noite')], validators=[InputRequired()])
	#		SelectField('Programming Language', choices=[('C++'), ('Python'), ('Plain Text')], validators=[InputRequired()])

@app.route('/')
def index():
	
	return render_template('index.html')

@app.route('/login', methods=['GET','POST'])
def login():
	form = LoginForm()

	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user:		#compara o hash do banco com a transformacao da senha passa em hash
			if check_password_hash(user.password, form.password.data):
			#if user.password == form.password.data:
				login_user(user, remember=form.remember.data)
				return redirect(url_for('dashboard'))

		return '<h2> Invalid username or password </h2>'
		#return '<h1>' + form.username.data + ' ' +form.password.data + '</h1>' 


	return render_template('login.html', form=form)

@app.route('/signup', methods=['GET','POST'])
def signup():
	form = RegisterForm()

	if form.validate_on_submit():
		hashed_password = generate_password_hash(form.password.data, method= 'sha256')
		new_user = User(username=form.username.data, email=form.email.data, password=hashed_password, matricula=form.matricula.data)
		#new_user = User(username=form.username.data, email=form.username.data, password=form.password.data)
		db.session.add(new_user)
		db.session.commit()

		return '<h1> New user has been create, porra </h1>'
		#return '<h1>' + form.username.data + ' '+form.email.data + ' ' +form.password.data + '</h1>' 

	return render_template('signup.html', form=form)

@app.route('/dashboard')
@login_required #para nao poder acessar diretamente
def dashboard():
	idusuario = current_user.id
	#texto = Texto.query.filter_by(autor=idusuario)
	return render_template('dashboard.html', name = current_user.username)

@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('index'))



@app.route('/uploadtodosPrincipal', methods=['POST','GET'])
@login_required
def uploadtodosPrincipal():

	form = RegisterArquivo()
	testando= '3'
	aul = current_user.id    #### falta ajeitar
	if form.validate_on_submit():
		newFile = MetaFile(titulo=form.titulo.data, curso=form.curso.data, professor=form.professor.data, ano=form.ano.data, idautor=aul, turno=form.turno.data, idFile=testando)
		db.session.add(newFile)
		db.session.commit()							#%d' % newFile.id
		return redirect(url_for('uploadtodosArquivos', id=newFile.id))
	return render_template('/uploadtodosPrincipal.html', form=form)

			
@app.route('/uploadtodosArquivos/<int:id>', methods=['POST','GET'])
def uploadtodosArquivos(id):

	if request.method =='POST':
		novoId=MetaFile.query.filter_by(id=id).first()

		file= request.files['inputFile']
		newFile = FileContents(name=file.filename, data= file.read())

		novoId.idFile=newFile.id
		db.session.add(newFile)
		db.session.commit()
		return 'Saved ' +file.filename + ' to the database!'
	return render_template('uploadtodosArquivos.html', id=id)

#@app.route('/exibirArquivos/<int:curso>')
#def exibirArquivos(curso):

#	return render_template('exibirArquivos.html',curso=curso)

#@app.route('/download-principal/<int:id>')
#def download():
#	file_data = FileContents.query.filter_by(id=2).first()
#	return send_file(BytesIO(file_data.data), attachment_filename='radial-blade-engine.jpg', as_attachment =True)

#@app.route("/atualizar/<int:id>", methods=['GET','POST'])
#def atualizar(id):
#	pessoa=Pessoa.query.filter_by(_id=id).first()
#
#	if request.method == "POST":
#		nome=request.form.get("nome")
#		telefone=request.form.get("telefone")
#		email=request.form.get("email")
#
#		if nome and telefone and email:
#			pessoa.nome=nome
#			pessoa.telefone=telefone
#			pessoa.email=email
#
#			db.session.commit()
#
#			return redirect(url_for("lista"))
#
#	return render_template("atualizar.html", pessoa=pessoa)



if __name__ == '__main__':
	app.run(debug=True)