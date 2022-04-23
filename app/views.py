from app import app
import dns
import pymongo
import os
import random
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from flask import render_template, request, redirect, session, send_file
from app.functions import getcookie, addcookie, delcookie, votechange, addnotiadmacs, allusers, verifycheck, sendemail, checklog
import random
clientm = os.getenv("clientm")
mainclient = pymongo.MongoClient(clientm)

@app.errorhandler(404)
def page_not_found(e):
  return render_template('404.html'), 404

@app.route('/')
def index():
  cookie = getcookie("User")
  search = True
  if checklog() == True or checklog() == None:
    pass
  else:
    return render_template("index.html", cookie=False, noti=False, search=search, text="You have been logged out!")
  if cookie != False:
    notificationsdb = mainclient.Notifications
    notificationscol = notificationsdb[cookie]
    for doc in notificationscol.find({}, {"_id":0, "Status":1}):
      if doc['Status'] == False:
        return render_template("index.html", cookie=cookie, noti=True, search=search)
    return render_template("index.html", cookie=cookie, noti=False, search=search)
  return render_template("index.html", cookie=False, noti=False, search=search)

@app.route('/signup')
def signup():
  if checklog() == True or checklog() == None:
    pass
  else:
    return render_template("index.html", cookie=False, noti=False, search=search, text="You have been logged out!")
  return render_template("signup.html", text="")

@app.route('/signup', methods=['POST', 'GET'])
def signupdef():
  if request.method == "POST":
    if checklog() == True or checklog() == None:
      pass
    else:
      return render_template("index.html", cookie=False, noti=False, search=search, text="You have been logged out!")
    username = request.form['name']
    password = request.form['password']
    usernames = []
    db = mainclient.AllUsers
    mycol = db.mainclient
    mycol2 = db.AllEmails
    allemails = []
    for i in mycol.find({}, {"_id":0, "Username":1}):
      usernames.append(i['Username'].lower())
    for i in mycol2.find({}, {"_id":0, "Email":1}):
      allemails.append(i['Email'].lower())
    if username.lower() in usernames:
      return render_template(
          "signup.html",
          text=
          "That is already a username, you have to choose another username!"
      )
    if " " in username:
      return render_template(
          "signup.html",
          text="You cannot have a space in your username!")
    if " " in password:
      return render_template(
          "signup.html",
          text="You cannot have a space in your password!")
    if "'" in username:
      return render_template(
          "signup.html",
          text="You cannot have an apostrophe in your username!")
    if "'" in password:
      return render_template(
          "signup.html",
          text="You cannot have an apostrophe in your username!")
    if '"' in username:
      return render_template(
          "signup.html",
          text="You cannot have a speech mark in your username!")
    if '"' in password:
      return render_template(
          "signup.html",
          text="You cannot have a speech mark in your password!")
    email = request.form['email']
    if email.lower() in allemails:
      return render_template(
          "signup.html",
          text="A user has already used this email! Use another email or contact wegreekofficail@gmail.com")
    document = [{
        "Username": username,
        "Password": password,
        "Votes": 0,
        "Description": "",
        "Admin": False,
        "MOD": False
    }]
    mycol.insert_many(document)
    for i in mycol.find({}, {'_id':1, 'Username': 1}):
      if i['Username'] == username:
        documentid = i['_id']
    context = ssl.create_default_context()
    mycol2 = db.AllEmails
    document2 = [{
      "Username": username,
      "Email": email,
      "Verified": False
    }]
    mycol2.insert_many(document2)
    for i in mycol2.find({}, {'_id':1, 'Username': 1}):
      if i['Username'] == username:
        theid = i['_id']
    html = f"""
                <html>
                  <body>
                    <p><strong>You have signed up for an account in We Greek!</strong><br>
                      Click <a href='https://https://Greek-Mythology-Wikipedia.wegreek.repl.co/emailverification/{str(theid)}'>here</a> to verify your account!
                  <br>
                  If you didn't make this account, reply back to this email saying this isn't your account and <strong>DO NOT</strong> click on the link or the user who made the account will get verified with your email!</p>
                  </body>
                </html>
            """
    gmail_server = smtplib.SMTP('smtp.gmail.com', 587)
    message = MIMEMultipart("alternative")
    message["Subject"] = "Verification email"
    part2 = MIMEText(html, "html")
    message.attach(part2)
    gmail_server.starttls(context=context)
    gmail_server.login("wegreekofficial@gmail.com", os.getenv("mailpass"))
    try:
      message["From"] = "wegreekofficial@gmail.com"
      message["To"] = email
      gmail_server.sendmail("wegreekofficial@gmail.com", email, message.as_string())
    except:
      delete1 = {"_id": theid}
      mycol2.delete_one(delete1)
      delete2 = {"_id": documentid}
      mycol.delete_one(delete2)
      return render_template(
          "signup.html",
          text="That is not a valid email!")
    return render_template("index.html", text="Your account has been made! Now go to your email and verify your account!", cookie=username, noti=False)

@app.route('/login')
def login():
  if checklog() == True or checklog() == None:
    pass
  else:
    return render_template("index.html", cookie=False, noti=False, search=search, text="You have been logged out!")
  return render_template("login.html")

@app.route('/login', methods=['POST', 'GET'])
def logindef():
  if request.method == "POST":
    if checklog() == True or checklog() == None:
      pass
    else:
      return render_template("index.html", cookie=False, noti=False, search=search, text="You have been logged out!")
    username = request.form['username']
    password = request.form['password']
    db = mainclient["AllUsers"]
    mycol = db["mainclient"]
    allusers = []
    for doc in mycol.find({}, {"_id": 0, "Username": 1}):
      xx = doc['Username']
      allusers.append(xx)
    if username not in allusers:
      return render_template(
          "login.html", text="That is not a real username!")
    for doc in mycol.find({}, {"_id": 0, "Username": 1, "Password": 1}):
      someusername = doc['Username']
      if username == someusername:
        passwordnew = doc['Password']
    if password == passwordnew:
      pass
    else:
      return render_template("login.html", text="Wrong password!")
    addcookie("User", username)
    cookie = str(getcookie("User"))
    return redirect('/')

@app.route("/notifications")
def notifications():
  if checklog() == True or checklog() == None:
    pass
  else:
    return render_template("index.html", cookie=False, noti=False, search=search, text="You have been logged out!")
  cookie = getcookie("User")
  if cookie == False:
    return render_template("index.html", cookie=cookie, text="You have to log in to see your notifications!", noti=False)
  else:
    noti = []
    notificationsdb = mainclient.Notifications
    notificationscol = notificationsdb[cookie]
    for doc in notificationscol.find({}, {"_id":1, "Notification":1, "Url":1, "Status":1}):
      status = str(doc['Status'])
      del doc['Status']
      doc['Status'] = status
      noti.append(doc)
    for i in noti:
      theid = i['_id']
      notification = i['Notification']
      url = i['Url']
      status = i['Status']
      delete = {"_id": theid}
      notificationscol.delete_one(delete)
      document = [{
        "Notification":notification,
        "Url": url,
        "Status": True
      }]
      notificationscol.insert_many(document)
    noti.reverse()
    return render_template("notifications.html", all=noti)

@app.route("/delnoti")
def delnoti():
  if checklog() == True or checklog() == None:
    pass
  else:
    return render_template("index.html", cookie=False, noti=False, search=search, text="You have been logged out!")
  cookie = getcookie("User")
  if cookie == False:
    return render_template("index.html", cookie=cookie, text="You have to log in to clear your notifications!", noti=False)
  else:
    notificationsdb = mainclient.Notifications
    notificationscol = notificationsdb[cookie]
    notificationscol.drop()
    return redirect("/notifications")

@app.route("/logout")
def logout():
  session.clear()
  return redirect("/")

