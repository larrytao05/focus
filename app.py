import os
from db import db
from flask import Flask, request
import json
from db import *
from datetime import datetime, timezone

"""
Created by Larry Tao on 12/20/23
"""

app = Flask(__name__)
db_filename = "forum.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()

# generalized response formats
def success_response(data, code=200):
    return json.dumps(data), code

def failure_response(message, code=404):
    return json.dumps({"error": message}), code

# routes
@app.route("/")
@app.route("/api/users/", methods=["GET"])
def get_all_users():
    """
    Endpoint for getting all users
    """
    users = [user.serialize() for user in User.query.all()]
    return success_response({"users":users})
    
@app.route("/api/users/<string:username>/", methods=["POST"])
def create_user(username):
    """
    Endpoint for creating a user
    """
    body = json.loads(request.data)
    user = User.query.filter_by(username=username).first()
    if user is not None:
        return failure_response("A user with this username already exists")
    if username is None or body.get("password") is None:
        return failure_response("Username or password not provided")
    new_user = User(
        username=username,
        pfp=body.get("pfp"),
        skin=body.get("skin"),
        password=body.get("password")
    )
    db.session.add(new_user)
    db.session.commit()
    return success_response(new_user.serialize())

@app.route("/api/users/<int:user_id>/", methods=["GET"])
def get_user(user_id):
    """
    Endpoint for getting a user by id
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found")
    return success_response(user.serialize())

@app.route("/app/users/<int:user_id>/friends/", methods=["GET"])
def get_friends(user_id):
    """
    Endpoint for getting a user's friends
    """


@app.route("/api/users/login/<string:username>/<string:password>/", methods=["GET"])
def login(username, password):
    """
    Endpoint for verifying login
    """
    user = User.query.filter_by(username=username).first()
    if user is None:
        return failure_response("user does not exist")
    if password != user.password:
        return failure_response("Invalid password")
    return success_response(user.serialize())

@app.route("/api/users/<int:user_id>/", methods=["DELETE"])
def delete_user(user_id):
    """
    Endpoint for deleting a user
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found")
    db.session.delete(user)
    db.session.commit()
    return success_response(user.serialize(), 201)

@app.route("/api/sessions/<int:user_id>/", methods=["POST"])
def create_session(user_id):
    """
    Endpoint for starting a work session
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found")
    current_sessions = Session.query.filter_by(user_id=user_id, active=True).first()    
    if current_sessions is not None:
        return failure_response("User already in an active session", 400)
    new_session = Session(
        start=datetime.now(timezone.utc).timestamp(),
        user_id=user_id
    )
    db.session.add(new_session)
    db.session.commit()
    return success_response(new_session.serialize())

@app.route("/api/sessions/<int:user_id>/", methods=["PUT"])
def end_session(user_id):
    """
    Endpoint for ending a session
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found")
    session = Session.query.filter_by(user_id=user_id, active=True).first()
    if session is None:
        return failure_response("No active sessions for this user")
    session.active = False
    session.time_elapsed = datetime.now(timezone.utc).timestamp() - session.start
    user.total_time += session.time_elapsed
    user.lvl = user.total_time // 3600
    db.session.commit()
    return success_response(session.serialize())
    
@app.route("/api/sessions/<int:user_id>/", methods=["DELETE"])
def cancel_session(user_id):
    """
    Endpoint for canceling an ongoing session
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found")
    session = Session.query.filter_by(user_id=user_id, active=True).first()
    if session is None:
        return failure_response("No active sessions")
    db.session.delete(session)
    db.session.commit()
    return success_response(session.serialize())

@app.route("/api/users/friends/<string:username1>/<string:username2>/", methods=["POST"])
def add_friend(username1, username2):
    """
    Endpoint for adding a friend
    """
    user1 = User.query.filter_by(username=username1).first()
    user2 = User.query.filter_by(username=username2).first()
    if user1 is None or user2 is None:
        return failure_response("Invalid user ids")
    if user2 in user1.friends:
        return failure_response("Users are already friends")
    request = Request(
        sender_id=user1.id,
        receiver_id=user2.id,
        accepted=False
    )
    db.session.add(request)
    db.session.commit()
    return success_response(user1.serialize())
    
@app.route("/api/users/friends/<string:username1>/<string:username2>/", methods=["PUT"])
def accept_request(username1, username2):
    """
    Endpoint for accepting a friend request
    Make sure receiver id comes first
    """
    user1 = User.query.filter_by(username=username1).first()
    user2 = User.query.filter_by(username=username2).first()
    if user1 is None or user2 is None:
        return failure_response("Invalid user ids")
    if user2 in user1.friends:
        return failure_response("Users are already friends")
    request = Request.query.filter_by(receiver_id=user1.id, sender_id=user2.id).first()
    if request is None:
        return failure_response("Friend request not found")
    user1.friends.append(user2)
    user2.friends.append(user1)
    db.session.delete(request)
    db.session.commit()
    return success_response(user1.serialize())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)