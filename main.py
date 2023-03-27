from twilio.twiml.messaging_response import MessagingResponse
from flask import Flask, request, render_template, flash, redirect, url_for
from flask_socketio import SocketIO, emit
import sqlite3
import secrets

secret_key = secrets.token_hex(16) # generates a 32-character random string

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///messages.db'
app.config['SECRET_KEY'] = secret_key
socketio = SocketIO(app)


@app.route('/')
def index():
    # Fetch all messages from the database
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()
    c.execute('SELECT * FROM messages')
    messages = c.fetchall()
    conn.close()
    
    # Render the template with the messages
    return render_template('index.html', messages=messages, enumerate=enumerate, len=len)

@app.route('/sms', methods=['POST'])
def sms():
    message_body = request.form['Body']
    sender_number = request.form['From']
    
    # Insert the message and sender's phone number into the database
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()
    c.execute('INSERT INTO messages (message, sender_number) VALUES (?, ?)', (message_body, sender_number))
    conn.commit()
    conn.close()

    # Emit a 'new message' event to all connected clients
    socketio.emit('new_message', {'message_body': message_body, 'sender_number': sender_number})

# Send a response back to the sender
# resp = MessagingResponse()
# resp.message('Thanks for your message!')
# return str(resp)

@app.route("/delete/<int:message_id>", methods=['POST'])
def delete(message_id):
    """Delete the message with the given id from the database."""
    conn = sqlite3.connect("messages.db")
    c = conn.cursor()
    c.execute("DELETE FROM messages WHERE id=?", (message_id,))
    conn.commit()
    conn.close()
    flash("Message deleted!")
    return redirect(url_for("index"))

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, port=5002)