@app.route("/makewiki")
def makewiki():
  if checklog() == True or checklog() == None:
    pass
  else:
    return render_template("index.html", cookie=False, noti=False, search=search, text="You have been logged out!")
  cookie = getcookie("User")
  if cookie == False:
    return render_template("index.html", text="You have to log in to make a wiki!", cookie=False, noti=False)
  else:
    verify = verifycheck(cookie)
    if verify == False:
      return render_template("index.html", text="You have to go on your email and verify your account to make a wiki!", cookie=cookie, noti=False)
    return render_template("makewiki.html")

@app.route('/makewiki', methods=['POST', 'GET'])
def makewikidef():
  if request.method == "POST":
    if checklog() == True or checklog() == None:
      pass
    else:
      return render_template("index.html", cookie=False, noti=False, search=search, text="You have been logged out!")
    cookie = getcookie("User")
    if cookie == False:
      return render_template("index.html", text="You have to log in to make a wiki!", cookie=False, noti=False)
    verify = verifycheck(cookie)
    if verify == False:
      return render_template("index.html", text="You have to go on your email and verify your account to make a wiki!", cookie=cookie, noti=False)
    db = mainclient["Threads"]
    mycol = db["Wikis"]
    titles = []
    for i in mycol.find():
      titles.append(i['Title'])
    title = request.form['title']
    if title in titles:
      return render_template("makewiki.html", text="This title is already a title of a wiki!")
    body = request.form['body']
    allids = []
    for doc in mycol.find({}, {"_id": 1}):
      xx = doc['_id']
      allids.append(xx)
    col = db["Wikis"]
    for doc in col.find({}, {"_id": 1}):
      xx = doc['_id']
      allids.append(xx)
    randomid = ""
    for i in range(15):
      number = random.randint(0, 9)
      randomid = str(number) + randomid
    while int(randomid) in allids:
      randomid = ""
      for i in range(15):
        number = random.randint(0, 9)
        randomid = str(number) + randomid
    document = [{
        '_id': int(randomid),
        'Title': title,
        'Body': body,
        'Author': cookie,
        "Verified": False,
    }]
    mycol.insert_many(document)
    adb = mainclient.Views
    acol = adb.Wikis
    adocument = [{
      "Wiki id": int(randomid),
      "Viewers": []
    }]
    acol.insert_many(adocument)
    for i in mycol.find():
      if i['Title'] == title:
        if i['Body'] == body:
          if i['Author'] == cookie:
            randomid = i['_id']
    url = "/wikis/" + str(randomid)
    print(url)
    noti = cookie + " has made a new wiki! Click here to verify it!"
    addnotiadmacs(url, noti)
    return redirect(url)

@app.route("/deleteblog/<id>")
def deletewiki(id):
  if checklog() == True or checklog() == None:
    pass
  else:
    return render_template("index.html", cookie=False, noti=False, search=search, text="You have been logged out!")
  DB = mainclient.Threads
  MYCOL = DB.Wikis
  ids = []
  for i in MYCOL.find({}, {"_id":1, "Author":1}):
    theid = str(i['_id'])
    ids.append(theid)
  if id in ids:
    for i in MYCOL.find({}, {"_id":0, "Author":1}):
      if i['_id'] == id:
        author = i['Author']
    db = mainclient.AllUsers
    allcol = db.mainclient
    user = {}
    cookie = getcookie("User")
    if cookie == False:
      user['PERMS'] = "NONE"
    else:
      yourusername = cookie
      for doc in allcol.find({}, {"_id": 0, "Username": 1, "MOD":1, "Admin":1}):
        if doc['Username'] == yourusername:
          if author == yourusername:
            user['PERMS'] = "YOURPOST"
          elif doc['MOD'] == True:
            user['PERMS'] = "MOD"
          elif doc['Admin'] == True:
            user['PERMS'] = "ADMIN"
          else:
            user['PERMS'] = "NONE"
      if user['PERMS'] != "NONE":
        delete = {"_id":int(id)}
        DB = mainclient.Threads
        MYCOL = DB.Wikis
        MYCOL.delete_one(delete)
        adb = mainclient.Views
        acol = adb.WIkis
        for i in acol.find():
          if i['Wiki id'] == int(id):
            delete = {"_id": i['_id']}
            acol.delete_one(delete)
        notificationsdb = mainclient.Notifications
        notificationscol = notificationsdb[cookie]
        for doc in notificationscol.find({}, {"_id":0, "Status":1}):
          if doc['Status'] == False:
            return render_template("index.html", cookie=cookie, noti=True, text="The wiki has been deleted!")
        return render_template("index.html", cookie=cookie, noti=False, text="The wiki has been deleted!")
      else:
        return render_template("404.html")
  else:
    return render_template("404.html")

@app.route("/verifywiki/<id>")
def verifywiki(id):
  if checklog() == True or checklog() == None:
    pass
  else:
    return render_template("index.html", cookie=False, noti=False, search=search, text="You have been logged out!")
  DB = mainclient.Threads
  MYCOL = DB.Wikis
  ids = []
  for i in MYCOL.find({}, {"_id":1, "Author":1}):
    theid = str(i['_id'])
    ids.append(theid)
  if id in ids:
    # for i in MYCOL.find({}, {"_id":1, "Author":1}):
    #   if i['_id'] == id:
    #     author = i['Author']
    db = mainclient.AllUsers
    allcol = db.mainclient
    user = {}
    cookie = getcookie("User")
    if cookie == False:
      user['PERMS'] = "NONE"
    else:
      yourusername = cookie
      for doc in allcol.find({}, {"_id": 0, "Username": 1, "MOD":1, "Admin":1}):
        if doc['Username'] == yourusername:
          if doc['MOD'] == True:
            user['PERMS'] = "MOD"
          elif doc['Admin'] == True:
            user['PERMS'] = "ADMIN"
          else:
            user['PERMS'] = "NONE"
      if user['PERMS'] != "NONE":
        DB = mainclient.Threads
        MYCOL = DB.Wikis
        for i in MYCOL.find({}, {'_id': 1,'Title': 1,'Body': 1,'Author': 1}):
          if str(i['_id']) == str(id):
            delete = {"_id":int(id)}
            MYCOL.delete_one(delete)
            document = [{
              "_id": i['_id'],
              "Title":i['Title'],
              "Body": i['Body'],
              "Author":i['Author'],
              "Verified": True
            }]
            MYCOL.insert_many(document)
            thedb = mainclient.Notifications
            thecol = thedb[i['Author']]
            thedocument = [{
              "Notification": "Your wiki has been verified",
              "Url": "/wikis/" + str(id),
              "Status": False
            }]
            thecol.insert_many(thedocument)
            votechange(i['Author'], 1)
            sendemail(i['Author'], "Your wiki has been verified", "/wikis/" + str(id))
            addnotiadmacs("/wikis/" + str(id), "A wiki has been verified")
        return redirect("/wikis/" + str(id))
      else:
        return render_template("404.html")
  else:
    return render_template("404.html")

@app.route("/allwikis")
def allwikis():
  if checklog() == True or checklog() == None:
    pass
  else:
    return render_template("index.html", cookie=False, noti=False, search=search, text="You have been logged out!")
  DB = mainclient.Threads
  MYCOL = DB.Wikis
  wikis = []
  for i in MYCOL.find({}, {"_id":1, "Title":1, "Verified":1, "Author":1}):
    if i['Verified'] == True:
      if len(i['Title']) > 10:
        title = i['Title']
        firstten = title[0:10]
        title = firstten + "..."
        del i['Title']
        i['Title'] = title
      i['URL'] = "/wikis/" + str(i['_id'])
      wikis.append(i)
    random.shuffle(wikis)
  return render_template("allwikis.html", wikis=wikis)

