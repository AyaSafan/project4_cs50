import os
import psycopg2
import requests
import json
from functools import wraps
from flask import abort, jsonify
from functools import wraps
from flask import Flask,g,flash, render_template, request, session, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import Flask, render_template, request  
from sqlalchemy import func
from flask_socketio import SocketIO, emit

from models import * 
import datetime
import base64



def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:            
            return redirect(url_for('index'))
    return wrap

users = {}

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ['DATABASE_URL']
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  
app.secret_key =  os.getenv("SECRET_KEY")
db.init_app(app)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
socketio = SocketIO(app)


#------------------------------------------------Render Routes----------------------------------------------------------------
@app.route("/")
def index():
    try: 
        logged = session['logged_in']
    except:
        logged = False
        session['username'] = None

    return render_template("LastFriend_templates/index.html" , logged = logged , session_username = session['username'])

@app.route("/signup", methods=["POST"]) 
def signup():
    session["username"]= request.form.get("sign_username")
    session["name"]= request.form.get("sign_name")
    password = request.form.get("sign_password")

    try:
        image = request.files["sign_img"]
        image_read = image.read()
        image_64_encode = base64.encodestring(image_read)
        image_string = image_64_encode.decode('utf-8')        
    except:
        image_string=""
        
    
    if User.query.filter_by(username=session["username"]).count()==0:
        user=User(username=session["username"], password=password)

        user.name = request.form.get("sign_name")
        if request.form.get("sign_age") != "":
            user.age = request.form.get("sign_age")
        user.gender = request.form.get("sign_gender")
        user.height = request.form.get("sign_height")
        user.weight = request.form.get("sign_weight")
        user.ethnicity = request.form.get("sign_ethnicity")
        user.orientation = request.form.get("sign_orientation")
        user.job = request.form.get("sign_job")
        user.interests =  request.form.get("sign_interests")
        user.favorite = request.form.get("sign_favorite")
        user.life = request.form.get("sign_life")
        user.bucket =  request.form.get("sign_bucket")
        user.thoughts = request.form.get("sign_thoughts")
        user.img = image_string
        
        db.session.add(user)
        db.session.commit()
        session['logged_in']=True

        flash('Successfully signed up and logged in.')
        return redirect(url_for('profile'))            
    else: 
        flash('Error! Username is taken.')
        return redirect(url_for('index'))       

@app.route("/login", methods=["POST"]) 
def login():
    username = request.form.get("log_username")
    password =  request.form.get("log_password")
    user= User.query.filter(and_( User.username == username, User.password == password)).first()
    if  user == None: 
        flash('Error! Username and Password do not match.')
        return redirect(url_for('index'))  
    session['logged_in']=True
    session['username'] = username
    session['name'] = user.name
    return redirect(url_for('profile'))

@app.route("/profile")
@login_required
def profile():
    user = User.query.filter_by(username=session['username']).first()
    Posts = []
    posts= user.posts
    for post in posts:
        Posts.append(post)
    return render_template("LastFriend_templates/profile.html" , User = user, Posts = Posts , session_username = session['username'], session_name=session['name'])

@app.route("/profile_user/<string:username>")
@login_required
def profile_user(username):
    user = User.query.filter_by(username=username).first()
    # If the user searched for isn't found abort with 404 error / without it an empty profile loads without error
    if user == None:
        abort(404)
    #Get the user's posts
    Posts = []
    posts= user.posts
    for post in posts:
        Posts.append(post) 

    # show if user is a friend, blocked, request

    #recieved friend requests to that username from session user ---> session user sent request
    sent_request = user.friend_recieved.filter_by(from_username=session['username']).first()
    #sent friend requests from that username to session user ---> session user recieved request
    recieved_request = user.friend_sent.filter_by(to_username=session['username']).first()
    # are users friends boolen
    if recieved_request != None:
        friends = recieved_request.accepted 
    elif sent_request != None:
        friends = sent_request.accepted
    else:
        friends = None

    #recieved block to that username from session user ---> session user sent block
    session_blocker = user.user_blocked.filter_by(from_username=session['username']).first()
    #sent friend requests from that username to session user ---> session user recieved block
    session_blocked = user.user_blocker.filter_by(to_username=session['username']).first()
    
    #---> session user sent block or not
    if session_blocker != None:
        block = True
    else:
        block = False

    #---> session user recieved block
    if session_blocked != None:
        abort(404)    

    return render_template("LastFriend_templates/profile_user.html", User = user , Posts = Posts , recieved_request = recieved_request , sent_request = sent_request, friends = friends, block = block ,  session_username = session['username'], session_name=session['name'])
        

