from crypt import methods
from flask import Flask, render_template, request, flash, redirect, send_from_directory, session, jsonify
import os
from werkzeug.utils import secure_filename
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from functools import wraps
import datetime

##### SESSION CONTROL #####
class User:
    def startSession(self, user):
        #del user['password']
        session['logged_in'] = True
        session['user'] = user
        return (user)

    def signup(self):
        user2 = {
            "_id": uuid.uuid4().hex,
            "username": request.form.get("fname"),
            "password": request.form.get("lname")
        }
        user2['password'] = generate_password_hash(user2['password'])
        mongo.db.user.insert_one(user2)
        #return self.startSession(user2)
        #return jsonify(user2)
    
    def signout(self): #Ajouter un bouton
        session.clear()
        flash('You are now logged out')
        return redirect('/')

    def loggin (self):
        user2 = {
            "username": request.form.get("fname"),
            "password": request.form.get("lname")
        }
        return self.startSession(user2)


#Decorator that assure that we can not have access to certain pages if we are not logged in
def loggin_required(f):
    @wraps(f)
    def wrap(*arg, **kwargs):
        if 'logged_in' in session:
            return f(*arg, **kwargs)
        else:
            flash ('You should first log in')
            return redirect('/auth')
    return wrap

##### End SESSION CONTROL #####

##### MONGO CONFIGURATION #####
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/task2"
mongo = PyMongo(app)

##### END MONGO CONFIGURATION #####

##### ROUTES #####

# SIGN OUT 
@app.route('/user/signout')
def signout():
    return User().signout()

# HOMEPAGE
@app.route("/")
def home_page():
    online_users = mongo.db.users.find({})
    all_posts = list(mongo.db.posts.find())
    return render_template("list.html", users=online_users, posts = all_posts)

#Sign In
@app.route('/sign', methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("SignUp.html")
    else:
        lname = request.form.get("fname")
        fname = request.form.get("lname")
        if mongo.db.user.count_documents ({'username':lname}) !=0:
            flash ('This name is already used')
            return redirect('/sign')
        else:
            return render_template("authentification.html", lname=lname, fname=fname), User().signup()


#Authentification
@app.route('/auth', methods=["GET", "POST"])
def auth1 ():
    if request.method == "GET":
        return render_template("authentification.html")
    else:
        username = request.form.get("fname")
        password = request.form.get("lname")
        user = mongo.db.user.find_one({'username':username})
        if user and check_password_hash(user['password'], password) :
            User().loggin()
            flash('You are logged in, you can now write a post')
            #return render_template('list.html', username= username, passaword=password)
            return redirect ('/')

        else:
            flash('Username or password is not correct')
            return redirect (request.url)

#Join the blog
@app.route('/post', methods=(["GET","POST"]))
@loggin_required
def post():
    if request.method == "GET":
        return render_template("create_post_page.html")
    else:
        message = request.form.get('text')
        if not message:
            flash('Post can not be empty')
            return redirect(request.url)
        else : 
            time = str(datetime.datetime.now())
            time = time [:-10]
            #time = str(hexacte.minute) 
            mongo.db.posts.insert_one ({"post":message, "writter": session ['user']['username'], "time": time})
            all_posts = mongo.db.posts.find()
            return render_template("list.html", posts = all_posts)

    

if __name__ == "__main__":
    app.secret_key = 'many random bytes'
    app.run(host='localhost', port=5002, debug=True)