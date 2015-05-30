import socket
import datetime
import calendar, time
from Crypto.PublicKey import RSA
from Crypto.Hash import MD5
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

hash = MD5.new(keystring).digest()
signature = key.sign(hash, random_generator)


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    server.connect((TCP_IP, TCP_PORT))
except:
    print "Server not running"
    exit(1)
header = {'UID': UID, 'KEY': keystring}
message_queue = []
keys = {}
server.send(pickle.dumps(header))
message = server.recv(2048)
print message


def recv():
    while True:
        data = server.recv(8)
        if not data:
            continue
        data = server.recv(int(data))
        message = pickle.loads(data)
        if message.get('command') == 'message':
            encrypted_message = message.get('content')
            try:
                decrypted_message = key.decrypt(encrypted_message[0])
            except:
                print "Error decrypting message. Corrupt?"
                continue
            message['content'] = decrypted_message
            message_queue.append(message)
        elif message.get('command') == 'response':
            message_queue.append(message)
        elif message.get('command') == 'getKey':
            rsa_pubkey = message.get('KEY')
            pubkey = RSA.importKey(rsa_pubkey)
            keys[message.get('CID')] = pubkey
            message_queue.append(message)
def output():
    print "Display server running"
    while True:
        while len(message_queue) != 0:
            message = message_queue.pop()
            if message.get('command') == 'message':
                print "\n\n****************************"
                print "New message from " + message.get('CID') + "!\n"
                print message.get('content')
                print "\n\n****************************"
            elif message.get('command') == 'response':
                success = message.get('status')
                if success == 1:
                    print "Message sent successfully"
                else:
                    print "Failed to send message"
            elif message.get('command') == 'getKey':
                print "Public key for "+ message.get('CID') + " added to dictionary."

def message(CID, text):
    if CID in keys.keys():
        pubkey = keys.get(CID)
    else:
        print "Requesting public key from server for user " + UID
        to_send = {'command': 'getKey', 'CID': UID}
        n = str(len(pickle.dumps(to_send)))
        server.send(n.zfill(8))
        server.send(pickle.dumps(to_send))
        i = 0
        while CID not in keys.keys():
            time.sleep(1)
            if i > 5:
                print "Did not receive a public key"
                return
        pubkey = keys.get(CID)
    print "Beginning to send message..."
    encrypted_text = pubkey.encrypt(text, 32)
    to_send = {'command': 'message', 'CID': CID, 'Content': encrypted_text}
    n = str(len(pickle.dumps(to_send)))
    server.send(n.zfill(8))
    server.send(pickle.dumps(to_send))


def disconnect():
    to_send = {'command': 'disconnect'}
    n = str(len(pickle.dumps(to_send)))
    server.send(n.zfill(8))
    server.send(pickle.dumps(to_send))
    print "Quitting..."
    sys.exit()


Thread(target=recv).start()
Thread(target=output).start()

while True:
    UID = raw_input("Enter a UID to send a message\n")
    if UID == 'exit':
        disconnect()
    text = raw_input("Enter some text to send\n")
    message(UID, text)
