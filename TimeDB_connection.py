import mysql.connector
import Pyro4    
from datetime import date, time

class TimeDB_Connection():
    nextNode = 0
    nextHourNode = 0
    nextHour = 0

    def __init__(self):
        self.openConnection()

        nextNode_query = "SELECT id FROM equipo ORDER BY id DESC LIMIT 1"
        self.cursor.execute(nextNode_query)
        response = self.cursor.fetchall()
        if(len(response) == 0):
            self.nextNode += 1
        else:
            self.nextNode = response[0][0] + 1
        
        nextHourNode_query = "SELECT id FROM hora_equipo ORDER BY id DESC LIMIT 1"
        self.cursor.execute(nextHourNode_query)
        response = self.cursor.fetchall()
        if(len(response) == 0):
            self.nextHourNode += 1
        else:
            self.nextHourNode = response[0][0] + 1

        nextHour_query = "SELECT id FROM hora_central ORDER BY id DESC LIMIT 1"
        self.cursor.execute(nextHour_query)
        response = self.cursor.fetchall()
        if(len(response) == 0):
            self.nextHour += 1
        else:
            self.nextHour = response[0][0] + 1

    def openConnection(self):
        self.db = mysql.connector.connect(
            host = "localhost", 
            database = "tiempo_servidores", 
            user = "root", 
            password = "")
        self.cursor = self.db.cursor()

    def closeConnection(self):
        self.cursor.close()
        self.db.close()

    def setServerHour(self, time, adjust_time):
        #Inserting new record
        setNode_query = "INSERT INTO hora_central VALUES(%s, %s, %s)"
        node_tuple = (self.nextHour, time, adjust_time)
        self.cursor.execute(setNode_query, node_tuple)
        self.db.commit()
        self.nextNode += 1
        

    def setNodeHour(self, userIP, time, adjust_time, adjust):
        #Getting node
        nodeId_query = "SELECT id from equipo where ip=%s"
        self.cursor.execute(nodeId_query, (userIP[0], ))
        nodeId = self.cursor.fetchall()

        #Insert next hour adjust record
        setNodeHour_query = "INSERT INTO hora_equipo VALUES(%s, %s, %s, %s, %s, %s)"
        node_hour_tuple = (self.nextHourNode, self.nextHour, nodeId[0][0], time, adjust_time, adjust)
        self.cursor.execute(setNodeHour_query, node_hour_tuple)
        self.db.commit()
        self.nextHourNode += 1

    def nodeExists(self, userIP):
        #Verifies if the user already exists. If it doesn't, creates it 
        nodeExists_query = "SELECT count(*) from equipo where ip=%s"
        self.cursor.execute(nodeExists_query, (userIP[0], ))
        nodeExists = self.cursor.fetchall()
        print(f"User exists: {nodeExists[0][0]}")
        if(nodeExists[0][0] == 0):
            setNode_query = "INSERT INTO equipo(id, ip, nombre) VALUES(%s, %s, %s)"
            print(self.nodeExists)
            node_tuple = (self.nextNode, userIP[0], userIP[1])
            self.cursor.execute(setNode_query, node_tuple)
            self.db.commit()
            self.nextNode += 1
        return nodeExists[0][0]