@app.route("/messages")
@login_required
def messages():
    # Get sesssion friends
    Friends=[]
    friends = Request.query.filter(or_(and_(Request.from_username == session["username"], Request.accepted == True),and_(Request.to_username == session["username"], Request.accepted == True))).all()
    for friend in friends:
        Friends.append(friend)
    # Get username of last messaged friend to open
    user =User.query.filter_by(username= session['username']).first()
    last_msg_username = user.last_msg_username

    # Get all messages from or to the session username
    Messages=[]
    messages = Message.query.filter(or_(and_(Message.from_username == session["username"],  Message.to_username == last_msg_username  ), and_(Message.to_username == session["username"],  Message.from_username == last_msg_username  ) )).all()
    for message in messages:
        Messages.append(message)
    return render_template("LastFriend_templates/messages.html", Friends = Friends , last_msg_username = last_msg_username, Messages = Messages,  session_username = session['username'], session_name=session['name'])

@app.route("/friends" ,  methods=["GET","POST"])
def friends():
    Friends=[]
    friends = Request.query.filter(or_(and_(Request.from_username == session["username"], Request.accepted == True),and_(Request.to_username == session["username"], Request.accepted == True))).all()
    for friend in friends:
        Friends.append(friend)
    
    Requests =[]
    reqests = Request.query.filter(and_(Request.to_username == session["username"], Request.accepted == False)).all()
    for reqest in reqests:
        Requests.append(reqest)

    Blocks =[]
    blocks = Block.query.filter(Block.from_username == session["username"]).all()
    for block in blocks:
        Blocks.append(block)

    Results = []
    if request.method == "POST":
        name = request.form.get("name")
        gender = request.form.get("gender")
        min_age = request.form.get("min_age")
        max_age = request.form.get("max_age")

        if (min_age == "" and max_age == ""):
            results= User.query.filter(and_(or_(User.name.like("%"+name+"%") , User.username.like("%"+name+"%")), User.gender.like("%"+gender+"%"))).all()
            for result in results:
                Results.append(result)
        elif (min_age == "" and max_age != ""):
            results= User.query.filter(and_(or_(User.name.like("%"+name+"%") , User.username.like("%"+name+"%")), User.gender.like("%"+gender+"%"), User.age <= max_age)).all()
            for result in results:
                Results.append(result)
        elif (min_age != "" and max_age == ""):
            results= User.query.filter(and_(or_(User.name.like("%"+name+"%") , User.username.like("%"+name+"%")), User.gender.like("%"+gender+"%"), User.age >= min_age)).all()
            for result in results:
                Results.append(result)  
        else:
            results= User.query.filter(and_(or_(User.name.like("%"+name+"%") , User.username.like("%"+name+"%")) , User.gender.like("%"+gender+"%"), User.age <= max_age, User.age >= min_age)).all()
            for result in results:
                Results.append(result) 

    #users blocking the session user to remove from the search results
    Removes=[]
    blocked_to_session = Block.query.filter(Block.to_username == session["username"]).all()
    for block in blocked_to_session:
        Removes.append(block) 

    for Result in Results:
        #remove session user from results
        if Result.username == session['username']:
            Results.remove(Result)
        #removes users blocking session
        for Remove in Removes:
            if Result.username == Remove.from_username:
                Results.remove(Result)

   
    
    return render_template("LastFriend_templates/friends.html" , Friends = Friends , Requests = Requests, Blocks=Blocks, Results = Results,  session_username = session['username'], session_name=session['name'])

