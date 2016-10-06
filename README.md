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
In config.py
- Add these contents to config.py and save 
```
deltaKey = 'your delta api key'
CVip = 'the ip of the computer running the CV code'
CVport = the port number of the computer running the CV code as an integer
```
In daRealThing.py...
- Set the camera ip/port - `streamURLS`
- Set the ip/port of the webapp - `webpageIP`
- Add the Microsoft Cognitive Services API Key - `_key`

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

Pressing the enter key with your computer focused on the webapp page will trigger the CV code 