@app.route("/users/<username>")
def users(username):
  if checklog() == True or checklog() == None:
    pass
  else:
    return render_template("index.html", cookie=False, noti=False, search=search, text="You have been logged out!")
  db = mainclient.AllUsers
  allcol = db.mainclient
  allusers = []
  for doc in allcol.find({}, {"_id": 0, "Username": 1}):
    theusername = doc['Username']
    allusers.append(theusername)
  doc = {}
  doc['User'] = username
  db = mainclient.Threads
  mycol = db.Wikis
  wikis = 0
  for i in mycol.find():
    if i['Verified'] == True:
      wikis = wikis + 1
  if wikis > 99:
    doc['Wiki Master'] = True
  else:
    doc['Wiki Master'] = False
  if username in allusers:
    for doc in allcol.find({}, {"_id": 0, "Username": 1, "Admin":1, "MOD":1, "Votes":1, "Description":1}):
      if doc['Username'] == username:
        return render_template("user.html", doc=doc)
  else:
    return render_template("404.html")

@app.route("/admacsnoti")
def admacsnotifications():
  if checklog() == True or checklog() == None:
    pass
  else:
    return render_template("index.html", cookie=False, noti=False, search=search, text="You have been logged out!")
  cookie = getcookie("User")
  user = {}
  if cookie == False:
    user['PERMS'] = "NONE"
  else:
    yourusername = cookie
    db = mainclient.AllUsers
    allcol = db.mainclient
    for doc in allcol.find({}, {"_id": 0, "Username": 1, "MOD":1, "Admin":1}):
      if doc['Username'] == yourusername:
        if doc['MOD'] == True:
          user['PERMS'] = "MOD"
        elif doc['Admin'] == True:
          user['PERMS'] = "ADMIN"
        else:
          user['PERMS'] = "NONE"
  if user['PERMS'] == "NONE":
    return render_template("index.html", cookie=cookie, text="You don't have permissions to look at this!", noti=False)
  else:
    noti = []
    notificationsdb = mainclient.ADMACS
    notificationscol = notificationsdb.Notifications
    for doc in notificationscol.find({}, {"_id":1, "Notification":1, "Url":1, "Status":1}):
      status = str(doc['Status'])
      del doc['Status']
      doc['Status'] = status
      noti.append(doc)
    for i in noti:
      theid = i['_id']
      notification = i['Notification']
      url = i['Url']
      status = i['Status']
      delete = {"_id": theid}
      notificationscol.delete_one(delete)
      document = [{
        "Notification":notification,
        "Url": url,
        "Status": True
      }]
      notificationscol.insert_many(document)
    return render_template("admacsnoti.html", all=noti)

@app.route("/account")
def account():
  if checklog() == True or checklog() == None:
    pass
  else:
    return render_template("index.html", cookie=False, noti=False, search=search, text="You have been logged out!")
  cookies = getcookie("User")
  if cookies == False:
    return render_template("index.html", text="You have to login first!", cookie=cookies, noti=False)
  else:
    username = cookies
    db = mainclient.AllUsers
    mycol = db.mainclient
    for i in mycol.find({}, {"_id":1, "Username":1, "Description":1}):
      if i['Username'] == username:
        desc = i['Description']
        check = verifycheck(username)
        print(check)
        return render_template("account.html", text="", desc=desc, check=check)

@app.route("/account", methods=['POST', 'GET'])
def accountmain():
  if request.method == "POST":
    if checklog() == True or checklog() == None:
      pass
    else:
      return render_template("index.html", cookie=False, noti=False, search=search, text="You have been logged out!")
    cookies = getcookie("User")
    if cookies == False:
      return render_template("index.html", text="You have to login first!", cookie=False, noti=False)
    verify = verifycheck(cookies)
    if verify == False:
      return render_template("index.html", text="You have to go on your email and verify your account to do stuff on your account!", cookie=cookies, noti=False)
    db = mainclient.AllUsers
    mycol = db.mainclient
    for i in mycol.find({}, {"_id":1, "Username":1, "Password":1, "Votes":1, "Admin":1, "MOD":1}):
      if i['Username'] == cookies:
        theid = i['_id']
        password = i['Password']
        votes = i['Votes']
        admin = i['Admin']
        mod = i['MOD']
    description = request.form['description']
    delete = {"_id": theid}
    mycol.delete_one(delete)
    document = [{
        "Username": cookies,
        "Password": password,
        "Votes": votes,
        "Description": description,
        "Admin": admin,
        "MOD": mod
    }]
    mycol.insert_many(document)
    return redirect("/users/" + cookies)

@app.route("/", methods=['POST', 'GET'])
def search():
  if request.method == "POST":
    search = False
    if checklog() == True or checklog() == None:
      pass
    else:
      return render_template("index.html", cookie=False, noti=False, search=search, text="You have been logged out!")
    search = request.form['search'].lower()
    searches = []
    db = mainclient.AllUsers
    mycol = db.mainclient
    for user in mycol.find({}, {"Username":1}):
      if search in user['Username'].lower():
        answer = {"Title":"User: " + user['Username'], "Url": "/users/" + user['Username'], "Title2": ""}
        searches.append(answer)
      elif user['Username'].lower() in search:
        answer = {"Title":"User: " + user['Username'], "Title2":"", "Url": "/users/" + user['Username']}
        searches.append(answer)
    db = mainclient.Threads
    mycol = db.Wikis
    for wiki in mycol.find():
      if wiki['Verified'] == False:
        pass
      else:
        if search in wiki['Author'].lower():
          answer = {"Title": wiki['Title'],  "Title2":"By: " + wiki['Author'], "Url": "/wikis/" + str(wiki['_id'])}
          searches.append(answer)
        elif wiki['Author'].lower() in search:
          answer = {"Title": wiki['Title'],  "Title2":"By: " + wiki['Author'], "Url": "/wikis/" + str(wiki['_id'])}
          searches.append(answer)
        elif search in wiki['Title'].lower():
          answer = {"Title": wiki['Title'],  "Title2":"By: " + wiki['Author'], "Url": "/wikis/" + str(wiki['_id'])}
          searches.append(answer)
        elif wiki['Title'].lower() in search:
          answer = {"Title": wiki['Title'],  "Title2":"By: " + wiki['Author'], "Url": "/wikis/" + str(wiki['_id'])}
          searches.append(answer)
        elif search in wiki['Body'].lower():
          answer = {"Title": wiki['Title'],  "Title2":"By: " + wiki['Author'], "Url": "/wikis/" + str(wiki['_id'])}
          searches.append(answer)
    db = mainclient.Threads
    mycol = db.Posts
    for wiki in mycol.find({}, {"_id":1, "Title":1, "Body":1, "Author":1}):
      if search in wiki['Author'].lower():
        answer = {"Title": wiki['Title'],  "Title2":"By: " + wiki['Author'], "Url": "/posts/" + str(wiki['_id'])}
        searches.append(answer)
      elif wiki['Author'].lower() in search:
        answer = {"Title": wiki['Title'],  "Title2":"By: " + wiki['Author'], "Url": "/posts/" + str(wiki['_id'])}
        searches.append(answer)
      elif search in wiki['Title'].lower():
        answer = {"Title": wiki['Title'],  "Title2":"By: " + wiki['Author'], "Url": "/posts/" + str(wiki['_id'])}
        searches.append(answer)
      elif wiki['Title'].lower() in search:
        answer = {"Title": wiki['Title'],  "Title2":"By: " + wiki['Author'], "Url": "/posts/" + str(wiki['_id'])}
        searches.append(answer)
      elif search in wiki['Body'].lower():
        answer = {"Title": wiki['Title'],  "Title2":"By: " + wiki['Author'], "Url": "/posts/" + str(wiki['_id'])}
        searches.append(answer)
    random.shuffle(searches)
    return render_template("search.html", thesearch=search, searches=searches)

