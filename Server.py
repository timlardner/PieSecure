import socket, threading, pickle, sqlite3

class ClientThread(threading.Thread):
    def __init__(self,ip,port,cid,key):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.CID = CID
        self.Key = key
        print "[+] New thread started for "+ip+":"+str(port)

    def run(self):    
        print "Connection from : "+ip+":"+str(port)
        message = "You are client "+self.CID
        clientsock.send("\nWelcome to the server. "+message+"\nYou may now begin sending commands.\n")
        data = "dummydata"
        while True:
            data = clientsock.recv(8)
            if not data:
                continue
            data = clientsock.recv(int(data))
            try:
                message = pickle.loads(data)
                command = message.get('command')
                if command == 'getKey':
                    CID = message.get('CID')
                    t = (CID,)
                    conn = sqlite3.connect('PieMessage.db')
                    c = conn.cursor()
                    c.execute('SELECT KEY FROM clients WHERE CID=?',t)
                    output = c.fetchone()
                    conn.close()
                    message={'command':'getKey','CID':CID,'KEY':output[0]}
                    n=str(len(pickle.dumps(message)))
                    clientsock.send(n.zfill(8))
                    clientsock.send(pickle.dumps(message))
                    print "Key for user "+CID+" returned to client "+self.CID+"\n"
                    #look up the thread for a given CID and return the private key
                elif command =='message':
                    print "Message command received from client "+CID
                    CID = message.get('CID')

                    conn = sqlite3.connect('PieMessage.db')
                    c = conn.cursor()
                    c.execute('SELECT ONLINE FROM clients WHERE CID=?',t)
                    output = c.fetchone()
                    conn.close()
                    if output[0] == 0:
                        #client is offline. cannot send message
                        message = {'command':'response','status':0}
                        n=str(len(pickle.dumps(message)))
                        clientsock.send(n.zfill(8))
                        clientsock.send(pickle.dumps(message))
                    else:
                        online_thread = clients.get(CID)
                        online_thread.message(self.CID,message.get('Content'))
                        message = {'command':'response','status':1}
                        n=str(len(pickle.dumps(message)))
                        clientsock.send(n.zfill(8))
                        clientsock.send(pickle.dumps(message))
                        #forward the attached encrypted message to a given CID
                elif command =='disconnect':
                    print "Received disconnect command. Setting client to offline.\n"
                    conn = sqlite3.connect('PieMessage.db')
                    c = conn.cursor()
                    c.execute('UPDATE clients SET ONLINE = 0 WHERE CID = ?',(self.CID,))
                    conn.commit()
                    conn.close()
                    break

            except:
                print " "

    def message(self, CID, text):
        print "Sending message to client..."
        message = {'command':'message', 'CID':CID, 'content':text}
        n=str(len(pickle.dumps(message)))
        clientsock.send(n.zfill(8))
        clientsock.send(pickle.dumps(message))


host = "0.0.0.0"
port = 9999

tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcpsock.bind((host,port))
threads = []
clients = {}
while True:
    tcpsock.listen(4)
    print "\nListening for incoming connections..."
    (clientsock, (ip, port)) = tcpsock.accept()
    print "\nReceived connection. Awaiting client details..."
    data = clientsock.recv(2048)
    header = data
    print "Received header"
    header = pickle.loads(data)
    CID = header.get('UID')
    KEY = header.get('KEY')

    t = (CID,)
    conn = sqlite3.connect('PieMessage.db')
    c = conn.cursor()
    c.execute('SELECT EXISTS(SELECT * FROM clients WHERE CID=?)',t)
    output = c.fetchone()
    output_str = str(output)

    if output_str[1]=='0':
        print "Client does not exist in database.\nAdding client\n"
        c.execute('INSERT INTO clients VALUES (''?'',''?'',1)',(CID,KEY))
        conn.commit()
        print "Done\n"
    else:
        print "Client exists in database.\nSetting to online\n"
        c.execute('UPDATE clients SET ONLINE = 1 WHERE CID = ?',(CID,))
        conn.commit()
        print "Done\n"
    conn.close()
    newthread = ClientThread(ip,port,CID,KEY)
    newthread.start()
    threads.append(newthread)
    clients[CID] = newthread

for t in threads:
    t.join()