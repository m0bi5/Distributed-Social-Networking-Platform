from flask import Flask,request,Response,render_template,redirect,session
import logging,sys,requests
import urllib.parse
import json

app = Flask(__name__)
app.secret_key = "askjhahfsdhjf"
loadBalancer='http://localhost:5000'
myUrl='http://localhost:8000'

def dbInteractor(url,*args):
    url=url.replace(myUrl,loadBalancer)
    for arg in args:
        url+='/'+urllib.parse.quote(str(arg))

    response=requests.get(url)
    return response.json()

def setSession(info):
    for key in info:
        session[key]=str(info[key])

def removeSession():
    session.clear()     



@app.route('/login', methods=['POST','GET'])
def login():
    if request.method=="GET":
        return render_template('login.html')
    else:
        email=request.values.get('email')
        password=request.values.get('password')
        response=dbInteractor(request.url,email,password)
        if response:
            setSession(response)
            return redirect('/dashboard')
        else:
            return render_template('login.html',error='Login Failed')

@app.route('/logout', methods=['POST','GET'])
def logout():
    removeSession()
    return redirect('/login')
    

@app.route('/', methods=['POST','GET'])
def home():
    return redirect('/login')

@app.route('/register', methods=['POST','GET'])
def register():
    if request.method=="GET":
        return render_template('register.html')
    else:
        email=request.values.get('email')
        password=request.values.get('password') 
        firstName=request.values.get('firstName')
        lastName=request.values.get('lastName')
        status=request.values.get('status')
        response=dbInteractor(request.url,email,password,firstName,lastName,status)
        return redirect('/login')

@app.route('/dashboard', methods=['POST','GET'])
def dashboard():
    if len(session.keys())==0:
        return redirect('/login')
    friends=dbInteractor(request.host_url+'getFriends',session['userId'])
    friendsInfo=[]
    for friend in friends:
        friendsInfo+=dbInteractor(request.host_url+'getUserInfo',friend['friendId'])
    myPosts=dbInteractor(request.host_url+'getUserPosts',session['userId'])
    return render_template('dashboard.html',posts=myPosts,friends=friendsInfo)
    

#Profile Page
@app.route('/getUserPosts/<userId>', methods=['POST','GET'])
def profile(userId):
    isFriend=dbInteractor(request.host_url+'isFriend',session['userId'],userId)
    info=dbInteractor(request.host_url+'getUserInfo',userId)
    posts=dbInteractor(request.url)
    return render_template('profile.html',userPosts=posts,userInfo=info[0],isFriend=isFriend)

@app.route('/createPost/<userId>',methods=['POST'])
def createPost(userId):
    r=requests.post(loadBalancer+'/createPost/'+userId+'/',data={'title':request.values.get('title'),'text':request.values.get('text')})
    return redirect('/dashboard')

@app.route('/searchUsers/<name>', methods=['POST'])
def search(name):
    users=dbInteractor(request.url)
    return json.dumps(users)

@app.route('/deletePost/<userId>/<postId>', methods=['GET'])
def deletePost(userId,postId):
    dbInteractor(request.url)
    return redirect('/dashboard')

@app.route('/makeFriends/<userId>/<friendId>', methods=['GET'])
def makeFriends(userId,friendId):
    dbInteractor(request.url)
    return redirect('/getUserPosts/'+friendId)

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0', port=int(sys.argv[1]))