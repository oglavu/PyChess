import socket
import threading
import consts

class Client:
    def __init__(self):
        self.color = None
        self.sock = None
        self.thread = None
        self.data = None
        self.signal = False
        self.ready = False

    def connect(self):
        #Attempt connection to server
        #if successfull returns 0 elsewise 1
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((consts.HOST, consts.PORT))
            self.signal = True
        except:
            print("[SERVER] Couldn't establish connection with the server")
            return

        #Create new thread to wait for data
        self.thread = threading.Thread(target = self.receive)
        self.thread.start()
        print("[CLIENT] You have been connected to the server")

    def disconnect(self):
        try:
            if not self.sock:
                return 
            self.sock.sendall(consts.DISCONNECT_MESSAGE.encode("utf-8"))
            self.sock.close()
            self.__init__()
        except:
            print("[SERVER] Server has been shut down")

    def send_message(self, data):
        try:
            self.sock.sendall(data.encode("utf-8"))
        except:
            print("[SERVER] Server has been shut down")

    def request_rematch(self):
        self.send_message(consts.REMATCH_MESSAGE)

    def request_draw(self):
        self.send_message(consts.DRAW_MESSAGE)

    def decline_draw(self):
        self.send_message(consts.DECLINE_MESSAGE)
    
    def declare_surrender(self):
        self.send_message(consts.SURRENDER_MESSAGE)

    def send(self, data: tuple[int]):
        try:
            mail = "00000000"
            mail = (mail[ : consts.TRANSMISSION_DATA_SIZE//2 - len(str(data[0]))] + str(data[0]) + 
                            mail[consts.TRANSMISSION_DATA_SIZE//2 : consts.TRANSMISSION_DATA_SIZE - len(str(data[1]))] + str(data[1]))
            self.sock.sendall(str.encode(mail))
        except:
            print("[SERVER] Server has been shut down")

    def receive(self):
        #Wait for incoming data from server
        #.decode is used to turn the message in bytes to a string
        while self.signal:
            try:
                data = self.sock.recv(consts.TRANSMISSION_DATA_SIZE).decode("utf-8")
                print("[OPPONENT] " + data)

                if data == consts.DISCONNECT_MESSAGE:
                    print("[OPPONENT] Opponent has disconnected")
                    self.data = consts.DISCONNECT_MESSAGE
                    self.signal = False
                elif data == consts.REMATCH_MESSAGE:
                    self.color = "white" if self.color == "black" else "black"
                    self.data = data
                elif data == consts.DRAW_MESSAGE or data == consts.DECLINE_MESSAGE or data == consts.SURRENDER_MESSAGE:
                    self.data = data
                elif not self.color:
                    self.color = "white" if data[0] == "w" else "black"
                elif not self.ready:
                    self.ready = True
                    self.data = data
                else:
                    self.data = (int(data[:4]), int(data[4:8]))

            except:
                self.signal = False
                self.disconnect()
        print("[CLIENT] You have been disconnected successfully")

def main():
    #Create client object
    c = Client()
    c.connect()

    #Send data to server
    #str.encode is used to turn the string message into bytes so it can be sent across the network
    while True:
        message = input()
        if message == consts.DISCONNECT_MESSAGE:
            break
        elif message == consts.REMATCH_MESSAGE:
            c.send(message)
        elif message == consts.RECONNECT_MESSAGE:
            c.connect()
        elif '.' in message:
            message = tuple(map(int, message.split(".")))
            c.send(message)
        else:
            print("[CLIENT] Invalid message format")

    c.disconnect()


  
if __name__ == "__main__":
    main()