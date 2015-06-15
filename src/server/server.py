#!/usr/bin/env python3

import sys
from functools import wraps, lru_cache
import json
from enum import Enum

import requests
from sqlalchemy import func
from flask import Flask, request, session, redirect, abort, render_template, url_for
from flask.ext.sqlalchemy import SQLAlchemy

class Perms(Enum):
    _participant = (
            view_index,
            view_room,
            create_question,
            join_lecture,
            vote_tempo,
            vote_question,
            vote_survey
            ) = tuple(range(7))
    _lecturer = (
            manage_lecture,
            create_survey,
            create_room,
            close_survey,
            delete_question
            ) = tuple(range(12,12+5))
    _admin_only = (
            create_account,
            delete_account,
            assign_role,
            create_role,
            edit_role,
            delete_role
            ) = tuple(range(26,26+6))

DEFAULT_PARTICIPANT = Perms._participant.value
DEFAULT_LECTURER = Perms._participant.value + Perms._lecturer.value

MAX_OPTS = 4

app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://hieronymus:2dS3v5l6oaG2RpEne1CH7WT9UyEwe5nk@localhost/hieronymus'
app.config['PUSH_STREAM_URL'] = 'http://localhost/pub'
app.config['ADMINS'] = ['admin']
app.secret_key = 'jMHF20JxP49hfTp2rZIDFmRbPCcjw5p9'
db = SQLAlchemy(app)

def is_admin():
    return session['uid'] in app.config['ADMINS']

def publish(channel, eventtype, payload):
    return
    requests.post(app.config['PUSH_STREAM_URL'], params={'id': channel},
            data=json.dumps({'type': eventtype, 'payload': payload}))