@app.route("/admacsdelnoti")
def admacsdelnoti():
  if checklog() == True or checklog() == None:
    pass
  else:
    return render_template("index.html", cookie=False, noti=False, search=search, text="You have been logged out!")
  cookie = getcookie("User")
  user = {}
  if cookie == False:
    user['PERMS'] = "NONE"
  else:
    yourusername = cookie
    db = mainclient.AllUsers
    allcol = db.mainclient
    for doc in allcol.find({}, {"_id": 0, "Username": 1, "MOD":1, "Admin":1}):
      if doc['Username'] == yourusername:
        if doc['MOD'] == True:
          user['PERMS'] = "MOD"
        elif doc['Admin'] == True:
          user['PERMS'] = "ADMIN"
        else:
          user['PERMS'] = "NONE"
  if user['PERMS'] == "NONE":
    return render_template("404.html")
  else:
    notificationsdb = mainclient.ADMACS
    notificationscol = notificationsdb.Notifications
    notificationscol.drop()
    return redirect("/admacsnoti")

@app.route("/wikis/<id>")
def checkwiki(id):
  if checklog() == True or checklog() == None:
    pass
  else:
    return render_template("index.html", cookie=False, noti=False, search=search, text="You have been logged out!")
  user = {}
  DB = mainclient.Threads
  MYCOL = DB.Wikis
  ids = []
  for i in MYCOL.find({}, {"_id":1, "Author":1}):
    theid = str(i['_id'])
    ids.append(theid)
  if id in ids:
    for i in MYCOL.find():
      if str(i['_id']) == id:
        author = i['Author']
    db = mainclient.AllUsers
    allcol = db.mainclient
    cookie = getcookie("User")
    if cookie == False:
      user['PERMS'] = "NONE"
    else:
      adb = mainclient.Views
      acol = adb.Wikis
      yourusername = cookie
      for wiki in acol.find():
        if str(wiki['Wiki id']) == id:
          if yourusername in wiki['Viewers']:
            pass
          else:
            thedoc = wiki
            thedoc['Viewers'].append(yourusername)
            acol.delete_one({"_id": wiki['_id']})
            acol.insert_many([thedoc])
      
      for doc in allcol.find({}, {"_id": 0, "Username": 1, "MOD":1, "Admin":1}):
        if doc['Username'] == yourusername:
          if doc['Admin'] == True:
            user['PERMS'] = "ADMIN"
          elif doc['MOD'] == True:
            user['PERMS'] = "MOD"
          elif author == yourusername:
            user['PERMS'] = "YOURPOST"
          else:
            user['PERMS'] = "NONE"
    DB = mainclient.Threads
    MYCOL = DB.Wikis
    for doc in MYCOL.find({}, {"_id": 1, "Title":1, "Body":1, "Verified":1}):
      if str(doc['_id']) == str(id):
        if doc['Verified'] == True:
          adb = mainclient.Views
          acol = adb.Wikis
          views= 0
          for wiki in acol.find():
            if str(wiki['Wiki id']) == id:
              for i in wiki['Viewers']:
                views = views + 1
          if views % 100 == 0 and cookie != False:
            votechange(author, 1)
          doc['Author'] = author
          doc['url'] = "/deleteblog/" + str(id) 
          doc['Views'] = views
          return render_template("wiki.html", doc=doc, user=user)
        else:
          if user['PERMS'] != "NONE":
            doc['Author'] = author
            doc['url'] = "/deleteblog/" + str(id)
            doc['url2'] = "/verifywiki/" + str(id)
            adb = mainclient.Views
            acol = adb.Wikis
            views=0
            for wiki in acol.find():
              if str(wiki['Wiki id']) == id:
                for i in wiki['Viewers']:
                  views = views + 1
            if views % 100 == 0 and cookie != False:
              votechange(author, 1)
            doc['Views'] = views
            return render_template("wiki.html", doc=doc, user=user)
          else:
            return render_template("404.html")      
  else:
    return render_template("404.html")

@app.route("/wikis/<id>", methods=['POST', 'GET'])
def editwiki(id):
  if request.method == "POST":
    if id==None:
      return render_template("404.html")
    if checklog() == True or checklog() == None:
      pass
    else:
      return render_template("index.html", cookie=False, noti=False, search=search, text="You have been logged out!")
    user = {}
    DB = mainclient.Threads
    MYCOL = DB.Wikis
    ids = []
    for i in MYCOL.find({}, {"_id":1, "Author":1}):
      theid = str(i['_id'])
      ids.append(theid)
    if id in ids:
      for i in MYCOL.find({}, {"_id":1, "Author":1}):
        author = i['Author']
      db = mainclient.AllUsers
      allcol = db.mainclient
      cookie = getcookie("User")
      if cookie == False:
        return render_template("404.html")
      else:
        yourusername = cookie
        for doc in allcol.find({}, {"_id": 0, "Username": 1, "MOD":1, "Admin":1}):
          if doc['Username'] == yourusername:
            if doc['Admin'] == True:
              user['PERMS'] = "ADMIN"
            elif doc['MOD'] == True:
              user['PERMS'] = "MOD"
            elif author == yourusername:
              user['PERMS'] = "YOURPOST"
            else:
              return render_template("404.html")
      body = request.form['body']
      for wiki in MYCOL.find({}, {'_id': 1, 'Title': 1, 'Body': 1, 'Author': 1, "Verified": 1}):
        if int(id) == wiki['_id']:
          delete = {"_id": int(id)}
          MYCOL.delete_one(delete)
          document = [{
            "_id": int(id),
            "Title": wiki['Title'],
            "Body": body,
            "Author": wiki['Author'],
            "Verified": wiki['Verified']
          }]
          MYCOL.insert_many(document)
          addnotiadmacs("/wikis/" + str(id), cookie + " has edited a wiki! Click here to check if it is safe!")
          return render_template("wiki.html", doc=wiki, user=user)
    else:
      return render_template("404.html")

@app.route("/makepost")
def makepost():
  cookie = getcookie("User")
  if checklog() == True or checklog() == None:
    pass
  else:
    return render_template("index.html", cookie=False, noti=False, search=search, text="You have been logged out!")
  if cookie == False:
    return render_template("index.html", text="You have to log in to make a post!", cookie=False, noti=False)
  else:
    verify = verifycheck(cookie)
    if verify == False:
      return render_template("index.html", text="You have to go on your email and verify your account to make a post!", cookie=cookie, noti=False)
    return render_template("makepost.html")

@app.route('/makepost', methods=['POST', 'GET'])
def makepostdef():
  if request.method == "POST":
    if checklog() == True or checklog() == None:
      pass
    else:
      return render_template("index.html", cookie=False, noti=False, search=search, text="You have been logged out!")
    cookie = getcookie("User")
    if cookie == False:
      return render_template("index.html", text="You have to log in to make a wiki!", cookie=False, noti=False)
    verify = verifycheck(cookie)
    if verify == False:
      return render_template("index.html", text="You have to go on your email and verify your account to make a post!", cookie=cookie, noti=False)
    title = request.form['title']
    body = request.form['body']
    bodysplit = body.split()
    db = mainclient["Threads"]
    mycol = db["Posts"]
    allids = []
    for doc in mycol.find({}, {"_id": 1}):
      xx = doc['_id']
      allids.append(xx)
    col = db["Wikis"]
    for doc in col.find({}, {"_id": 1}):
      xx = doc['_id']
      allids.append(xx)
    randomid = ""
    for i in range(15):
      number = random.randint(0, 9)
      randomid = str(number) + randomid
    while int(randomid) in allids:
      randomid = ""
      for i in range(15):
        number = random.randint(0, 9)
        randomid = str(number) + randomid
    document = [{
        '_id': int(randomid),
        'Title': title,
        'Body': body,
        'Author': cookie,
        "Votes": [0, []]
    }]
    mycol.insert_many(document)
    adb = mainclient.Views
    acol = adb.Posts
    adocument = [{
      "Post id": int(randomid),
      "Viewers": []
    }]
    acol.insert_many(adocument)
    url = "/posts/" + str(randomid)
    mentionusers = []
    theallusers = allusers()
    for word in bodysplit:
      if "@" in word:
        wordlettersplit = list(word)
        atindex = wordlettersplit.index("@") 
        wordlettersplit.pop(atindex)
        mentionusersplit = wordlettersplit
        mentionuserandtag = "".join(mentionusersplit)
        if mentionuserandtag in theallusers:
          if mentionuserandtag in mentionusers:
            pass
          else:
            notificationsdb = mainclient.Notifications
            notificationscol = notificationsdb[mentionuserandtag]
            document = [{
              "Notification": mentionuserandtag + " mentioned you in their post",
              "Url": url,
              "Status": False,
            }]
            notificationscol.insert_many(document)
            mentionusers.append(mentionuserandtag)
        else:
          pass
    print(url)
    noti = cookie + " has made a new post! Click here to check it is safe!"
    addnotiadmacs(url, noti)
    return redirect(url)

