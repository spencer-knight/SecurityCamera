import smtplib, ssl
import json
import util

settings = util.getSettings()
notifacationGroup = settings["alertGroup"]

def alertEmail(receiver_email, message = "\nMotion detected!"):
    port = 465  
    smtp_server = "smtp.gmail.com"
    sender_email = str(settings["emailAddress"])  
    password = str(settings["emailPassword"])

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)

def alertGroup( message = "\n Motion detected!"):
    if True:
        for x in notifacationGroup:
            alertEmail( x, message)
        print("Finished alerting")