#----------------------------------- profile settings------------------------------------------------
@app.route("/profile_pic", methods=["POST"]) 
def profile_pic():
    try:
        image = request.files["img"]
        image_read = image.read()
        image_64_encode = base64.encodestring(image_read)
        image_string = image_64_encode.decode('utf-8')        
    except:
        image_string=""

    user = User.query.filter_by(username=session['username']).first()   
    user.img = image_string
    db.session.commit()

    return redirect(url_for('profile'))       

@app.route("/profile_edit", methods=["POST"]) 
def profile_edit():
    user = User.query.filter_by(username=session['username']).first() 
    
    user.name = request.form.get("sign_name")
    if request.form.get("sign_age") != "":
        user.age = request.form.get("sign_age")
    user.gender = request.form.get("sign_gender")
    user.height = request.form.get("sign_height")
    user.weight = request.form.get("sign_weight")
    user.ethnicity = request.form.get("sign_ethnicity")
    user.orientation = request.form.get("sign_orientation")
    user.job = request.form.get("sign_job")
    user.interests =  request.form.get("sign_interests")
    user.favorite = request.form.get("sign_favorite")
    user.life = request.form.get("sign_life")
    user.bucket =  request.form.get("sign_bucket")
    user.thoughts = request.form.get("sign_thoughts")

    db.session.commit()
    return redirect(url_for('profile'))  

@app.route("/logout" , methods=["GET", "POST"])
@login_required
def logout():
    users.pop(session['username'])
    session.pop('logged_in', None)
    session.clear()    
    return redirect(url_for('index'))

@app.route("/delete_account" , methods=["POST"])
@login_required
def delete_account():
    user = User.query.filter_by(username=session['username']).first()
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('logout'))

#----------------------------------------Profile Post------------------------------------------------------------
@socketio.on("new post")
@login_required
def post(data):
    username = session["username"]
    title = data["title"]
    post = data["post"]
    date = str(datetime.datetime.now().strftime("%d %b. %Y @%H:%M"))
    new_post = Post(username = username, title = title, post= post, date = date)
    db.session.add(new_post)
    db.session.flush()
    post_id = new_post.id 
    db.session.commit()    
    emit("announce post", {'title': title, 'post': post, 'date': date, 'username': username, 'post_id': post_id}, broadcast=True)


@socketio.on('emit_delete_post')
def emit_delete_post(data):
    post_id = int(data['post_id'])
    post =Post.query.get(post_id)

    db.session.delete(post)
    db.session.commit()   
 
    emit('announce_delete_post', {'post_id': post_id} , broadcast=True)

#----------------------------------profile_user options----------------------------------------------

@app.route("/send_friend_request" , methods=["POST"])
@login_required
def send_friend_request():
    #check the username you are sending request to exists
    profile_user_username = request.form.get("profile_user_username")
    if User.query.filter_by(username=profile_user_username).count()==0:
        return jsonify({"success": "404"})
    #check the username you are sending request to isn't blocking you
    block = Block.query.filter(and_(Block.to_username == session["username"], Block.from_username == profile_user_username)).first()
    if (block != None):
        return jsonify({"success": "404"})
    #check the username you are sending request to didn't send you a request already
    req = Request.query.filter(and_(Request.to_username == session["username"], Request.from_username == profile_user_username)).first()
    if (req == None):
        # create request from the session user to the opend profile_user  
        req = Request(from_username = session["username"], to_username= profile_user_username)
        db.session.add(req)
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"success": False})

