# Preference file contains username, prompt_email, prompt_phone

from threading import Thread
import os.path
import Crypto.PublicKey.RSA as RSA
from Crypto.Hash import MD5
from Crypto import Random
import socket
import time
import logging
import pickle

SAVEFILE = 'PM.pem'
PREFILE = 'prefs.pm'
TCP_IP = '127.0.0.1'
TCP_PORT = 9999

state_queue = []
message_queue = []
log = []

class ClientStates:
    def __init__(self):
        self.username = []
        self.phone = []
        self.email = []
        self.publickey = []
        self.server = []
        self.preferences = {}

        self.username_valid = -1
        state_queue.append('initialise')
        Thread(target=self.program).start()

    def output(self):
        print 'Consume the message queue here'

    def listener(self):
        while True:
            data = self.server.recv(8)
            if not data:
                continue
            data = self.server.recv(int(data))
            message = pickle.loads(data)
            if message.get('command') == 'keyCheck':
                if message.get('content'):
                    self.username = message.get('username')
                    self.phone = message.get('phone')
                    self.email = message.get('email')
                    state_queue.append('signupExisting')
                else:
                    state_queue.append('signupNew')
            elif message.get('command') == 'checkUsername'
                status = message.get('status')
                if status == 1:
                    self.username_valid = 1
                else:
                    self.username_valid = 0
            elif message.get('command') == 'auth':
                status = message.get('status')
                if status == 1:
                    print "Client successfully authenticated"
                    state_queue.append('ready')
                elif status == 2:
                    print "Public key not recognised"
                    # Here, we give an option to delete the public key and start again
                elif status == 3:
                    print "Public key verified, but username does not match"
                    state_queue.append('login')


    def program(self):
        while True:
            state = message_queue.pop()
            if state == 'initialise':
                if os.path.isfile(SAVEFILE):
                    f = open(SAVEFILE,'r')
                    key = RSA.importKey(f.read())
                    f.close()
                else:
                    random_generator = Random.new().read
                    key = RSA.generate(2048)
                    f = open(SAVEFILE,'w')
                    f.write(RSA.exportKey('PEM'))
                    f.close()
                self.publickey = key.publickey()
                state_queue.append('connect')
            elif state=='connect':
                self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                tries = 0
                while True:
                    try:
                        self.server.connect((TCP_IP, TCP_PORT))
                        break
                    except:
                        tries = tries + 1
                        logging.info('Server connect failed')
                        time.sleep(1)
                        if tries > 3:
                            logging.error('Cannot connect to server')
                            exit(1)
                        else:
                            logging.info('Retrying')
                state_queue.append('login')
            elif state=='login':
                if os.path.isfile(PREFILE): #User account exists
                    f = open(PREFILE,'r')
                    self.preferences = pickle.loads(f.read())
                    f.close()
                    logging.debug('User preferences loaded. Going to authentication')
                    state_queue.append('auth')
                else: # no preferences
                    print "No preference files have been found."
                    logging.debug('Checking to see if public key exists in server database')
                    message = {'command': 'keyCheck', 'key': self.publickey.exportKey()}
                    n = str(len(pickle.dumps(message)))
                    self.server.send(n.zfill(8))
                    self.server.send(pickle.dumps(message))
            elif state=='signupExisting':
                print "Account found. Username is "+ self.username
                if self.email == "":
                    state_queue.append('update_email')
                    state_queue.append('auth')
                else:
                    state_queue.append('auth')
                    self.preferences = {'username': self.username, 'emailPrompt': 0}
                    f = open(PREFILE,'w')
                    f.write(pickle.dumps(self.preferences))
                    f.close()
                # We'll do phone numbers here too once we get an iphone app working...
            elif state=='signupNew':
                valid = False
                while not valid:
                    desired_username = raw_input("Enter a desired username")
                    message = {'command':'checkUsername','username':desired_username}
                    while self.username_valid == -1:
                        time.sleep(1)
                    if self.username_valid == 1:
                        valid = True
                    else:
                        self.username_valid = -1
                        print "Sorry. Username taken."
                self.username = desired_username
                print "Your new username is " + self.username
                message = {'command':'register','username':self.username,'key':self.publickey.exportKey()}
                n = str(len(pickle.dumps(message)))
                self.server.send(n.zfill(8))
                self.server.send(pickle.dumps(message))
                state_queue.append('update_email')
                state_queue.append('auth')
            elif state=='update_email':
                email = raw_input("No email address on file. Enter an email address?")
                if email.lower() == 'no'or email.lower == "":
                    email_ask = raw_input("Would you like me to remind you next time (yes/no)?")
                    if email_ask.lower() == "no":
                        email_ask = 0
                    else:
                        email_ask = 1
                else:
                    hash = MD5.new(email).digest()
                    signature = key.sign(hash, random_generator)
                    message = {'command':'infoUpdate','email':email,'username':self.username,'signature':signature}
                    n = str(len(pickle.dumps(message)))
                    self.server.send(n.zfill(8))
                    self.server.send(pickle.dumps(message))
                    email_ask = 0
                self.preferences = {'username':self.username,'emailPrompt':email_ask}
                f = open(PREFILE,'w')
                f.write(pickle.dumps(self.preferences))
                f.close()
            elif state=='auth':
                #We have a desired username and an existing key
                hash = MD5.new(self.publickey.exportKey()).digest()
                signature = key.sign(hash, random_generator)
                message = {'command':'auth','signature':signature,'username':self.username}

