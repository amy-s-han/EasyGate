# EasyGate
Minimizes boarding time at the gate and ensures on time departures by predicting and preventing overhead bin overflow
![alt tag](http://i.imgur.com/ieNjdcM.png)

## The Stack
- OpenCV
- Flask
- Socket.io
- Microsoft Cognitive Services API

## Dependencies
- [Flask](http://flask.pocoo.org/)
- [Flask-SocketIO](https://flask-socketio.readthedocs.io)
- [IP Webcam](https://play.google.com/store/apps/details?id=com.pas.webcam&hl=en) on your Android device
- OpenCV for Python

## Running
### Set up your config.py
- Create a config.py in the same directory as app.py
- Add these contents and save
```
deltaKey = 'your delta api key'
CVip = 'the ip of the computer running the CV code'
CVport = 'the port number of the computer running the CV code
```

### Run the webapp
```
$ export FLASK_APP=app.py
$ flask run --host=0.0.0.0
```
The webapp should served on http://localhost:5000

### Run the CV operations
```
$ python daRealThing.py
```