@app.route("/remove_friend_request" , methods=["POST"])
@login_required
def remove_friend_request():
    #check the username you are removing their request to exists
    profile_user_username = request.form.get("profile_user_username")
    if User.query.filter_by(username=profile_user_username).count()==0:
        return jsonify({"success": "404"})
     #check the username you are removing their request to isn't blocking you
    block = Block.query.filter(and_(Block.to_username == session["username"], Block.from_username == profile_user_username)).first()
    if (block != None):
       return jsonify({"success": "404"})
    #check such a request exists
    req = Request.query.filter(or_(and_(Request.from_username == session["username"], Request.to_username == profile_user_username),and_(Request.from_username == profile_user_username , Request.to_username == session["username"]))).first()
    if (req != None):
        db.session.delete(req)
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"success": False})

@app.route("/accept_friend_request" , methods=["POST"])
@login_required
def accept_friend_request():
    #check the username you are accepting their request to exists
    profile_user_username = request.form.get("profile_user_username")
    if User.query.filter_by(username=profile_user_username).count()==0:
        return jsonify({"success": "404"})
    #check the username you are accepting their request to isn't blocking you
    block = Block.query.filter(and_(Block.to_username == session["username"], Block.from_username == profile_user_username)).first()
    if (block != None):
        return jsonify({"success": "404"})
    #check such a request exists
    req = Request.query.filter(and_(Request.to_username == session["username"], Request.from_username == profile_user_username)).first()
    if (req != None):
        req.accepted = True
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"success": False})

@app.route("/block" , methods=["POST"])
@login_required
def block():
    #check the username you are blocking exists
    profile_user_username = request.form.get("profile_user_username")
    if User.query.filter_by(username=profile_user_username).count()==0:
        return jsonify({"success": "404"})
    #check the username isn't blocking you
    block = Block.query.filter(and_(Block.to_username == session["username"], Block.from_username == profile_user_username)).first()
    if (block != None):
        return jsonify({"success": "404"})

    #check the username is already blocked
    block = Block.query.filter(and_(Block.from_username == session["username"], Block.to_username == profile_user_username)).first()
    if (block != None):
        return jsonify({"success": False})
    # if there is requests between usernames delete them
    req = Request.query.filter(or_(and_(Request.from_username == session["username"], Request.to_username == profile_user_username),and_(Request.from_username == profile_user_username , Request.to_username == session["username"]))).first()
    if req != None: 
        db.session.delete(req)
    #block the given profile_user
    block = Block(from_username = session["username"], to_username= profile_user_username)
    db.session.add(block)
    db.session.commit()

    # if the blocked user is opening the chat of the blocker then set it to none
    user =User.query.filter_by(username= profile_user_username).first()
    if user.last_msg_username == session["username"]:
        user.last_msg_username = None

    return jsonify({"success": True})

@app.route("/unblock" , methods=["POST"])
@login_required
def unblock():
    #check the username you are unblocking exists
    profile_user_username = request.form.get("profile_user_username")
    if User.query.filter_by(username=profile_user_username).count()==0:
        return jsonify({"success": "404"})
    #delete block
    block = Block.query.filter(and_(Block.from_username == session["username"], Block.to_username == profile_user_username)).first()
    db.session.delete(block)
    db.session.commit()
    return jsonify({"success": True})

#-----------------------------------------General-----------------------------------------------------------


@socketio.on('session_sid', namespace='/private')
@login_required
def session_sid():
    users[session['username']] = request.sid
    print('Username added!')

@socketio.on('emit_notification', namespace='/private')
@login_required
def emit_notification(data):
    if data['reciever_username'] in users:
        reciever_sid = users[data['reciever_username']]
        notification = data['notification']
        emit('announce_notification',  {"notification": notification, "sender": session["username"]}, room=reciever_sid)

@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404

#------------------------------------------messages-----------------------------------------------------
@app.route("/last_msg_username" , methods=["POST"])
@login_required
def last_msg_username():
    #check the username you are sending measage to exists
    last_msg_username = request.form.get("last_msg_username")
    user =User.query.filter_by(username=last_msg_username).first()
    if user==None:
        return jsonify({"success": False})

    #check the username you are sending measage to is a friend
    friend = Request.query.filter(or_(and_(Request.from_username == session["username"], Request.to_username == last_msg_username, Request.accepted == True),and_(Request.from_username == last_msg_username, Request.to_username == session["username"], Request.accepted == True))).first()
    if friend==None:
        return jsonify({"success": False})

    else:
        user =User.query.filter_by(username= session['username']).first()
        user.last_msg_username = last_msg_username
        #if the chat being opened is the last unseen chat --> unseen now is zero
        if friend.unseen_username == last_msg_username:
            friend.unseen = 0
            friend.unseen_username = None
        db.session.commit()
        return jsonify({"success": True})

