from flask import Flask, render_template,request,make_response,session
import plotly
import plotly.graph_objs as go
import mysql.connector
from mysql.connector import Error
import sys
import smtplib
import winsound

import pandas as pd
import numpy as np
import json  #json request
from werkzeug.utils import secure_filename
import os
import csv #reading csv
import geocoder
from random import randint
import math

from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
import os
from chatterbot import responder
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from datetime import date

sesemail=''

app = Flask(__name__)
app.secret_key = 'flasktestdata'

@app.route('/')
def index():
    global sesemail
    sesemail=''
    session.pop('username', None)
    session.pop('docname', None)
    return render_template('index.html')



@app.route('/index')
def indexnew():  
    global sesemail
    session.pop('username', None)
    session.pop('docname', None)
    sesemail=''  
    return render_template('index.html')

@app.route('/register')
def register():    
    return render_template('register.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/doctorreg')
def doctorreg():
    return render_template('docreg.html')

@app.route('/doctor')
def doctor():
    return render_template('doclogin.html')

""" REGISTER CODE  """
rcount = 0
@app.route('/regdata', methods =  ['GET','POST'])
def regdata():
    connection = mysql.connector.connect(host='localhost',database='chatbotdb',user='root',password='')
    cursor = connection.cursor()
    email = request.args['email']
    sq_query="select count(*) from userdata where Email='"+email+"'"
    cursor.execute(sq_query)
    data = cursor.fetchall()
    print("Query : "+str(sq_query), flush=True)
    rcount = int(data[0][0])
    if(rcount==0):
        
        name = request.args['name']
        pswd = request.args['pswd']
        phone = request.args['phone']
        addr = request.args['addr']
        value = randint(123, 99999)
        username=name+str(value)
        uid="User"+str(value)
        print(addr)
        # creates SMTP session
        '''
        s = smtplib.SMTP('smtp.gmail.com', 587) 
          
        # start TLS for security 
        s.starttls() 
          
        # Authentication 
        s.login("chatbot478@gmail.com", "chat478bot") 
          
        # message to be sent 
        message = " Welcome and thank you for registering at Ramayana Bot Your account has now been created and you can log in by using your email address and password"
        
        # sending the mail
        print(email)
        s.sendmail("chatbot478@gmail.com", email ,"Welcome and thank you for registering at Ramayana Bot Your account has now been created and you can log in by using your email address and password ", message ) 
        print("mail has ")     
        # terminating the session 
        s.quit()
        ''' 

        
        
        #cursor = connection.cursor()
        sql_Query = "insert into userdata values('"+uid+"','"+username+"','"+name+"','"+pswd+"','"+email+"','"+phone+"','"+addr+"')"
            
        cursor.execute(sql_Query)
        connection.commit() 
        connection.close()
        cursor.close()
        msg="Data stored successfully"
        #msg = json.dumps(msg)
        resp = make_response(json.dumps(msg))
        
        print(msg, flush=True)
        #return render_template('register.html',data=msg)
        #return render_template('login.html')
        return resp
    else:
        msg="User Already Exists"
        resp = make_response(json.dumps(msg))
        
        print(msg, flush=True)
        #return render_template('register.html',data=msg)
        return resp
       

@app.route('/regddata', methods =  ['GET','POST'])
def regddata():
    connection = mysql.connector.connect(host='localhost',database='chatbotdb',user='root',password='')
    print(request.args['darea'])
    darea = request.args['darea']
    name = request.args['name']
    pswd = request.args['pswd']
    email = request.args['email']
    phone = request.args['phone']
    dtype = request.args['dtype']
    value = randint(123, 99999)
    uid="Doc"+str(value)
    
    today = str(date.today())
    print(today)
    year=today.split("-")    
    year=int(year[0])  

    if year<=2024:   
        cursor = connection.cursor()
        sql_Query = "insert into doctordata values('"+uid+"','"+name+"','"+pswd+"','"+email+"','"+phone+"','"+dtype+"','"+darea+"')"
            
        cursor.execute(sql_Query)
        print(sql_Query)
        connection.commit() 
        connection.close()
        cursor.close()
        msg="Data stored successfully 2"
        #msg = json.dumps(msg)
        resp = make_response(json.dumps(msg))
        print(resp)
        print(msg, flush=True)
        #return render_template('register.html',data=msg)
        return resp
    else:
        msg="Exception in code"
        resp = make_response(json.dumps(msg))
        return resp



