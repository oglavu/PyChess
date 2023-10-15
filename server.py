import socket
import threading
import consts

class LRU_Cache:
    def __init__(self, capacity, firstUser):
        self.currUser = firstUser
        self.currUserCount = 0
        self.capacity = capacity
        self.lst = []
        self.saved = False
    def add(self, data, user):
        self.currUserCount += 1
        if (self.currUser != user and self.currUserCount >= self.capacity):
            self.currUser = (self.currUser + 1) % 2
            self.currUserCount = 1
            self.lst.append(data)
        elif self.currUser != user:
            return
        elif self.currUser == user and self.currUserCount > self.capacity:
            self.lst.pop(-2)
            self.lst.append(data)
        else:
            self.lst.append(data)
    def clear(self):
        self.__init__(self.capacity, self.currUser)
    def prepareLog(self):
        s = ""
        for i in range(1, len(self.lst)):
            s += self.lst[i-1].decode("utf-8") + ':'
            s += self.lst[i].decode("utf-8") + ','
        s += '\n'
        return s
    def writeLog(self):
        if not self.saved:
            with open(consts.LOG_FILE_NAME, "a") as f:
                f.write(self.prepareLog())
            self.saved = True


#Variables for holding information about connections
connections = []
cache = LRU_Cache(capacity=2, firstUser=0)

#Client class, new instance created for each connected client
#Each instance has the socket and address that is associated with items
#Along with an assigned ID and a name chosen by the client
class Client(threading.Thread):
    def __init__(self, socket, address, id, name, signal):
        threading.Thread.__init__(self)
        self.socket = socket
        self.address = address
        self.id = id
        self.name = name
        self.signal = signal
    
    def __str__(self):
        return str(self.id) + " " + str(self.address)
    
    #Attempt to get data from client
    #If unable to, assume client has disconnected and remove him from server data
    #If able to and we get data back, print it in the server and send it back to every
    #client aside from the client that has sent it
    #.decode is used to convert the byte data into a printable string
    def run(self):
        connections[-1].socket.sendall(self.name.encode("utf-8"))
        while self.signal:
            try:
                data = self.socket.recv(consts.TRANSMISSION_DATA_SIZE)
            except:
                self.signal = False
                data = None
            if data:
                print("[CLIENT] ID " + str(self.id) + ": " + pos_to_tile(data.decode("utf-8")))
                if data.decode("utf-8") == consts.DISCONNECT_MESSAGE:
                    self.signal = False
                elif data.decode("utf-8") == consts.REMATCH_MESSAGE:
                    cache.writeLog()
                    cache.clear()
                else:
                    cache.add(data, self.id)
                for client in connections:
                    if client.id != self.id:
                        client.socket.sendall(data)
        
        connections.remove(self)
        print("[SERVER] Client " + str(self.address) + " has disconnected")
        cache.writeLog()
        print("[SERVER] This game has been saved")

#Wait for new connections
def newConnections(socket):
    while True:
        sock, address = socket.accept()
        if len(connections) == 2:
            sock.sendall(consts.DISCONNECT_MESSAGE.encode("utf-8"))
        else:
            c = Client(sock, address, len(connections), "b0000000" if len(connections) else "w0000000", True)
            connections.append(c)
            connections[-1].start()
            print("[SERVER] New connection at ID " + str(connections[-1]))
            if not len(connections) % 2:
                connections[-1].socket.sendall("ready000".encode("utf-8"))
                connections[-2].socket.sendall("ready000".encode("utf-8"))

def pos_to_tile(pos: tuple[str]):
    if (pos == consts.DISCONNECT_MESSAGE or pos == consts.REMATCH_MESSAGE or
            pos == consts.DECLINE_MESSAGE or pos == consts.DRAW_MESSAGE or pos == consts.SURRENDER_MESSAGE):
        return pos
    x =int(pos[:4]) - consts.MARGIN
    y =int(pos[4:8]) - consts.HEADER

    return chr(ord('a') + (x//consts.SIDE)) + str(8 - y//consts.SIDE)

def main():
    print("[SERVER] Server started successfully")

    #Create new server socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((consts.HOST, consts.PORT))
    sock.listen(2)

    #Create new thread to wait for connections
    newConnectionsThread = threading.Thread(target = newConnections, args = (sock,))
    newConnectionsThread.start()

if __name__ == "__main__":
    main()