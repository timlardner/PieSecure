import socket
import datetime
import calendar,time
from Crypto.PublicKey import RSA
from Crypto import Random
import pickle
from threading import Thread
import sys

STOP_FLAG = 0
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
keys = {}
server.send(pickle.dumps(header))
message = server.recv(2048)
print message

def recv():
    while True:
        data = server.recv(8)
        data = server.recv(int(data))
        message = pickle.loads(data)
        if message.get('command') == 'message':
            encrypted_message = message.get('content')
            try:
                decrypted_message = key.decrypt(encrypted_message[0])
            except:
                print "Error decrypting message. Corrupt?"
                continue
            print "New message from " + message.get('CID')+"!"
            print decrypted_message
        elif message.get('command') == 'response':
            success = message.get('status')
            if success==1:
                print "Message sent successfully"
            else:
                print "Failed to send message"
        elif message.get('command') == 'getKey':
            print 'Key received. Adding to dictionary.'
            rsa_pubkey = message.get('KEY')
            pubkey = RSA.importKey(rsa_pubkey)
            keys[message.get('CID')] = pubkey

def message(CID, text):
    if CID in keys.keys():
        pubkey = keys.get(CID)
    else:
        print "Requesting public key from server for user "+UID
        to_send = {'command':'getKey','CID':UID}
        n=str(len(pickle.dumps(to_send)))
        server.send(n.zfill(8))
        server.send(pickle.dumps(to_send))
        i=0
        while CID not in keys.keys():
            time.sleep(1)
            if i>5:
                return
        pubkey = keys.get(CID)
    encrypted_text = pubkey.encrypt(text, 32)
    to_send = {'command':'message','CID':CID,'Content':encrypted_text}
    n=str(len(pickle.dumps(to_send)))
    server.send(n.zfill(8))
    server.send(pickle.dumps(to_send))

def disconnect():
    to_send = {'command':'disconnect'}
    n=str(len(pickle.dumps(to_send)))
    server.send(n.zfill(8))
    server.send(pickle.dumps(to_send))
    sys.exit()


Thread(target=recv).start()

while True:
    time.sleep(3)

    message(24,'Hello')
    message(UID,'This is a test')
    time.sleep(10)

    disconnect()



