import tkinter as tk
import threading
import socket
import time as timesl
import random
import io
import numpy
import pickle
import Pyro4
import sys
sys.path.append(".")
from Clock import Clock
from BooksDB_Connection import BooksDB_Connection
from functools import partial
from PIL import Image, ImageTk
from datetime import time,  datetime, timedelta, date
from timeit import default_timer as timer 

class Server(tk.Frame):
    bookImage = None
    bookName = ""
    assignedBooks = numpy.zeros(15)
    sincQueries = Pyro4.Proxy("PYRO:biblioteca.queries@10.0.0.13:17000")
    
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.protocol("WM_DELETE_WINDOW", self.onClosingWindow)
        self.createInterface()
        
        self.server = 1
        self.clientsAddress = []
        self.bookDB = BooksDB_Connection()

        #Thread for running server clock
        self.clock = Clock(self.receiveInitialHour()) 
        self.lock = threading.Lock()
        self.t0 = threading.Thread(target=self.clock.startClock, args=(self.lock, ))
        self.t0.start()

        #Thread for synchronizing DB
        self.t3 = threading.Thread(target=self.syncDownloadDB)
        self.t3.start()
        timesl.sleep(1)

        #Thread to listen client requests
        self.t1 = threading.Thread(target=self.reciveRequests)
        self.t1.start()

        #Thread to adjust clock
        self.t2 = threading.Thread(target=self.adjustHour)
        self.t2.start()

        #Thread to refresh the interface
        self.t4 = threading.Thread(target=self.refreshInterface)
        self.t4.start()

    def createInterface(self):
        #Canvas
        self.canvas = tk.Canvas(self.master, width=160, height=250, bg='white')
        self.canvas.place(x = 70, y = 30)
        #Clock
        self.clock1_hour_str = tk.StringVar()
        self.clock1_hour = tk.Label(self.master, textvariable = self.clock1_hour_str, font = ("Times", 18))
        self.clock1_hour.place(x = 95, y = 310)
        #Boton Ajustar
        self.btn_mod_1 = tk.Button(self.master, text = "Ajustar Reloj", command = partial(self.modifyHour))
        self.btn_mod_1.place(x = 105, y = 350, width = 90)
        #Boton Reiniciar Sesion
        self.btn_mod_1 = tk.Button(self.master, text = "Reiniciar Sesion", command = partial(self.forceNewSession))
        self.btn_mod_1.place(x = 105, y = 380, width = 90)
    
    def refreshInterface(self):
        while(True):
            self.clock1_hour_str.set(self.clock.returnHour())
            timesl.sleep(0.2)

    def modifyHour(self, oldHour, newHour):
        if (newHour > oldHour):
            print("Hora nueva mayor")
            self.clock.stopClock()
            self.clock.modifyClock(self.lock, newHour)
        else:
            print("Hora vieja mayor")
            self.clock.stopClock()
            micros = oldHour.microsecond/1000000.0
            timesl.sleep(micros)
            self.clock.modifyClock(self.lock)

    def reciveRequests(self):
        self.startNewSession()
        receiveSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        receiveSocket.bind(('10.0.0.13', 7900))

        while True:
            clientSock = receiveSocket.recvfrom(1024)
            if clientSock[0]:
                #Send hour to client
                hour = self.clock.returnHourTime()
                receiveSocket.sendto(pickle.dumps(hour), clientSock[1])
                #DB Queries
                userExists = self.bookDB.userExists(clientSock[1])
                if userExists != None:
                    self.syncUploadDB(userExists)
                self.requestBook(clientSock[1], hour) 
                #Send book to client
                receiveSocket.sendto(self.bookName.encode(), clientSock[1])

    def startNewSession(self):
        self.bookDB.closeConnection()
        self.assignedBooks = numpy.zeros(15)
        self.bookDB.openConnection()
        result = self.bookDB.newSession(self.clock.returnHourTime(), '10.0.0.13')
        self.syncUploadDB(result)
        self.currentSession = self.bookDB.getCurrentSession('10.0.0.13')

    def forceNewSession(self):
        result = self.bookDB.closeSession(self.clock.returnHourTime(), self.currentSession)
        self.syncUploadDB(result)
        self.startNewSession()

    def requestNewSession(self, userIP):
        reqSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        reqSocket.sendto("Nueva Sesion".encode(), userIP)
        response = reqSocket.recvfrom(1024)
        if response[0]:
            opcion = response[0].decode('utf-8')
            self.closeSession(self.clock.returnHourTime(), self.currentSession)
            if(opcion == "Si"):
                self.startNewSession()
            else: 
                self.bookDB.closeConnection()
    
    def requestBook(self, userIP, time):
        #Selecting book randomly
        random.seed()
        book = random.randint(0,14)
        entregados = numpy.where(self.assignedBooks == 0)
        allData = None
        while allData == None:
            if len(entregados[0]) > 0:
                while self.assignedBooks[book] == 1:
                    book = random.randint(0,14)
            self.assignedBooks[book] = 1
            allData = self.bookDB.getBook(book, userIP, self.currentSession, time)
        bookData = allData["bookInfo"]
        self.bookName = bookData[0][1]
        imageBytes = bookData[0][-1]
        imageGenerated = Image.open(io.BytesIO(imageBytes))
        self.bookImage = ImageTk.PhotoImage(imageGenerated)
        self.canvas.create_image(70, 30, anchor='center' ,image=self.bookImage)
        self.syncUploadDB(allData["query"])

    def adjustHour(self):
        adjustSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        adjustSocket.bind(('10.0.0.13', 8000))
        print("Listening in ")

        while True:
            serverHour, servAdd = adjustSocket.recvfrom(1024)
            if serverHour:
                #Send hour to time server
                hour = self.clock.returnHourTime()
                t0 = timer()
                adjustSocket.sendto(pickle.dumps(hour), servAdd)
                sTime, address = adjustSocket.recvfrom(1024)
                t1 = timer()
                serverTime = pickle.loads(sTime) 
                adjust = timedelta(seconds = t1-t0)/2.0
                aux = datetime.combine(date.today(), serverTime) + adjust
                correction_time = aux.time()
                self.modifyHour(hour, correction_time)
                final = {"hour": correction_time, "adjust": adjust}
                adjustSocket.sendto(pickle.dumps(final), servAdd)

    def onClosingWindow(self):
        result = self.bookDB.closeSession(self.clock.returnHour(), self.currentSession)
        self.syncUploadDB(result)
        self.master.destroy()

    def receiveInitialHour(self):
        receiveSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        receiveSocket.sendto("Initial time".encode(), ('10.0.0.27', 9000))
        initialHour, serverAddr = receiveSocket.recvfrom(1024)
        return initialHour.decode('utf-8')

    def syncDownloadDB(self):
        while(True):
            queries = self.sincQueries.getQuery(self.server)
            for query in queries:
                print("Synchronizing")
                self.bookDB.synchronizeDB(query)
            timesl.sleep(0.5)

    def syncUploadDB(self, newQuery):
        self.sincQueries.setQuery(newQuery, self.server)

class ModifyWindow():
    def __init__(self, parent):
        self.popup_win = tk.Toplevel(parent)
        self.popup_win.geometry("160x120")
        self.createInterface()
        self.newTime = []

    def createInterface(self):
        self.hour = tk.Text(self.popup_win, height = 1, width = 2, font = ("Times", 18))
        self.minute = tk.Text(self.popup_win, height = 1, width = 2, font = ("Times", 18))
        self.second = tk.Text(self.popup_win, height = 1, width = 2, font = ("Times", 18))
        self.hour.place(x = 30, y = 30)
        self.minute.place(x = 65, y = 30)
        self.second.place(x = 100, y = 30)
        self.btn_mod = tk.Button(self.popup_win, text = "Modificar", command = self.setNewHour)
        self.btn_mod.place(x = 50, y = 75)

    def setNewHour(self):
        self.newTime.append(self.hour.get("1.0", "end-1c"))
        self.newTime.append(self.minute.get("1.0", "end-1c"))
        self.newTime.append(self.second.get("1.0", "end-1c"))
        self.popup_win.destroy()
    
    def getNewHour(self):
        return self.newTime
    
main_screen = tk.Tk()
main_screen.geometry("300x400")
server = Server(master = main_screen)
server.mainloop()