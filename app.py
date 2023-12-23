import os
from db import db
from flask import Flask, request
import json
from db import User
from db import Session
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
    return success_response(users)
    
@app.route("/api/users/", methods=["POST"])
def create_user():
    """
    Endpoint for creating a user
    """
    body = json.loads(request.data) 
    new_user = User(
        username=body.get("username"),
        pfp=body.get("pfp"),
        skin=body.get("skin")
    )
    db.session.add(new_user)
    db.session.commit()
    return success_response(new_user.serialize())

@app.route("/api/users/<int:user_id>/", methods=["GET"])
def get_user(user_id):
    """
    Endpoint for getting a user
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found")
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)