@app.route("/posts/<id>")
def checkpost(id):
  if checklog() == True or checklog() == None:
    pass
  else:
    return render_template("index.html", cookie=False, noti=False, search=search, text="You have been logged out!")
  user = {}
  DB = mainclient.Threads
  MYCOL = DB.Posts
  ids = []
  for i in MYCOL.find({}, {"_id":1, "Author":1}):
    theid = str(i['_id'])
    ids.append(theid)
  if id in ids:
    for i in MYCOL.find({}, {"_id":1, "Author":1}):
      if str(i['_id']) == str(id):
        author = i['Author']
    db = mainclient.AllUsers
    allcol = db.mainclient
    cookie = getcookie("User")
    adb = mainclient.Views
    acol = adb.Posts
    views = 0
    for i in acol.find():
      if str(i['Post id']) == id:
        for viewers in i['Viewers']:
          views = views + 1
    if cookie == False:
      user['PERMS'] = "NONE"
      DB = mainclient.Threads
      MYCOL = DB.Posts
      comcol = DB.PostComments
      comments = []
      for comment in comcol.find({}, {"_id":1, "Author":1, "Comment":1, "PostId":1, "Votes":1}):
        if comment['PostId'] == int(id):
          comment['Url'] = "/deletepostcomment/" + str(comment['_id'])
          if user['PERMS'] == "YOURPOST" or user['PERMS'] == "USER":
            if comment['Author'] == cookie:
              comment['PERMS'] = "YOURCOMMENT"
          else:
            comment['PERMS'] = user['PERMS']
          comments.append(comment)
      for doc in MYCOL.find({}, {"_id": 1, "Title":1, "Body":1, "Author":1}):
        if str(doc['_id']) == str(id):
            doc['url'] = "/deletepost/" + str(id) 
            doc['Views'] = views
            return render_template("post.html", doc=doc, user=user, allcom=comments)
    else:
      yourusername = cookie
      adb = mainclient.Views
      acol = adb.Posts
      yourusername = cookie
      for wiki in acol.find():
        if str(wiki['Post id']) == id:
          if yourusername in wiki['Viewers']:
            pass
          else:
            thedoc = wiki
            thedoc['Viewers'].append(yourusername)
            acol.delete_one({"_id": wiki['_id']})
            acol.insert_many([thedoc])
      for doc in allcol.find({}, {"_id": 0, "Username": 1, "MOD":1, "Admin":1}):
        if doc['Username'] == yourusername:
          if doc['Admin'] == True:
            user['PERMS'] = "ADMIN"
          elif doc['MOD'] == True:
            user['PERMS'] = "MOD"
          elif author == yourusername:
            user['PERMS'] = "YOURPOST"
          else:
            user['PERMS'] = "USER"
          DB = mainclient.Threads
          MYCOL = DB.Posts
          comcol = DB.PostComments
          comments = []
          for comment in comcol.find({}, {"_id":1, "Author":1, "Comment":1, "PostId":1, "Votes":1}):
            if comment['PostId'] == int(id):
              comment['Url'] = "/deletepostcomment/" + str(comment['_id'])
              if user['PERMS'] == "YOURPOST" or user['PERMS'] == "USER":
                if comment['Author'] == cookie:
                  comment['PERMS'] = "YOURCOMMENT"
              else:
                comment['PERMS'] = user['PERMS']
              comments.append(comment)
          for doc in MYCOL.find({}, {"_id": 1, "Title":1, "Body":1, "Author":1}):
            if str(doc['_id']) == str(id):
                doc['url'] = "/deletepost/" + str(id) 
                doc['Views'] = views
                return render_template("post.html", doc=doc, user=user, allcom=comments)
                if user['PERMS'] != "NONE":
                  doc['Author'] = author
                  doc['url'] = "/deletepost/" + str(id)
                  doc['Views'] = views
                  return render_template("post.html", doc=doc, user=user, allcom=comments)
                else:
                  return render_template("404.html")  
          
  else:
    return render_template("404.html")

@app.route("/posts/<id>", methods=['POST', 'GET'])
def commentpost(id):
  if request.method == "POST":
    if checklog() == True or checklog() == None:
      pass
    else:
      return render_template("index.html", cookie=False, noti=False, search=search, text="You have been logged out!")
    DB = mainclient.Threads
    MYCOL = DB.Posts
    wikis = []
    for i in MYCOL.find({}, {"_id":1, "Title":1, "Author":1}):
      theid = str(i['_id'])
      wikis.append(theid)
    if id in wikis:
      cookie = getcookie("User")
      if cookie == False:
        return render_template("index.html", text="You have to log in to comment!", cookie=False, noti=False)
      verify = verifycheck(cookie)
      if verify == False:
        return render_template("index.html", text="You have to go on your email and verify your account to comment!", cookie=cookie, noti=False)
      body = request.form['body']
      db = mainclient["Threads"]
      mycol = db["PostComments"]
      document = [{
        "Author": cookie,
        "Comment": body,
        "Votes":0,
        "PostId":int(id)
      }]
      mycol.insert_many(document)
      for post in MYCOL.find({}, {"_id":1, "Author":1}):
        if str(post['_id']) == id:
          author = post['Author']
          db = mainclient.Notifications
          mycol = db[author]
          document = [{
            "Notification": cookie + " has commented on your post!",
            "Url": "/posts/" + id,
            "Status": False
          }]
          mycol.insert_many(document)
          addnotiadmacs("/posts/" + id, cookie + " has commented on this post! Check it out!")
          return redirect("/posts/" + id)
    else:
      return render_template("404.html")

@app.route("/deletepost/<id>")
def deletepost(id):
  if checklog() == True or checklog() == None:
    pass
  else:
    return render_template("index.html", cookie=False, noti=False, search=search, text="You have been logged out!")
  DB = mainclient.Threads
  MYCOL = DB.Posts
  ids = []
  for i in MYCOL.find({}, {"_id":1, "Author":1}):
    theid = str(i['_id'])
    ids.append(theid)
  if id in ids:
    for i in MYCOL.find({}, {"_id":0, "Author":1}):
      author = i['Author']
    db = mainclient.AllUsers
    allcol = db.mainclient
    user = {}
    cookie = getcookie("User")
    if cookie == False:
      user['PERMS'] = "NONE"
    else:
      yourusername = cookie
      for doc in allcol.find({}, {"_id": 0, "Username": 1, "MOD":1, "Admin":1}):
        if doc['Username'] == yourusername:
          if author == yourusername:
            user['PERMS'] = "YOURPOST"
          elif doc['MOD'] == True:
            user['PERMS'] = "MOD"
          elif doc['Admin'] == True:
            user['PERMS'] = "ADMIN"
          else:
            user['PERMS'] = "NONE"
      if user['PERMS'] != "NONE":
        delete = {"_id":int(id)}
        DB = mainclient.Threads
        MYCOL = DB.Posts
        MYCOL.delete_one(delete)
        thecol = DB.PostComments
        for comment in thecol.find({}, {"_id":1, "PostId":1}):
          if id == str(comment['PostId']):
            delete = {"_id": comment['_id']}
            thecol.delete_one(delete)
        adb = mainclient.Views
        acol = adb.Posts
        for i in acol.find():
          if i['Post id'] == int(id):
            delete = {"_id": i['_id']}
            acol.delete_one(delete)
        notificationsdb = mainclient.Notifications
        notificationscol = notificationsdb[cookie]
        for doc in notificationscol.find({}, {"_id":0, "Status":1}):
          if doc['Status'] == False:
            return render_template("index.html", cookie=cookie, noti=True, text="The post has been deleted!")
        return render_template("index.html", cookie=cookie, noti=False, text="The post has been deleted!")
      else:
        return render_template("404.html")
  else:
    return render_template("404.html")

