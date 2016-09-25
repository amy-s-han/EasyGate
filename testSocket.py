import urllib2
import json

'''
import socket

ip = "127.0.0.1"
port = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((ip, port))

while True:
	data, addr = sock.recvfrom(1024)
	print data


'''

data = {"result": "cayla"}


req = urllib2.Request('http://127.0.0.1:5000/submitCVResult')
req.add_header('Content-Type', 'application/json')

response = urllib2.urlopen(req, json.dumps(data))