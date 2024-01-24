from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    """
    User Model
    """
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    pfp = db.Column(db.String, nullable=False)
    lvl = db.Column(db.Integer, nullable=False)
    skin = db.Column(db.String, nullable=False)
    total_time = db.Column(db.Float, nullable=False)
    sessions = db.relationship("Session", cascade="delete")

    def __init__(self, **kwargs):
        """
        Initialize a User
        """
        self.username = kwargs.get("username", "")
        self.password = kwargs.get("password", "")
        self.pfp = kwargs.get("pfp", "")
        self.lvl = 0
        self.skin = kwargs.get("skin", "default")
        self.total_time = 0.0
    def serialize(self):
        """
        Serialize a User
        """
        return {
            "id": self.id,
            "username": self.username,
            "pfp": self.pfp,
            "time": self.total_time,
            "lvl": self.lvl,
            "skin": self.skin,
            "sessions": [session.serialize() for session in self.sessions]
        }

    
class Session(db.Model):
    """
    Session model
    """
    __tablename__ = "session"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    start = db.Column(db.Float, nullable=False)
    time_elapsed = db.Column(db.Float, nullable=False)
    active = db.Column(db.Boolean, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    

    def __init__(self, **kwargs):
        """
        Initialize a session
        """
        self.start = kwargs.get("start", 0.0)
        self.time_elapsed = 0.0
        self.active = True
        self.user_id = kwargs.get("user_id", 1)

    def serialize(self):
        """
        Serialize a session
        """
        return {
            "id": self.id,
            "start": self.start,
            "active": self.active,
            "timeElapsed": self.time_elapsed,
            "user": self.user_id
        }