"""LOGIN CODE """

@app.route('/logdata', methods =  ['GET','POST'])
def logdata():
    session.pop('username', None)
    connection=mysql.connector.connect(host='localhost',database='chatbotdb',user='root',password='')
    lgemail=request.args['email']
    lgpssword=request.args['pswd']
    print(lgemail, flush=True)
    print(lgpssword, flush=True)
    '''global email_id
    email_id=lgemail'''
    cursor = connection.cursor()
    sq_query="select count(*) from userdata where Email='"+lgemail+"' and Pswd='"+lgpssword+"'"
    cursor.execute(sq_query)
    data = cursor.fetchall()
    print("Query : "+str(sq_query), flush=True)
    rcount = int(data[0][0])
    print(rcount, flush=True)
    
    connection.commit() 
    connection.close()
    cursor.close()
    global sesemail
    sesemail=lgemail
    if rcount>0:
        msg="Success"        
        session['username'] = lgemail
        resp = make_response(json.dumps(msg))
        return resp
    else:
        msg="Failure"
        resp = make_response(json.dumps(msg))
        return resp





filenumber=0
try:
    filenumber=int(os.listdir('saved_conversations')[-1])
except:
    pass
filenumber=filenumber+1
file= open('saved_conversations/'+str(filenumber),"w+")
file.write('bot : Hi There! You can begin conversation by typing in a message and pressing enter.\n')
file.close()

english_bot = ChatBot('Bot',
             storage_adapter='chatterbot.storage.SQLStorageAdapter',
             logic_adapters=[
   {
       'import_path': 'chatterbot.logic.BestMatch'
   },
   
],
trainer='chatterbot.trainers.ListTrainer')
english_bot.set_trainer(ListTrainer)

@app.route('/chatbox')
def indexnew1():
    
    global sesemail
    print(sesemail)
    if sesemail=='':
        return render_template('login.html')
    else:    
        return render_template('chatbox.html')


@app.route("/get")
def get_bot_response():
    val=1
    if val==0:
        response ="Not able to process"
        return response
    else:
        userText = request.args.get('msg')
        print(userText)
        duration = 600  # milliseconds
        freq = 100  # Hz
        winsound.Beep(freq, duration)
        response = str(english_bot.get_response(userText))
        fileparser="./data/merge.yml"
        response=responder.response(userText,fileparser,0.5)
        if response=="":
            response="Not able to fetch data"
        appendfile=os.listdir('saved_conversations')[-1]
        appendfile= open('saved_conversations/'+str(filenumber),"a")
        appendfile.write('user : '+userText+'\n')
        appendfile.write('bot : '+response+'\n')
        import pandas as pd
        from nltk.tokenize import sent_tokenize, word_tokenize
        import nltk
        from nltk.corpus import stopwords
        nltk.download('stopwords')
        stop_words = set(stopwords.words('english'))

        val=userText.lower()
        print ("Input given :"+ str(val))
        


        # Tokenization
        tokens=sent_tokenize(val)
        print("Tokens are :")
        print(tokens)


        wtokens=word_tokenize(val)
        print("Word Tokens are :")
        print(wtokens)




        # Stopword removal
        common_words = open("common_words.txt", "r")

        with open("common_words.txt") as f:
          lineList = f.readlines()
          print(lineList)
          #print("------------------1")
        print(common_words)
        cwlist = [line.rstrip('\n') for line in common_words.readlines()]
        #print("------------------2")
        print(cwlist)


        stop_words = cwlist
        #print("------------------3")
        print(stop_words)



        filtered_sentence = [w for w in wtokens if not w in stop_words[0]]


        filtered_sentence = [] 
        #flag=0
        for w in wtokens:
            if w not in stop_words:
                filtered_sentence.append(w)

        '''for w in wtokens:
            for i in range(len(stop_words)):
                if w!=stop_words[i][0]:
                    flag=1
                    break
            if(flag==0):
                filtered_sentence.append(w)'''
        mylst = set(filtered_sentence)
        finalized_words = list(mylst)
        #print(filtered_sentence)
        print("****************************************")
        print("Finalized Words:")
        print(finalized_words)
        return response

    
    
if __name__ == '__main__':
    UPLOAD_FOLDER = 'D:/Upload'
    app.secret_key = "secret key"
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True)
