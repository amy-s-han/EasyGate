import socket

ip = "128.61.28.102"
port = 5005
message = "TAKEPIC"
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(message, (ip, port))