def room(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        name = kwargs.pop('room_name')
        room = Room.query.filter_by(name=name).first()
        if not room:
            abort(404)
        elif room.passkey != '' and\
            not room.users.filter_by(name=session['uid']).count() == 1 and\
            not is_admin():
                return redirect('/login_room')
        request.room = room
        return func(*args, room=room, **kwargs)
    return wrapper

def auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not 'uid' in session:
            return redirect(url_for('login', redirect=request.path))
        user = request.user = User.query.filter_by(name=session['uid']).first()
        if not user:
            return redirect(url_for('login', redirect=request.path))
        if not getattr(Perms, func.__name__) in user.permissions or is_admin():
            abort(403)
        return func(*args, **kwargs)
    return wrapper

def perform_login(pw_form, pw):
    return pw_form==pw

######################

@app.route('/_login', methods=['GET', 'POST'])
def login():
    # return status codes
    if request.method == 'POST':
        #TODO link the user creation with LDAP
        if perform_login(request.form['uid'], request.form['password']):
            session['uid'] = request.form['uid']
            user = User(name=session['uid'], role=Role.query.filter_by(name='participant').one())
            db.session.add(user)
            db.session.commit()
            
            session['uid'] = request.form['uid'] 
            return redirect(request.args.get('redirect', '/'))
        elif perform_login(request.form['password'], user.password):
            session['uid'] = request.form['uid']            
            return redirect(request.args.get('redirect', '/'))
        else:
            return redirect('/_login')
    else:
        return render_template('login.html')

@app.route('/')
@auth
def view_index():
    return 'It works! ' + request.user.name + ' !'

@app.route('/create_room', methods=['GET', 'POST'])
@auth
def create_room():
    if request.method == 'POST':
        room = Room(request.form['name'], request.user, request.form['passkey'])
        request.user.rooms.append(room)
        db.session.add(room)        
        db.session.add(request.user)
        db.session.commit()
        return redirect('/'+room.name)
        # return room name view here
    else:
        return render_template('create_room.html')

@app.route('/login_room', methods=['GET', 'POST'])
@auth
def login_room():
    rooms = Room.query.all()
    rooms_name = []
    for room in rooms:
        rooms_name.append(room.name)
        
    if request.method == 'POST':
        room = Room.query.filter_by(name=request.form['room_name']).first()
        if(request.form['passkey'] == room.passkey):
            request.user.rooms.append(room)
            db.session.add(request.user)
            db.session.commit()
            return redirect('/'+room.name)
        else :
            return render_template('login_room.html', rooms_name=rooms_name)
    else :
        return render_template('login_room.html', rooms_name=rooms_name)
        
@app.route('/<room_name>')
@auth
@room
def view_room(room):
    return render_template('room.html',
                room=room,
                questions=room.questions,
                surveys=room.proper_surveys,
                is_lecturer=is_lecturer(),
                max_opts=MAX_OPTS)

@app.route('/<room_name>/ask', methods=['POST'])
@auth
@room
def create_question(room):
    sv = Survey(request.form['question'], [], room)
    db.session.add(sv)
    db.session.commit()
    publish(room.name, 'question', sv.json)
    return redirect('/'+room.name)

@app.route('/<room_name>/new_survey', methods=['POST'])
@auth
@room
def create_survey(room):
    opts = []
    for i in range(MAX_OPTS):
        opt = request.form.get('option'+str(i))
        if opt:
            opts.append(opt)
        else:
            break
    if len(opts) < 2: # communist polls not allowed
        abort(400)
    sv = Survey(request.form['title'], opts, room)
    db.session.add(sv)
    db.session.commit()
    publish(room.name, 'survey', sv.json)
    return redirect('/'+room.name)

@app.route('/<room_name>/<int:survey_id>/vote', methods=['POST'])
@auth
@room
def vote_survey(room, survey_id):
    sv = Survey.query.get_or_404(survey_id)
    val = int(request.form['val'])
    if not val in range(0, len(sv.options)) and val:
        abort(400)
    sv.cast_vote(request.user, val)
    return redirect('/'+room.name)

@app.route('/<room_name>/<int:survey_id>/close', methods=['POST'])
@auth
@room
def close_survey(room, survey_id):
    sv = Survey.query.get_or_404(survey_id)
    sv.closed = True
    db.session.add(sv)
    db.session.commit()
    return redirect('/'+room.name)

# ask for increased/decreased tempo
@app.route('/<room_name>/t/<action>', methods=['POST'])
@auth
@room
def vote_tempo(room_id, action):
    room = Room.query.get_or_404(room_id)
    if action not in ('up', 'down'):
        abort(400, 'Tempo action must be one of "up" or "down"')
    publish(room.name, 'tempo', action)
    return redirect('/'+room.name)

###################

user_rooms = db.Table('user_rooms',
    db.Column('uid', db.Integer, db.ForeignKey('user.id')),
    db.Column('room_id', db.Integer, db.ForeignKey('room.id'))
)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    permissions = db.Column(db.Integer)

    def __init__(self, name, perms=()):
        self.name = name
        self.permissions = 0
        for perm in perms:
            self.permissions |= perm
    
    def __contains__(self, perm):
        return bool(self.permissions & (1<<perm.value))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    password = db.Column(db.String(120))

    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    role = db.relationship('Role', backref='users')

    surveys = db.relationship('Survey', lazy='dynamic', backref='user')
    rooms = db.relationship('Room', secondary=user_rooms, backref=db.backref('users', lazy='dynamic'), lazy='dynamic')

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    passkey = db.Column(db.String(120))
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship('User')

    def __init__(self, name, creator, passkey):
        self.name = name
        self.creator = creator
        self.passkey = passkey

    @property
    def questions(self):
        return [ sv for sv in self.surveys if len(sv.options)==0 ]

    @property
    def proper_surveys(self):
        return [ sv for sv in self.surveys if len(sv.options)>0 ]

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')
    option = db.Column(db.Integer)
    survey_id = db.Column(db.Integer, db.ForeignKey('survey.id'))

class Survey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    closed = db.Column(db.Boolean)
    options = db.Column(db.PickleType)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    room = db.relationship('Room', backref='surveys')
    votes = db.relationship('Vote', lazy='dynamic', backref='survey')

    def __init__(self, title, options, room):
        self.title = title
        self.options = options
        self.room = room
        self.closed = False

    def cast_vote(self, user, option):
        self.votes.filter_by(uid=uid).delete()
        vote = Vote()
        vote.user = user
        if option and option not in range(len(self.options)):
            raise ValueError('Invalid option index')
        vote.option = option
        vote.survey = self
        db.session.add(vote)
        db.session.commit()
    
    @lru_cache()
    def count_votes(self):
        res = dict(db.session.query(func.count(Vote.option), Vote.option)\
                .filter(Vote.survey_id==self.id)\
                .group_by(Vote.option)\
                .all())
        return [(opt, res.get(i, 0)) for i,opt in enumerate(self.options)]

    def total_votes(self):
        return self.votes.count()

    @property
    def json(self):
        if self.closed:
            return {'title': self.title,
                    'results': self.count_votes(),
                    'total': self.total_votes}
        else:
            return {'title': self.title,
                    'options': self.options}


if __name__ == '__main__':
    if '--debug' in sys.argv:
        app.debug = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    if '--create-db' in sys.argv:
        db.create_all()
        participant = Role('admin', DEFAULT_PARTICIPANT)
        lecturer    = Role('admin', DEFAULT_LECTURER)
        db.session.add(lecturer)
        db.session.add(participant)
        db.session.commit()
    else:
         app.run()
