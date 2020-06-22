from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from sqlalchemy import or_

from datetime import datetime
from datetime import timedelta

db = SQLAlchemy()

# all classes inherit from db.Model. This allows for the class to have some built-in relationship with SQLAlchemy to interact with the database.
#__str__ is the built-in function in python, used in classes for string representation of object.

# -------------------    Users  ----------------------# #----1----#

class User(db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, unique = True)
    password = db.Column(db.String, nullable = False)
    name = db.Column(db.String, nullable = False)

    age = db.Column(db.Integer, nullable = True)
    gender = db.Column(db.String, nullable = True)
    height = db.Column(db.String, nullable = True)
    weight = db.Column(db.String, nullable = True)
    ethnicity = db.Column(db.String, nullable = True)
    orientation = db.Column(db.String, nullable = True)
    job = db.Column(db.String, nullable = True)
    interests =  db.Column(db.Text, nullable = True)
    favorite = db.Column(db.Text, nullable = True)
    life = db.Column(db.Text, nullable = True)
    bucket =  db.Column(db.Text, nullable = True)
    thoughts = db.Column(db.Text, nullable = True)
    img = db.Column(db.Text, nullable = True)

    
    posts = db.relationship('Post', backref = 'user', lazy = True , cascade="all, delete-orphan" )

    friend_sent = db.relationship('Request', backref = 'sender', lazy = 'dynamic', foreign_keys = 'Request.from_username', cascade="all, delete-orphan" )
    friend_recieved = db.relationship('Request', backref = 'reciever', lazy = 'dynamic', foreign_keys = 'Request.to_username', cascade="all, delete-orphan" )

    user_blocker = db.relationship('Block', backref = 'blocker', lazy = 'dynamic', foreign_keys = 'Block.from_username' , cascade="all, delete-orphan" )
    user_blocked = db.relationship('Block', backref = 'blocked', lazy = 'dynamic', foreign_keys = 'Block.to_username' , cascade="all, delete-orphan" )

    message_sent = db.relationship('Message', backref = 'sender', lazy = 'dynamic', foreign_keys = 'Message.from_username', cascade="all, delete-orphan" )
    message_recieved = db.relationship('Message', backref = 'reciever', lazy = 'dynamic', foreign_keys = 'Message.to_username', cascade="all, delete-orphan" )
    last_msg_username = db.Column(db.String, db.ForeignKey("User.username"), nullable = True) 

    def __str__(self):
        return f"{self.username}"

     


class Post(db.Model):
    __tablename__ = "Post"
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, db.ForeignKey("User.username"), nullable = False) 
    title = db.Column(db.String, default = "" , nullable = True)
    post = db.Column(db.Text, nullable = True)
    date = db.Column(db.String, nullable = False)

    
class Request(db.Model):
    __tablename__ = "Request"
    id = db.Column(db.Integer, primary_key = True)
    from_username = db.Column(db.String, db.ForeignKey("User.username"), nullable = False) 
    to_username = db.Column(db.String, db.ForeignKey("User.username"), nullable = False) 
    accepted = db.Column(db.Boolean, default = False, nullable=False)
    last_msg = db.Column(db.Text, nullable = True)
    unseen = db.Column(db.Integer, default = 0 , nullable = False)
    unseen_username = db.Column(db.String, nullable = True) 

    def __str__(self):
        return f"{self.from_username} to {self.to_username}"

class Block(db.Model):
    __tablename__ = "Block"
    id = db.Column(db.Integer, primary_key = True)
    from_username = db.Column(db.String, db.ForeignKey("User.username"), nullable = False) 
    to_username = db.Column(db.String, db.ForeignKey("User.username"), nullable = False) 
  

    def __str__(self):
        return f"{self.from_username} blocked {self.to_username}"

class Message(db.Model):
    __tablename__ = "Message"
    id = db.Column(db.Integer, primary_key = True)
    from_username = db.Column(db.String, db.ForeignKey("User.username"), nullable = False) 
    to_username = db.Column(db.String, db.ForeignKey("User.username"), nullable = False) 
    msg = db.Column(db.Text, nullable = True)
    date = db.Column(db.String, nullable = False)
  