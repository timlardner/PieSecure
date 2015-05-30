import socket, threading, pickle

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
        message = "You are client "+CID
        clientsock.send("\nWelcome to the server. "+message+"\nYou may now begin sending commands.\n")
        data = "dummydata"
        while len(data):
            data = clientsock.recv(2048)
            print "Received "+ str(len(data))+ " content " + data
            try:
                message = pickle.loads(data)
                command = message.get('command')
                if command == 'getKey':
                    print "1"
                    #look up the thread for a given CID and return the private key
                elif command =='message':
                    print "2"
                    #forward the attached encrypted message to a given CID
                elif command =='disconnect':
                    break

            except:
                print "Didn't receive picked data\n"

            print "Client sent : "+data
            clientsock.send("You sent me : "+data)
        print "Client disconnected..."


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
    newthread = ClientThread(ip,port,CID,KEY)
    newthread.start()
    threads.append(newthread)
    clients[CID] = newthread

for t in threads:
    t.join()