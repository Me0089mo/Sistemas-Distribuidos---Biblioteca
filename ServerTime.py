import threading
import socket
import time as timesl
import tkinter as tk
import pickle
import sys
sys.path.append(".")
from TimeDB_connection import TimeDB_Connection
from Clock import Clock
from datetime import time, datetime, timedelta, date

class ServerTime(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.serversAddress = []
        self.timeDB = TimeDB_Connection()
        self.createInterface()
        #Thread for running server clock
        self.clock = Clock() 
        self.lock = threading.Lock()
        self.t0 = threading.Thread(target=self.clock.startClock, args=(self.lock, ))
        self.t0.start()
        intitalHour = datetime.combine(date.today(), self.clock.returnHourTime())
        self.timeDB.setServerHour(intitalHour, intitalHour)
        
        #Thread showing time
        self.t1 = threading.Thread(target=self.refreshInterface)
        self.t1.start()

        self.t2 = threading.Thread(target=self.setInitialHour)
        self.t2.start()

        self.t3 = threading.Thread(target=self.alwaysRunning)
        self.t3.start()
        #self.setInitialHour()
        
        #self.alwaysRunning()

    def setInitialHour(self):
        receiveSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        receiveSocket.bind(('10.0.0.13', 9000))
        clients = 0
        while clients < 2:
            clientSock = receiveSocket.recvfrom(1024)
            if clientSock[0]:
                #Register node
                self.timeDB.nodeExists(clientSock[1])
                #Send initial hour to application server
                hour = self.clock.returnHour()
                receiveSocket.sendto(hour.encode(), clientSock[1])
                print(clientSock[1])
                print(clientSock[1][0])
                modSock = (clientSock[1][0], 8000)
                print(modSock)
                self.serversAddress.append(modSock)
                clients += 1

    def createInterface(self):
        #Clock
        self.title = tk.Label(self.master, text = "Time Server", font = ("Times", 18))
        self.title.place(x = 35, y = 20)
        self.clock_hour_str = tk.StringVar()
        self.clock_hour = tk.Label(self.master, textvariable = self.clock_hour_str, font = ("Times", 18))
        self.clock_hour.place(x = 40, y = 70)
    
    def refreshInterface(self):
        while(True):
            self.clock_hour_str.set(self.clock.returnHour())
            timesl.sleep(0.2)
    
    def alwaysRunning(self):
        while True:
            timesl.sleep(10)
            print("Requesting times")
            #Thread to adjust servers hours
            if len(self.serversAddress) >= 1:
                self.adjustHours(self.serversAddress[0])
            if len(self.serversAddress) == 2:
                self.adjustHours(self.serversAddress[1])

    def adjustHours(self, serverAddress):
        adjustSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #Receving server app time and sending correct time
        adjustSocket.sendto("Send hour".encode(), serverAddress)
        timeSer, serverNode = adjustSocket.recvfrom(1024)
        adjustSocket.sendto(pickle.dumps(self.clock.returnHourTime()), serverAddress)
        timeSer2, serverNode = adjustSocket.recvfrom(1024)
        if timeSer and timeSer2:
            final = pickle.loads(timeSer2)
            print(f'{final["hour"]}, {final["adjust"]}')
            aux = final["adjust"]
            adjust = datetime.combine(date.today(), time(0, 0, 0))+aux
            self.timeDB.setNodeHour(serverNode, pickle.loads(timeSer), final["hour"], adjust.microsecond)

main_screen = tk.Tk()
main_screen.geometry("200x120")
server = ServerTime(master = main_screen)
server.mainloop()

#if __name__ == "__main__":
#    main()