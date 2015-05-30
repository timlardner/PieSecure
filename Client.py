import socket
import datetime
import calendar,time
from Crypto.PublicKey import RSA
from Crypto import Random
import pickle

TCP_IP = '127.0.0.1'
TCP_PORT = 9999
BUFFER_SIZE = 1024
UID = str(calendar.timegm(time.gmtime()))

random_generator = Random.new().read
key = RSA.generate(1024, random_generator)
public_key = key.publickey()
keystring = public_key.exportKey()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    server.connect((TCP_IP, TCP_PORT))
except:
    print "Server not running"
    exit(1)
header = {'UID':UID, 'KEY':keystring}
server.send(pickle.dumps(header))

message = server.recv(2048)
print message
while True:
    time.sleep(20)
    to_send = {'command':'disconnect'}
    server.send(pickle.dumps(to_send))
    time.sleep(10)
    break
    #keep alive

server.close()
