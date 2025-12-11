from flask import Flask, redirect, render_template, request, session
import mysql.connector
import random
import string
import os
import dotenv 

#loads env file
dotenv.load_dotenv()

#gets secret key
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

#gets database
def get_sqldb():
    return mysql.connector.connect(
        host = os.getenv('MYSQL_HOST'),
        user = os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        database=os.getenv('MYSQL_DB')
    )

#generates ender by grabbing all the possible digits and letters and choosing at random
def generateURLend(length=7):
    code = string.ascii_letters + string.digits
    ender = ''.join(random.choice(code) for i in range(length))
    return ender

#when the html relates to this this method will go and make a url and add it to the table
@app.route('/makeURL')
def makeshortURL():
    longurl=request.args.get('url')
    userid=session['userID']
    done = False
    db = get_sqldb()
    mkcursor=db.cursor()
    while not done:
        done = True
        slink = generateURLend()
        mkcursor.execute('SELECT shortURL FROM Links')
        URLs=mkcursor.fetchall()
        for url in URLs:
            if slink == url[0]:
                done = False
    mkcursor.execute('INSERT INTO Links (LongURL,ShortURL,user_ID) VALUES (%s,%s,%s)' ,(longurl,slink,userid))
    db.commit()
    return redirect('userlinkspage')

#this redirects from the shorturl to the long url
@app.route('/<shorturl>')
def redirectURL(shorturl):
    db = get_sqldb()
    recursor=db.cursor()
    recursor.execute('SELECT LongURL FROM Links WHERE shortURL=%s',(shorturl,))
    URL=recursor.fetchone()
    if not URL:
        return "404: You entered the URL incorrectly or it was deleted."
    return redirect(URL[0])

#the delete key
@app.route('/delete')
def deleteURL():
    urlID=request.args.get('urlID')
    db = get_sqldb()
    delcursor = db.cursor()
    delcursor.execute('DELETE FROM Links WHERE LinkID=%s',(urlID,))
    db.commit()
    return redirect('/userlinkspage')

#the login button activates this which checks to see if the user exists and then starts a session for that user account
@app.route('/login') 
def login():
    username=request.args.get('username')
    psswrd=request.args.get('password')
    db = get_sqldb()
    sqlcursor= db.cursor()
    sqlcursor.execute("SELECT userID FROM Users WHERE UserName=%s AND psswrd=%s",(username,psswrd))
    user = sqlcursor.fetchall()
    if len(user)==1:
        session['userID'] = user[0][0]
        return redirect('/userlinkspage')
    else: 
        return redirect('/loginpage')
#checks to see if user info already exists and makes a new account if it doesnt then takes the person to the login page
@app.route('/signup')
def signUp():
    username=request.args.get('username')
    psswrd=request.args.get('password')
    db = get_sqldb()
    sigcursor = db.cursor()
    sigcursor.execute("SELECT UserName, psswrd FROM Users WHERE UserName=%s AND psswrd=%s",(username,psswrd))
    user = sigcursor.fetchall()
    if len(user)==0:
        sigcursor.execute("INSERT INTO Users (UserName,psswrd) VALUES (%s,%s)",(username,psswrd))
        db.commit()
        return redirect('/loginpage')
    else: 
        return redirect('/signuppage')

#makes front page
@app.route('/')
def startup():
    return render_template('frontpage.html')
#makes login page
@app.route('/loginpage')
def loginpage():
    return render_template('loginpage.html')
#makes sign up page
@app.route('/signuppage')
def signuppage():
    return render_template('signuppage.html')
#makes user links page
@app.route('/userlinkspage')
def userlinkspage():
    userid=session['userID']
    db = get_sqldb()
    linkcursor = db.cursor()
    linkcursor.execute("SELECT LongURL, ShortURL, LinkID FROM Links WHERE user_ID=%s",(userid,))
    links = linkcursor.fetchall()
    return render_template('userlinkspage.html', links=links)

#logs out the user
@app.route('/logout')
def logout():
    del session['userID']
    return redirect('/')
