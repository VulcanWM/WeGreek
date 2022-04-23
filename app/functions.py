from flask import session
import pymongo
import os
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
clientm = os.getenv("clientm")
mainclient = pymongo.MongoClient(clientm)

def addcookie(key, value):
  session[key] = value


def delcookie(keyname):
  session.clear()

def getcookie(key):
  try:
    if (x := session.get(key)):
      return x
    else:
      return False
  except:
    return False

def votechange(username, number):
  db = mainclient.AllUsers
  mycol = db.mainclient
  for user in mycol.find({}, {"_id":1, "Username":1, "Password":1, "Votes":1, "Description":1, "Admin":1, "MOD":1}):
    if user['Username'] == username:
      password = user['Password']
      votes = user['Votes'] + int(number)
      desc = user['Description']
      admin = user['Admin']
      mod = user['MOD']
      theid = user['_id']
      delete = {"_id": theid}
      mycol.delete_one(delete)
      document = [{
        "Username":username,
        "Password":password,
        "Votes":votes,
        "Description": desc,
        "Admin": admin,
        "MOD": mod
      }]
      mycol.insert_many(document)

def addnotiadmacs(url, noti):
  db = mainclient.ADMACS
  mycol = db.Notifications
  document = [{
    "Notification": noti,
    "Url": url,
    "Status": False
  }]
  mycol.insert_many(document)
  html = f"""
                <html>
                  <body>
                  <a href='https://wegreek.vulcanwm.com{url}'>{noti}</a>
                  </body>
                </html>
          """
  context = ssl.create_default_context()
  gmail_server = smtplib.SMTP('smtp.gmail.com', 587)
  message = MIMEMultipart("alternative")
  message["Subject"] = "Verification email"
  part2 = MIMEText(html, "html")
  message.attach(part2)
  gmail_server.starttls(context=context)
  gmail_server.login("wegreekofficial@gmail.com", os.getenv("mailpass"))
  email = "wegreekofficial@gmail.com"
  message["From"] = "wegreekofficial@gmail.com"
  message["To"] = email
  gmail_server.sendmail("wegreekofficial@gmail.com", email, message.as_string())

def allusers():
  db = mainclient.AllUsers
  mycol = db.mainclient
  allusers = []
  for user in mycol.find({}, {"_id":1, "Username":1}):
    allusers.append(user['Username'])
  print(allusers)
  return allusers

def verifycheck(username):
  thedb = mainclient.AllUsers
  mycol = thedb.AllEmails
  for user in mycol.find():
    if user['Username'] == username:
      if user['Verified'] == True:
        return True
      else:
        return False
  return False

def getemail(username):
  thedb = mainclient.AllUsers
  mycol = thedb.AllEmails
  for user in mycol.find():
    if user['Username'] == username:
      return user['Email']
  return False

def sendemail(username, noti, url):
  email = getemail(username)
  html = f"""
                <html>
                  <body>
                   <a href='https://wegreek.vulcanwm.com{url}'>{noti}</a>
                  </body>
                </html>
          """
  context = ssl.create_default_context()
  gmail_server = smtplib.SMTP('smtp.gmail.com', 587)
  print("start")
  message = MIMEMultipart("alternative")
  message["Subject"] = "Verification email"
  part2 = MIMEText(html, "html")
  message.attach(part2)
  print("attached")
  gmail_server.starttls(context=context)
  print("some more")
  gmail_server.login("wegreekofficial@gmail.com", os.getenv("mailpass"))
  print("logged in")
  message["From"] = "wegreekofficial@gmail.com"
  message["To"] = email
  print("nearly there")
  gmail_server.sendmail("wegreekofficial@gmail.com", email, message.as_string())
  print("ayy done")

def checklog():
  username = getcookie("User")
  if username == False:
    return None
  db = mainclient.AllUsers
  mycol = db.mainclient
  for user in mycol.find():
    if user['Username'] == username:
      return True
  delcookie("hellothere")
  return False