@app.route("/reset_unseen_counter" , methods=["POST"])
@login_required
def reset_unseen_counter():
    friend_username = request.form.get("friend_username")
    friend = Request.query.filter(or_(and_(Request.from_username == session["username"], Request.to_username == friend_username, Request.accepted == True),and_(Request.from_username == friend_username, Request.to_username == session["username"], Request.accepted == True))).first()
    if friend != None:
        friend.unseen = 0
        friend.unseen_username = None
        db.session.commit() 
        return jsonify({"success": True})  
    return jsonify({"success": False})  

@socketio.on('emit_msg', namespace='/private')
@login_required
def emit_msg(data):
    session_sid = users[session["username"]]
    block = Block.query.filter(or_(and_(Block.from_username == session["username"], Block.to_username == data['reciever_username']),and_(Block.to_username == session["username"], Block.from_username == data['reciever_username']))).first()
    if block != None:
        user =User.query.filter_by(username= session['username']).first()
        user.last_msg_username = None
        db.session.commit()
        emit('failed_msg',{'alert': 'You can not send messages to this user' }, room=session_sid)

    else:
        friend = Request.query.filter(or_(and_(Request.from_username == session["username"], Request.to_username == data['reciever_username'], Request.accepted == True),and_(Request.from_username == data['reciever_username'], Request.to_username == session["username"], Request.accepted == True))).first()
        if friend == None:
            user =User.query.filter_by(username= session['username']).first()
            user.last_msg_username = None
            db.session.commit()
            emit('failed_msg',{'alert': 'You can not send messages to this user' }, room=session_sid)
        else:
            msg = data['msg']
            date = str(datetime.datetime.now().strftime("%d %b. %Y @%H:%M"))
            new_msg = Message(from_username = session['username'], to_username = data['reciever_username'], msg= msg, date = date)    
            db.session.add(new_msg)
            db.session.flush()
            msg_id = new_msg.id 
            #set friend last_msg         
            friend.last_msg = msg
            db.session.commit()

        
            #announce to sender            
            emit('announce_msg_me',  {"msg": msg, "sender": session["username"], 'reciever': data['reciever_username'],'date':date, 'msg_id':msg_id}, room=session_sid)
            #increase unseen counter
            friend = Request.query.filter(or_(and_(Request.from_username == session["username"], Request.to_username == data['reciever_username'], Request.accepted == True),and_(Request.from_username == data['reciever_username'], Request.to_username == session["username"], Request.accepted == True))).first()
            if friend != None:
                if friend.unseen_username !=  session["username"]:
                    friend.unseen_username =  session["username"]
                    friend.unseen = 0
                
                friend.unseen += 1
                counter = friend.unseen
                
            db.session.commit() 

            if data['reciever_username'] in users:
                reciever_sid = users[data['reciever_username']]        
                emit('announce_msg',  {"msg": msg, "sender": session["username"], 'reciever': data['reciever_username'], 'date':date, 'msg_id':msg_id, 'counter': counter}, room=reciever_sid)
                


@socketio.on('emit_delete_msg', namespace='/private')
@login_required
def emit_delete_msg(data):
    msg_id = int(data['msg_id'])
    msg=Message.query.get(msg_id)
    user_from = msg.from_username
    user_to = msg.to_username
    db.session.delete(msg)
    db.session.commit()
    
    from_sid = users[user_from]
    to_sid = users[user_to]
    emit('announce_delete', {'msg_id': msg_id} ,room=from_sid)
    emit('announce_delete', {'msg_id': msg_id} ,room=to_sid)

    
