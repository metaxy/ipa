#!/usr/bin/env python3

import sys
from functools import wraps, lru_cache
import json
from enum import Enum

import requests
from sqlalchemy import func
from flask import Flask, request, session, redirect, abort, render_template, url_for, jsonify
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
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PUSH_STREAM_URL'] = 'http://localhost/pub'
app.secret_key = 'jMHF20JxP49hfTp2rZIDFmRbPCcjw5p9'
db = SQLAlchemy(app)

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
        elif room.passkey != '' and not room.users.filter_by(name=session['uid']).exists():
            abort(403)
        request.room = room
        return func(*args, room=room, **kwargs)
    return wrapper

def auth(defaccess_or_fn=None, **kwargs):
    def deco(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not 'uid' in session:
                abort(403)
            user = request.user = User.query.filter_by(name=session['uid']).first()
            if not getattr(Perms, kwargs.get(request.method, defaccess_or_fn)) in user.permissions:
                abort(403)
            return func(*args, **kwargs)
        return wrapper

    if type(defaccess_or_fn) == type(auth):
        fn,defaccess_or_fn = defaccess_or_fn,defaccess_or_fn.__name__
        return deco(fn)
    return deco

def perform_login(pw_form, pw):
    return pw_form==pw

######################

@app.route('/')
@auth
def view_index():
    return redirect('/static/index.html')

@app.route('/api/login', methods=['POST'])
def login():
    # return status codes
    #TODO link the user creation with LDAP
    rd = request.get_json(True)

    if perform_login(rd['uid'], rd['password']):
        session['uid'] = rd['uid']
        user = request.user = User.query.filter_by(name=rd['uid']).first()
        if not user:
            user = User(name=session['uid'], role=Role.query.filter_by(name='participant').one())
            db.session.add(user)
            db.session.commit()
        return jsonify(result='ok')
    else:
        abort(403)

@app.route('/api/create_room', methods=['POST'])
@auth
def create_room():
    rd = request.get_json(True)
    if Room.query.filter_by(name=rd['name']).exists():
        abort(409)

    room = Room(rd['name'], request.user, rd['passkey'])
    request.user.rooms.append(room)
    db.session.add(room)        
    db.session.add(request.user)
    db.session.commit()
    return redirect(url_for('view_room', room=room.name))

@app.route('/api/list_rooms')
@auth('view_room')
def list_rooms():
    return jsonify(rooms=[r.name for r in Room.query.all()])
        
@app.route('/api/r/<room_name>/enter', methods=['POST'])
@auth('view_room')
def enter_room(room_name):
    room = Room.query.filter_by(name=room_name).one()

    rd = request.get_json(True)
    if rd['passkey'] == room.passkey:
        request.user.rooms.append(room)
        db.session.add(request.user)
        db.session.commit()
        return jsonify(result='ok')
    else:
        abort(403)

@app.route('/api/r/<room_name>')
@auth
@room
def view_room(room):
    return jsonify(name=room.name,
            questions=[q.as_dict() for q in room.questions],
            surveys=[sv.as_dict() for sv in room.surveys],
            user_is_lecturer=(room.creator == request.user))

@app.route('/api/r/<room_name>/create_question', methods=['POST'])
@auth
@room
def create_question(room):
    rd = request.get_json(True)
    q = Question(rd['test'], room, request.user)
    db.session.add(sv)
    db.session.commit()
    publish(room.name, 'question', q.as_dict())
    return jsonify(result='ok')

@app.route('/api/r/<room_name>/create_survey', methods=['POST'])
@auth
@room
def create_survey(room):
    rd = request.get_json(True)
    opts = rd['options']

    if len(opts) not in range(2, MAX_OPTS+1):
        abort(400)

    sv = Survey(rd['title'], opts, room)
    db.session.add(sv)
    db.session.commit()

    publish(room.name, 'survey', sv.as_dict())
    return jsonify(result='ok')

@app.route('/api/r/<room_name>/s/<int:survey_id>/vote', methods=['POST'])
@auth
@room
def vote_survey(room, survey_id):
    sv = Survey.query.get_or_404(survey_id)

    rd = request.get_json(True)
    op = int(rd['option'])
    if not val in range(0, len(sv.options)) and val:
        abort(400)

    sv.cast_vote(request.user, val)
    return jsonify(result='ok')

@app.route('/api/r/<room_name>/q/<int:question_id>/vote', methods=['POST'])
@auth
@room
def vote_question(room, question_id):
    q = Question.query.get_or_404(question_id)
    q.cast_vote(request.user)
    return jsonify(result='ok')

@app.route('/api/r/<room_name>/s/<int:survey_id>/close', methods=['POST'])
@auth
@room
def close_survey(room, survey_id):
    sv = Survey.query.get_or_404(survey_id)
    sv.closed = True
    db.session.add(sv)
    db.session.commit()
    return jsonify(result='ok')

@app.route('/api/r/<room_name>/q/<int:question_id>/delete', methods=['POST'])
@auth
@room
def delete_question(room, question_id):
    sv = Question.query.get_or_404(question_id)
    db.session.delete(sv)
    db.session.commit()
    return jsonify(result='ok')

# ask for increased/decreased tempo
@app.route('/api/r/<room_name>/t/<action>', methods=['POST'])
@auth
@room
def vote_tempo(room_id, action):
    room = Room.query.get_or_404(room_id)

    if action not in ('up', 'down'):
        abort(400)

    publish(room.name, 'tempo', action)
    return jsonify(result='ok')

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

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')

    option = db.Column(db.Integer)
    survey_id = db.Column(db.Integer, db.ForeignKey('survey.id'))
    survey = db.relationship('Survey')
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    question = db.relationship('Question')

    def __init__(self, survey_or_question, user, option=0):
        if type(survey_or_question) == Survey:
            self.survey = survey_or_question
        else:
            self.question = survey_or_question
        self.user, self.option = user, option

class Survey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    closed = db.Column(db.Boolean)
    options = db.Column(db.PickleType)

    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    room = db.relationship('Room', backref='surveys')

    votes = db.relationship('Vote', lazy='dynamic')

    def __init__(self, title, options, room):
        self.title = title
        self.options = options
        self.room = room
        self.closed = False

    def cast_vote(self, user, option):
        self.votes.filter_by(uid=user.id).delete()
        vote = Vote(self, user, option)
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

    def as_dict(self):
        if self.closed:
            return {'id': self.id,
                    'title': self.title,
                    'options': self.options,
                    'results': self.count_votes(),
                    'total': self.total_votes}
        else:
            return {'id': self.id,
                    'title': self.title,
                    'options': self.options}

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)

    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship('User')

    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    room = db.relationship('Room', backref='questions')

    votes = db.relationship('Vote', lazy='dynamic')

    def __init__(self, text, room, creator):
        self.text = text
        self.room = room
        self.creator = creator

    def cast_vote(self, user):
        self.votes.filter_by(uid=user.id).delete()
        vote = Vote(self, user)
        db.session.add(vote)
        db.session.commit()
    
    def total_votes(self):
        return self.votes.count()

    def as_dict(self):
        return {'id': self.id,
                'text': self.text,
                'votes': self.total_votes()}

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-c', '--create-db', action='store_true')
    parser.add_argument('-p', '--port', type=int, default=None)
    args = parser.parse_args()

    if args.debug:
        app.debug = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    if args.create_db:
        db.create_all()
        participant = Role('participant', DEFAULT_PARTICIPANT)
        lecturer    = Role('lecturer', DEFAULT_LECTURER)
        db.session.add(lecturer)
        db.session.add(participant)
        db.session.commit()
    else:
        if args.port is not None:
            app.config['SERVER_NAME'] = 'localhost:'+str(args.port)
        app.run()
