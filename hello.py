import os
from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username


class NameForm(FlaskForm):
    name = StringField('Cadastre o novo Professor:', validators=[DataRequired()])
    role = SelectField(u'Disciplina associada:', choices=[('DSWA5'), ('GPSA5'), ('IHCA5'), ('SODA5'), ('PJIA5'), ('TCOA5')])
    submit = SubmitField('Cadastrar')

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/avaliacao')
def avaliacao():
    return render_template('avaliacao.html')

@app.route('/cadastro_aluno')
def cadastro_aluno():
    return render_template('pagina_nao_disponivel.html')

@app.route('/cadastro_funcionario')
def cadastro_funcionario():
    return render_template('pagina_nao_disponivel.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    user_all = User.query.all()
    role_all = Role.query.all()

    if form.validate_on_submit():
        # Verifique se o usuário já existe
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            # Verifique se a disciplina (role) existe
            user_role = Role.query.filter_by(name=form.role.data).first()
            if user_role is None:
                # Se a disciplina não existir, crie-a
                user_role = Role(name=form.role.data)
                db.session.add(user_role)
                db.session.commit()

            # Crie o usuário e associe à disciplina
            user = User(username=form.name.data, role=user_role)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
            flash('Professor cadastrado com sucesso!', 'success')
        else:
            session['known'] = True
            flash('Professor já cadastrado. Escolha um nome diferente.', 'warning')

        session['name'] = form.name.data
        return redirect(url_for('index'))

    return render_template('index.html', form=form, name=session.get('name'),
                           known=session.get('known', False),
                           user_all=user_all, role_all=role_all)