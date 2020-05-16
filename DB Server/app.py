from flask import Flask, flash, redirect, render_template, request, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import json
import datetime
import logging
import sys
from passlib.hash import sha256_crypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:mohit123@localhost:3306/socialnetwork?autocommit=True'
db = SQLAlchemy(app)
dbString = ['mysql+pymysql://root:mohit123@localhost:3306/socialnetwork?autocommit=True','mysql+pymysql://root:mohit123@localhost:3306/socialnetwork2?autocommit=True'] 

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

def jsonify(data):
    res=[]
    try:
        if len(data._saved_cursor._result.rows)!=0:
            for datum in data:
                res.append(dict(datum.items()))
    except:
        if len(data)!=0:
            for datum in data:
                try:
                    res.append(dict(datum.items()))
                except:
                    res.append(datum)
    return json.dumps(res)

def hash(userId):
    return int(userId)%len(dbString)

def changeDB(hashId):
    print("Accessing database ",hashId," with url ",app.config['SQLALCHEMY_DATABASE_URI'])
    app.config['SQLALCHEMY_DATABASE_URI']=dbString[hashId]

@app.route('/register/<email>/<password>/<firstName>/<lastName>/<status>', methods=['GET'])
def register(email,password,firstName,lastName,status):
    rows=[]
    newUserId=0
    for i in range(len(dbString)):
        changeDB(i)
        row=db.engine.execute("select userId from Users order by userId desc limit 1;")
        row=jsonify(row)
        row=json.loads(row)
        if len(row)!=0:
            rows.append(row[0]['userId'])
    if len(rows)>0:
        newUserId=max(rows)+1
    changeDB(hash(newUserId))
    password=sha256_crypt.encrypt(password)
    db.engine.execute("insert into Users (userId,email,password,firstName,lastName,status) values (%s,'%s','%s','%s','%s','%s')"%(newUserId,email,password,firstName,lastName,status))
    return json.dumps(True)

@app.route('/login/<email>/<password>', methods=['GET'])
def login(email,password):
    rows=[]
    userRecord=None
    result=False
    verified=False
    for i in range(len(dbString)):
        changeDB(i)
        row=db.engine.execute("select * from Users;")
        row=jsonify(row)
        row=json.loads(row)
        rows.extend(row)
    print(email)
    for row in rows:
        if row['email']==email:
            userRecord=row
            break
    if userRecord:
        print(userRecord)
        verified=sha256_crypt.verify(password,userRecord['password'])
    if verified:
        return json.dumps(userRecord)
    return json.dumps(result)

@app.route('/getUserInfo/<userId>', methods=['GET'])
def getUserInfo(userId):
    changeDB(hash(userId))
    row=db.engine.execute("select * from Users where userId=%s"%(userId))
    row=jsonify(row)
    return (row)

@app.route('/searchUsers/<name>', methods=['GET'])
def searchUsers(name):
    rows=[]
    for i in range(len(dbString)):
        changeDB(i)
        row=db.engine.execute("SELECT * FROM Users WHERE firstName LIKE '%"+name+"%' OR lastName LIKE '%"+name+"%'")
        rows.extend(row)
    return jsonify(rows)

@app.route('/isFriend/<userId>/<friendId>', methods=['GET'])
def isFriend(userId,friendId):
    changeDB(hash(userId))
    rows1=db.engine.execute("select * from Friends where userId=%s and friendId=%s"%(userId,friendId))
    rows1=jsonify(rows1)
    changeDB(hash(friendId))
    rows2=db.engine.execute("select * from Friends where userId=%s and friendId=%s"%(friendId,userId))
    rows2=jsonify(rows2)
    rows=rows1+rows2
    return json.dumps(len(rows)>4)

@app.route('/getFriends/<userId>', methods=['GET'])
def getFriends(userId):
    changeDB(hash(userId))
    rows=db.engine.execute("select friendId from Friends where userId=%s"%(userId))
    rows=jsonify(rows)
    return (rows)

@app.route('/makeFriends/<userId>/<friendId>', methods=['GET'])
def makeFriends(userId,friendId):
    changeDB(hash(userId))
    db.engine.execute("insert into Friends (userId,friendId) values (%s,%s)"%(userId,friendId))
    changeDB(hash(friendId))
    db.engine.execute("insert into Friends (userId,friendId) values (%s,%s)"%(friendId,userId))
    return json.dumps(True)

@app.route('/createPost/<userId>/', methods=['GET','POST'])
def createPost(userId):
    changeDB(hash(userId))
    title=request.values.get('title')
    post=request.values.get('text')
    print(title,post)
    dateTime=datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    print('NOT DONEEEE')
    db.engine.execute("insert into Posts (userId,title,text,dateTime) values (%s,'%s','%s','%s')"%(userId,title,post,dateTime))
    print('DONEEEE')
    return json.dumps(True)

@app.route('/getUserPosts/<userId>', methods=['GET'])
def getUserPosts(userId):
    changeDB(hash(userId))
    rows=db.engine.execute("select * from Posts where userId=%s"%(userId))
    rows=jsonify(rows)
    return (rows)

@app.route('/deletePost/<userId>/<postId>', methods=['GET'])
def deletePost(userId,postId):
    changeDB(hash(userId))
    db.engine.execute("delete from Posts where userId=%s and postId=%s"%(userId,postId))
    return json.dumps(True)

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0', port=int(sys.argv[1]))
