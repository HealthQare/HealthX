
from flask import Flask, render_template, request, redirect
import sqlite3
import smtplib
import os
from datetime import datetime, timedelta

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')




def send_email(to_email):
    
    smtp_server = "smtp.gmail.com" 
    smtp_port = 587 
    smtp_username = "suhailskhan99@gmail.com" 
    smtp_password = "SKHAN7574" 

   
    message = MIMEMultipart()
    message['From'] = smtp_username
    message['To'] = to_email
    message['Subject'] = "Medication Reminder"

   
    message_body = f"Reminder: It's time to take your medicine)."
    # message_body = f"Reminder: It's time to take {med_name} ({med_dose})."

    message.attach(MIMEText(message_body, 'plain'))

    
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(smtp_username, smtp_password)
        server.sendmail(smtp_username, to_email, message.as_string())




@app.route('/add', methods=['POST'])
def add():
    email = request.form['email']
    dose = request.form['dose']
    frequency = request.form['frequency']
    start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
    end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
    time = request.form['time']
    conn = sqlite3.connect('medications.db')
    c = conn.cursor()
    c.execute('INSERT INTO medications (email, dose, frequency, start_date, end_date,time) VALUES (?, ?, ?, ?, ?,?)',
              (email, dose, frequency, start_date, end_date,time))
    conn.commit()
    conn.close()
    send_email(email)
    return redirect('/')

@app.route('/medications')
def medications():
    conn = sqlite3.connect('medications.db')
    c = conn.cursor()
    c.execute('SELECT * FROM medications')
    meds = c.fetchall()
    conn.close()
    return render_template('medications.html', meds=meds)

@app.route('/delete/<int:id>')
def delete(id):
    conn = sqlite3.connect('medications.db')
    c = conn.cursor()
    c.execute('DELETE FROM medications WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect('/medications')

@app.route('/reminder')
def reminder():
    now = datetime.now()
    conn = sqlite3.connect('medications.db')
    c = conn.cursor()
    c.execute('SELECT * FROM medications')
    meds = c.fetchall()
    reminders = []
    for med in meds:
        start_date = datetime.strptime(str(med[4]), '%Y-%m-%d %H:%M:%S')
        end_date = datetime.strptime(str(med[5]), '%Y-%m-%d %H:%M:%S')
        if start_date <= now <= end_date:
            days_since_start = (now - start_date).days
            if days_since_start % med[3] == 0:
                time_due = start_date + timedelta(days=days_since_start, hours=med[2])
                reminder = (med[0], med[1], time_due)
                reminders.append(reminder)
    conn.close()
    return render_template('reminder.html', reminders=reminders)



if __name__ == '__main__':
    app.run(debug=True)