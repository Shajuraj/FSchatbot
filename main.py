#!C:\Python\Python38\python.exe
from flask import Flask, render_template, request, url_for,redirect
from chatterbot import ChatBot
from chatterbot.response_selection import get_random_response
import random
import csv
import os
from chatterbot.trainers import ChatterBotCorpusTrainer
from flask_mysqldb import MySQL
from flask_cors import CORS
from botConfig import botAvatar,titleBg,sendIcon,micIcon,confidenceLevel,useGoogle,myBotName,refresh
import logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app)
chatbotName = myBotName
print("Bot Name set to: " + chatbotName)
print("Avatar is " + botAvatar)
print("titleBg is " + titleBg)
print("sendIcon is " + sendIcon)
print("micIcon is " + micIcon)
print("refreshIcon is " + refresh)
print("Confidence level set to " + str(confidenceLevel))

#Create Log file
try:
    file = open('BotLog.csv', 'r')
except IOError:
    file = open('BotLog.csv', 'w')

bot = ChatBot(
    "ChatBot",
    logic_adapters=[
        {
            'import_path': 'chatterbot.logic.BestMatch'
        },
        {
            'import_path': 'chatterbot.logic.LowConfidenceAdapter',
            'threshold': confidenceLevel,
            'default_response': 'IDKresponse'
        }
    ],
    response_selection_method=get_random_response,
    storage_adapter="chatterbot.storage.SQLStorageAdapter",
    database="botData.sqlite3"
)
bot.read_only=True #Comment this out if you want the bot to learn based on experience
print("Bot Learn Read Only:" + str(bot.read_only))


#bot.set_trainer(ChatterBotCorpusTrainer)
#bot.train("data/data.yml")

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'DEMO'
mysql = MySQL(app)



def tryGoogle(myQuery):
    return "<br><br>Would you like to refer Google: <a target='_blank' href='https://www.google.com/search?q=" + myQuery + "'>" + myQuery + "</a>"


@app.route("/")
def index():
    return render_template("index.html",botAvatar=botAvatar,titleBg=titleBg,sendIcon=sendIcon,micIcon=micIcon,refresh=refresh)

@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    botReply = str(bot.get_response(userText))
    if botReply is "IDKresponse":
        botReply = str(bot.get_response('IDKnull'))
        if useGoogle == "yes":
            botReply = botReply + tryGoogle(userText)
    print("Logging to CSV file now")
    with open('BotLog.csv', 'a', newline='') as logFile:
        newFileWriter = csv.writer(logFile)
        newFileWriter.writerow([userText, botReply])
        logFile.close()
    return botReply



@app.route('/insert', methods = ["POST"])
def insert():
 if request.method == "POST":
    name = request.form['name']
    phone = request.form['phone']
    email = request.form['email']
    purpose = request.form['purpose']

    mycursor = mysql.connection.cursor()
    mycursor.execute("INSERT INTO contact_informations (NAME,PHONE,EMAIL,PURPOSE) VALUES (%s,%s,%s,%s)",(name,phone,email,purpose))
    print(name,phone,email,purpose)
    mysql.connection.commit()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run()