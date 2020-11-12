from flask import Flask

app=Flask(__name__)

@app.route('/')
def home():
    return "<img src="{{ url_for('video_feed') }}" width="100%">"

@app.route('/video_feed')
def video_feed():
    return
def startApp():
    app.run(host='0.0.0.0')