@app.route("/allposts")
def allposts():
  if checklog() == True or checklog() == None:
    pass
  else:
    return render_template("index.html", cookie=False, noti=False, search=search, text="You have been logged out!")
  DB = mainclient.Threads
  MYCOL = DB.Posts
  wikis = []
  for i in MYCOL.find({}, {"_id":1, "Title":1, "Author":1}):
    if len(i['Title']) > 10:
      title = i['Title']
      firstten = title[0:10]
      title = firstten + "..."
      del i['Title']
      i['Title'] = title
    i['URL'] = "/posts/" + str(i['_id'])
    wikis.append(i)
    random.shuffle(wikis)
  return render_template("allposts.html", wikis=wikis)

@app.route("/deletepostcomment/<id>")
def deletepostcomment(id):
  if checklog() == True or checklog() == None:
    pass
  else:
    return render_template("index.html", cookie=False, noti=False, search=search, text="You have been logged out!")
  hello = True
  if hello == True:
    db = mainclient.Threads
    mycol = db.PostComments
    allids = []
    for comment in mycol.find({}, {"_id":1}):
      allids.append(str(comment['_id']))
    user = {}
    thedb = mainclient.AllUsers
    allcol = thedb.mainclient
    if id in allids:
      for comment in mycol.find({}, {"_id":1,   "Author":1}):
        if comment['_id'] == id:
          author = comment['Author']
      cookie = getcookie("User")
      if cookie == False:
        return render_template("404.html")
      else:
        yourusername = cookie
        for doc in allcol.find({}, {"_id": 0,  "Username": 1, "MOD":1, "Admin":1}):
          if doc['Username'] == yourusername:
            if doc['Admin'] == True:
              user['PERMS'] = "ADMIN"
            elif doc['MOD'] == True:
              user['PERMS'] = "MOD"
            elif author == yourusername:
              user['PERMS'] = "YOURPOST"
            else:
              user['PERMS'] = "NONE"
        db = mainclient.Threads
        thecol = db.PostComments
        if hello == True:
          for hello in thecol.find({}, {"_id":1, "PostId":1}): 
            if str(hello['_id']) == id:
              thepostid = str(hello['PostId'])
              delete = {"_id": hello['_id']}
              mycol.delete_one(delete)
              return redirect("/posts/" + thepostid)
    else:
      return render_template("404.html")

@app.route("/emailverification/<theid>")
def verifyemail(theid):
  if checklog() == True or checklog() == None:
    pass
  else:
    return render_template("index.html", cookie=False, noti=False, search=search, text="You have been logged out!")
  db = mainclient.AllUsers
  mycol = db.AllEmails
  allids = []
  for user in mycol.find({}, {"_id": 1}):
    allids.append(str(user['_id']))
  if theid in allids:
    pass
  else:
    return redirect("/")
  for hello in mycol.find({}, {"_id": 1, "Email":1, "Verified":1, "Username": 1}):
    if str(hello['_id']) == theid:
      user = hello
      del user['Verified']
      user['Verified'] = True
      delete = {"_id": hello['_id']}
      mycol.delete_one(delete)
      mycol.insert_many([user])
      delcookie("hello")
      # debugging function
      # for i in mycol.find():
      #   if str(i['_id']) == theid:
      #     print(i['Verified'])
      return render_template("index.html", text="Your account has been verified! Log in again to do all the cool stuufff!", cookie=False, noti=False)

@app.route("/discordadd")
def discordmain():
  if checklog() == True or checklog() == None:
    pass
  else:
    return render_template("index.html", cookie=False, noti=False, search=search, text="You have been logged out!")
  cookies = getcookie("User")
  if cookies == False:
    return render_template("index.html", text="You have to login first!", cookie=cookies, noti=False)
  else:
    return render_template("discordadd.html")

@app.route("/discordadd", methods=['POST', 'GET'])
def discordadd():
  if request.method == "POST":
    if checklog() == True or checklog() == None:
      pass
    else:
      return render_template("index.html", cookie=False, noti=False, search=search, text="You have been logged out!")
    try:
      cookies = getcookie("User")
      if cookies == False:
        return render_template("index.html", text="You have to login first!", cookie=cookies, noti=False)
      else:
        document = [{
          "_id": int(request.form['nameandtag']),
          "Username": cookies,
          "Verified": False
        }]
        db = mainclient.AllUsers
        mycol = db.Discord
        mycol.insert_many(document)
        return render_template("index.html", text=f"Your discord account has been noted! Now go to the We Greek discord server and do the command z:linkwegreek {cookies} in the server!", cookie=cookies, noti=False)
    except:
      return render_template("index.html", text=f"A user has already tried to link their We Greek account with this id!", cookie=cookies, noti=False)

@app.route("/makepoll")
def makepollmain():
  if checklog() == True or checklog() == None:
    pass
  else:
    return render_template("index.html", cookie=False, noti=False, search=search, text="You have been logged out!")
  cookie = getcookie("User")
  if cookie == False:
    return render_template("index.html", text="You have to log in to make a post!", cookie=False, noti=False)
  else:
    verify = verifycheck(cookie)
    if verify == False:
      return render_template("index.html", text="You have to go on your email and verify your account to make a post!", cookie=cookie, noti=False)
    return render_template("makepoll.html")

@app.route("/makepoll", methods=['POST', 'GET'])
def makepoll():
  if request.method == "POST":
    if checklog() == True or checklog() == None:
      pass
    else:
      return render_template("index.html", cookie=False, noti=False, search=search, text="You have been logged out!")
    cookie = getcookie("User")
    if cookie == False:
      return render_template("index.html", text="You have to log in to make a post!", cookie=False, noti=False)
    else:
      verify = verifycheck(cookie)
      if verify == False:
        return render_template("index.html", text="You have to go on your email and verify your account to make a post!", cookie=cookie, noti=False)
    title = request.form['title']
    body = request.form['body']
    options = body.split("/")
    numberopt = len(options)
    if numberopt == 1:
      return render_template(
          "makepoll.html",
          text="You cannot only one option!")
    seen = []
    for number in options:
      if number in seen:
        return render_template(
          "makepoll.html",
          text="Two options you have provided are the same!")
      else:
        seen.append(number)
    db = mainclient["Threads"]
    mycol = db["Polls"]
    allids = []
    for doc in mycol.find({}, {"_id": 1}):
      xx = doc['_id']
      allids.append(xx)
    randomid = ""
    for i in range(15):
      number = random.randint(0, 9)
      randomid = str(number) + randomid
    while int(randomid) in allids:
      randomid = ""
      for i in range(15):
        number = random.randint(0, 9)
        randomid = str(number) + randomid
    optvote = []
    for option in options:
      thedict = {}
      thedict['Option name'] = option
      thedict['Votes'] = 0 
      thedict['Voters'] = []
      optvote.append(thedict)
    document = [{
        '_id': int(randomid),
        'Title': title,
        'Author': cookie,
        "Option/Votes": optvote
    }]
    mycol.insert_many(document)
    noti = cookie + " has made a new poll! Click here to check it is safe!"
    addnotiadmacs(f"/polls/{str(document[0]['_id'])}", noti)
    return redirect(f"/polls/{str(document[0]['_id'])}")
    
