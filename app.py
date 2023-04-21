from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/db_name'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False)
    team = db.Column(db.String(100), unique=False)
    wins = db.Column(db.Integer)
    losses = db.Column(db.Integer)
    score_for = db.Column(db.Integer)
    score_against = db.Column(db.Integer)

    def __init__(self, name, team, wins=0, losses=0, score_for=0, score_against=0):
        self.name = name
        self.team = team
        self.wins = wins
        self.losses = losses
        self.score_for = score_for
        self.score_against = score_against

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user2_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    user1_score = db.Column(db.Integer)
    user2_score = db.Column(db.Integer)
    input_userid = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, user1_id, user2_id, user1_score, user2_score, input_userid):
        self.user1_id = user1_id
        self.user2_id = user2_id
        self.user1_score = user1_score
        self.user2_score = user2_score
        self.input_userid = input_userid

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'team', 'wins', 'losses', 'score_for', 'score_against')

class MatchSchema(ma.Schema):
    class Meta:
        fields = ('id', 'user1_id', 'user2_id', 'date', 'user1_score', 'user2_score', 'input_userid')

user_schema = UserSchema()
users_schema = UserSchema(many=True)
match_schema = MatchSchema()
matches_schema = MatchSchema(many=True)

@app.route('/register', methods=['POST'])
def register_user():
    name = request.json['name']
    team = request.json['team']
    new_user = User(name, team)
    db.session.add(new_user)
    db.session.commit()
    return user_schema.jsonify(new_user)

@app.route('/users', methods=['GET'])
def get_all_users():
    all_users = User.query.all()
    return users_schema.jsonify(all_users)

@app.route('/user/<id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    return user_schema.jsonify(user)

@app.route('/user/<id>', methods=['PUT'])
def update_user(id):
    user = User.query.get(id)
    user.name = request.json['name']
    db.session.commit()
    return user_schema.jsonify(user)

@app.route('/user/<id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    return user_schema.jsonify(user)

@app.route('/matches', methods=['GET'])
def get_all_matches():
    all_matches = Match.query.all()
    return matches_schema.jsonify(all_matches)

@app.route('/add/match', methods=['POST'])
def add_match():
    user1_id = request.json['user1_id']
    user2_id = request.json['user2_id']
    user1_score = request.json['user1_score']
    user2_score = request.json['user2_score']
    input_userid = request.json['input_userid']

    new_match = Match(user1_id, user2_id, user1_score, user2_score, input_userid)
    db.session.add(new_match)

    user1 = User.query.get(user1_id)
    user2 = User.query.get(user2_id)

    user1.score_for += user1_score
    user2.score_for += user2_score
    user1.score_against += user2_score
    user2.score_against += user1_score

    if user1_score > user2_score:
        user1.wins += 1
        user2.losses += 1
    elif user1_score < user2_score:
        user1.losses += 1
        user2.wins += 1

    db.session.commit()

    return match_schema.jsonify(new_match)

if __name__ == '__main__':
    app.run(debug=True)