@app.route("/polls/<id>")
def checkpoll(id):
  if checklog() == True or checklog() == None:
    pass
  else:
    return render_template("index.html", cookie=False, noti=False, search=search, text="You have been logged out!")
  user = {}
  DB = mainclient.Threads
  MYCOL = DB.Polls
  allvotes = {}
  for poll in MYCOL.find():
    for i in poll['Option/Votes']:
      for x in i['Voters']:
        theindex = poll['Option/Votes'].index(i)
        allvotes[theindex] = x
  ids = []
  for i in MYCOL.find({}, {"_id":1, "Author":1}):
    theid = str(i['_id'])
    ids.append(theid)
  if id in ids:
    for i in MYCOL.find({}, {"_id":1, "Author":1}):
      if i['_id'] == int(id):
        author = i['Author']
    db = mainclient.AllUsers
    allcol = db.mainclient
    cookie = getcookie("User")
    if cookie == False:
      user['PERMS'] = "NONE"
    yourusername = cookie
    for doc in allcol.find({}, {"_id": 0, "Username": 1, "MOD":1, "Admin":1}):
      if doc['Username'] == yourusername:
        if doc['Admin'] == True:
          user['PERMS'] = "ADMIN"
        elif doc['MOD'] == True:
          user['PERMS'] = "MOD"
        elif author == yourusername:
          user['PERMS'] = "YOURPOST"
        else:
          user['PERMS'] = "USER"
    user['Username'] = cookie
    for doc in MYCOL.find():
      if doc['_id'] == int(id):
        for i in doc['Option/Votes']:
          theindex = doc['Option/Votes'].index(i)
          i['url'] = f"/votepoll/{str(id)}/{theindex}"
        return render_template("poll.html", doc=doc, user=user, allvotes=allvotes)
  else:
    return render_template("404.html")

@app.route("/poll/<id>")
def checkpoll2(id):
  if checklog() == True or checklog() == None:
    pass
  else:
    return render_template("index.html", cookie=False, noti=False, search=search, text="You have been logged out!")
  user = {}
  DB = mainclient.Threads
  MYCOL = DB.Polls
  allvotes = {}
  for poll in MYCOL.find():
    for i in poll['Option/Votes']:
      for x in i['Voters']:
        theindex = poll['Option/Votes'].index(i)
        allvotes[theindex] = x
  ids = []
  for i in MYCOL.find({}, {"_id":1, "Author":1}):
    theid = str(i['_id'])
    ids.append(theid)
  if id in ids:
    for i in MYCOL.find({}, {"_id":1, "Author":1}):
      if i['_id'] == int(id):
        author = i['Author']
    db = mainclient.AllUsers
    allcol = db.mainclient
    cookie = getcookie("User")
    if cookie == False:
      user['PERMS'] = "NONE"
    yourusername = cookie
    for doc in allcol.find({}, {"_id": 0, "Username": 1, "MOD":1, "Admin":1}):
      if doc['Username'] == yourusername:
        if doc['Admin'] == True:
          user['PERMS'] = "ADMIN"
        elif doc['MOD'] == True:
          user['PERMS'] = "MOD"
        elif author == yourusername:
          user['PERMS'] = "YOURPOST"
        else:
          user['PERMS'] = "USER"
    user['Username'] = cookie
    for doc in MYCOL.find():
      if doc['_id'] == int(id):
        for i in doc['Option/Votes']:
          theindex = doc['Option/Votes'].index(i)
          i['url'] = f"/votepoll/{str(id)}/{theindex}"
        return render_template("poll2.html", doc=doc, user=user, allvotes=allvotes)
  else:
    return render_template("404.html")

@app.route("/votepoll/<pollid>/<optionindex>")
def votepoll(pollid, optionindex):
  if checklog() == True or checklog() == None:
    pass
  else:
    return render_template("index.html", cookie=False, noti=False, search=search, text="You have been logged out!")
  DB = mainclient.Threads
  MYCOL = DB.Polls
  ids = []
  for i in MYCOL.find({}, {"_id":1}):
    theid = str(i['_id'])
    ids.append(theid)
  if pollid in ids:
    cookie = getcookie("User")
    if cookie == False:
      return render_template("index.html", text="You have to make an account to vote in a poll!", cookie=cookie, noti=False)
    else:
      verify = verifycheck(cookie)
      if verify == False:
        return render_template("index.html", text="You have to go on your email and verify your account to vote in a poll!", cookie=cookie, noti=False)
      for poll in MYCOL.find():
        if poll['_id'] == int(pollid):
          allvotes = {}
          for i in poll['Option/Votes']:
            for x in i['Voters']:
              theindex = poll['Option/Votes'].index(i)
              allvotes[theindex] = x
          try:
            voters = poll['Option/Votes'][int(optionindex)]['Voters']
            if cookie in voters:
              voters.remove(cookie)
              del poll['Option/Votes'][int(optionindex)]['Voters']
              poll['Option/Votes'][int(optionindex)]['Voters'] = voters
              votes = poll['Option/Votes'][int(optionindex)]['Votes']
              del poll['Option/Votes'][int(optionindex)]['Votes']
              poll['Option/Votes'][int(optionindex)]['Votes'] = votes - 1
            else:
              if cookie in allvotes.values():
                return redirect(f"/polls/{pollid}")
              else:
                voters.append(cookie)
                del poll['Option/Votes'][int(optionindex)]['Voters']
                poll['Option/Votes'][int(optionindex)]['Voters'] = voters
                votes = poll['Option/Votes'][int(optionindex)]['Votes']
                del poll['Option/Votes'][int(optionindex)]['Votes']
                poll['Option/Votes'][int(optionindex)]['Votes'] = votes + 1
            MYCOL.delete_one({"_id":int(pollid)})
            MYCOL.insert_many([poll])
            return redirect(f"/polls/{pollid}")
          except:
            return render_template("404.html")
  else:
    return render_template("404.html")

@app.route("/allpolls")
def allpolls():
  if checklog() == True or checklog() == None:
    pass
  else:
    return render_template("index.html", cookie=False, noti=False, search=search, text="You have been logged out!")
  DB = mainclient.Threads
  MYCOL = DB.Polls
  wikis = []
  for i in MYCOL.find({}, {"_id":1, "Title":1, "Author":1}):
    if len(i['Title']) > 10:
      title = i['Title']
      firstten = title[0:10]
      title = firstten + "..."
      del i['Title']
      i['Title'] = title
    i['URL'] = "/polls/" + str(i['_id'])
    wikis.append(i)
    random.shuffle(wikis)
  return render_template("allpolls.html", wikis=wikis)

@app.route("/deletepoll/<id>")
def deletepoll(id):
  if checklog() == True or checklog() == None:
    pass
  else:
    return render_template("index.html", cookie=False, noti=False, search=search, text="You have been logged out!")
  DB = mainclient.Threads
  MYCOL = DB.Polls
  ids = []
  for i in MYCOL.find({}, {"_id":1, "Author":1}):
    theid = str(i['_id'])
    ids.append(theid)
  if id in ids:
    for i in MYCOL.find({}, {"_id":0, "Author":1}):
      author = i['Author']
    db = mainclient.AllUsers
    allcol = db.mainclient
    user = {}
    cookie = getcookie("User")
    if cookie == False:
      user['PERMS'] = "NONE"
    else:
      yourusername = cookie
      for doc in allcol.find({}, {"_id": 0, "Username": 1, "MOD":1, "Admin":1}):
        if doc['Username'] == yourusername:
          if author == yourusername:
            user['PERMS'] = "YOURPOST"
          elif doc['MOD'] == True:
            user['PERMS'] = "MOD"
          elif doc['Admin'] == True:
            user['PERMS'] = "ADMIN"
          else:
            user['PERMS'] = "NONE"
      if user['PERMS'] != "NONE":
        delete = {"_id":int(id)}
        MYCOL.delete_one(delete)
        notificationsdb = mainclient.Notifications
        notificationscol = notificationsdb[cookie]
        for doc in notificationscol.find({}, {"_id":0, "Status":1}):
          if doc['Status'] == False:
            return render_template("index.html", cookie=cookie, noti=True, text="The poll has been deleted!")
        return render_template("index.html", cookie=cookie, noti=False, text="The poll has been deleted!")
      else:
        return render_template("404.html")
  else:
    return render_template("404.html")

@app.route("/changemail")
def changemailmain():
  if checklog() == True or checklog() == None:
    pass
  else:
    return render_template("index.html", cookie=False, noti=False, search=search, text="You have been logged out!")
  cookie = getcookie("User")
  if cookie == False:
    return render_template("index.html", text="You have to log in to make a post!", cookie=False, noti=False)
  else:
    return render_template("changemail.html")

@app.route("/changemail", methods=['POST', 'GET'])
def changemail():
  if request.method == "POST":
    if checklog() == True or checklog() == None:
      pass
    else:
      return render_template("index.html", cookie=False, noti=False, search=search, text="You have been logged out!")
    cookie = getcookie("User")
    if cookie == False:
      return render_template("index.html", text="You have to log in to make a post!", cookie=False, noti=False)
    email = request.form['email']
    db = mainclient.AllUsers
    mycol = db.AllEmails
    for i in mycol.find():
      if i['Username'] == cookie:
        delete = {"_id": i['_id']}
        mycol.delete_one(delete)
    document2 = [{
      "Username": cookie,
      "Email": email,
      "Verified": False
    }]
    mycol.insert_many(document2)
    return render_template("index.html", text="Your email has been changed! Now go to your email and verify your email!", cookie=cookie, noti=False)

@app.route("/resendverification")
def resendverification():
  if checklog() == True or checklog() == None:
    pass
  else:
    return render_template("index.html", cookie=False, noti=False, search=search, text="You have been logged out!")
  cookie = getcookie("User")
  if cookie == False:
    return render_template("index.html", text="You have to log in to make a post!", cookie=False, noti=False)
  db = mainclient.AllUsers
  mycol = db.AllEmails
  for i in mycol.find():
    if i['Username'] == cookie:
      if i['Verified'] == True:
        return render_template("index.html", text="You have already verified your email!", cookie=cookie, noti=False)
      else:
        email = i['Email']
        theid = i['_id']
        context = ssl.create_default_context()
        html = f"""
                    <html>
                      <body>
                        <p><strong>You have signed up for an account in We Greek!</strong><br>
                          Click <a href='https://Greek-Mythology-Wikipedia.wegreek.repl.co/emailverification/{str(theid)}'>here</a> to verify your account!
                        <br>
                  If you didn't make this account, reply back to this email saying this isn't your account and <strong>DO NOT</strong> click on the link or the user who made the account will get verified with your email!
                 <\p>
                      </body>
                    </html>
                """
        gmail_server = smtplib.SMTP('smtp.gmail.com', 587)
        message = MIMEMultipart("alternative")
        message["Subject"] = "Verification email"
        part2 = MIMEText(html, "html")
        message.attach(part2)
        gmail_server.starttls(context=context)
        gmail_server.login("wegreekofficial@gmail.com", os.getenv("mailpass"))
        message["From"] = "wegreekofficial@gmail.com"
        message["To"] = email
        gmail_server.sendmail("wegreekofficial@gmail.com", email, message.as_string())
        return render_template("index.html", text="Sent verification email!", cookie=cookie, noti=False)

@app.route("/deleteuser")
def deleteusermain():
  if checklog() == True or checklog() == None:
    pass
  else:
    return render_template("index.html", cookie=False, noti=False, search=search, text="You have been logged out!")
  cookie = getcookie("User")
  if cookie == False:
    return render_template("index.html", text="You have to make an account to delete a user!", cookie=cookie, noti=False)
  else:
    return render_template("deleteuser.html")

@app.route("/deleteuser", methods=['POST', 'GET'])
def deleteuser():
  if request.method == "POST":
    if checklog() == True or checklog() == None:
      pass
    else:
      return render_template("index.html", cookie=False, noti=False, search=search, text="You have been logged out!")
    cookie = getcookie("User")
    if cookie == False:
      return render_template("index.html", text="You have to make an account to delete a user!", cookie=cookie, noti=False)
    else:
      username = request.form['username']
      if username == cookie:
        db = mainclient.AllUsers
        mycol = db.mainclient
        for i in mycol.find():
          if i['Username'] == username:
            delete = {"_id": i['_id']}
            mycol.delete_one(delete)
        db = mainclient.AllUsers
        mycol = db.AllEmails
        for i in mycol.find():
          if i['Username'] == username:
            email = i['Email']
            html = f"""
                          <html>
                            <body>
                            <p><strong>Your We Greek Account, {username}, has been deleted!
                            </body>
                          </html>
                    """
            context = ssl.create_default_context()
            gmail_server = smtplib.SMTP('smtp.gmail.com', 587)
            message = MIMEMultipart("alternative")
            message["Subject"] = "Your We Greek Account"
            part2 = MIMEText(html, "html")
            message.attach(part2)
            gmail_server.starttls(context=context)
            gmail_server.login("wegreekofficial@gmail.com", os.getenv("mailpass"))
            message["From"] = "wegreekofficial@gmail.com"
            message["To"] = email
            gmail_server.sendmail("wegreekofficial@gmail.com", email, message.as_string())
            delete = {"_id": i['_id']}
            mycol.delete_one(delete)
        db = mainclient.AllUsers
        mycol = db.Discord
        for i in mycol.find():
          if i['Username'] == username:
            delete = {"_id": i['_id']}
            mycol.delete_one(delete)
        db = mainclient.Notifications
        mycol = db[username]
        mycol.drop()
        db = mainclient.Threads
        mycol = db.PostComments
        for i in mycol.find():
          if i['Author'] == username:
            delete = {"_id": i['_id']}
            mycol.delete_one(delete)
        db = mainclient.Threads
        mycol = db.Posts
        for i in mycol.find():
          if i['Author'] == username:
            delete = {"_id": i['_id']}
            mycol.delete_one(delete)
        db = mainclient.Threads
        mycol = db.Wikis
        for i in mycol.find():
          if i['Author'] == username:
            delete = {"_id": i['_id']}
            mycol.delete_one(delete)
        db = mainclient.Threads
        mycol = db.Polls
        for i in mycol.find():
          if i['Author'] == username:
            delete = {"_id": i['_id']}
            mycol.delete_one(delete)
        for i in mycol.find():
          for option in i['Option/Votes']:
            if username in option['Voters']:
              newdoc = i
              index = i['Option/Votes'].index(option)
              voters = i['Option/Votes'][index]['Voters']
              userindex = voters.index(username)
              del newdoc['Option/Votes'][index]['Voters']
              voters.pop(userindex)
              newdoc['Option/Votes'][index]['Voters'] = voters
              votes = newdoc['Option/Votes'][index]['Votes']
              del newdoc['Option/Votes'][index]['Votes']
              newdoc['Option/Votes'][index]['Votes'] = votes - 1
              mycol.delete_one({"_id": i['_id']})
              mycol.insert_many([newdoc])
        adb = mainclient.Views
        acol = adb.Wikis
        for i in acol.find():
          if username in i['Viewers']:
            doc = i
            index = doc['Viewers'].index(username)
            doc['Viewers'].pop(index)
            acol.delete_one({"_id": i['_id']})
            acol.insert_many([doc])
        adb = mainclient.Views
        acol = adb.Posts
        for i in acol.find():
          if username in i['Viewers']:
            doc = i
            index = doc['Viewers'].index(username)
            doc['Viewers'].pop(index)
            acol.delete_one({"_id": i['_id']})
            acol.insert_many([doc])
            
        delcookie("hello")
        return render_template("deleteuser.html", text=f"Everything deleted relating to {username}")
      else:
        return render_template("deleteuser.html", text="You cannot delete this user!")
  

@app.route("/rules")
def rules():
  if checklog() == True or checklog() == None:
    pass
  else:
    return render_template("index.html", cookie=False, noti=False, search=search, text="You have been logged out!")
  return render_template("rules.html")

@app.route("/discord")
def discord():
  return redirect("https://discord.gg/pUAFBUpur7")


@app.route('/favicon-ico')
def logo():
  return send_file('static/wegreeklogo.png')

