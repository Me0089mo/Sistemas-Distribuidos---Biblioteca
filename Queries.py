from __future__ import print_function
import Pyro4

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class Queries(object):
    def __init__(self):
        self.queriesS1 = []
        self.queriesS2 = []

    def getQuery(self, server):
        newQueries = []
        if server == 1:
            if len(self.queriesS2) > 0:
                newQueries = self.queriesS2.copy()
                self.queriesS2.clear()
        else:
            if len(self.queriesS1) > 0:
                newQueries = self.queriesS1.copy()
                self.queriesS1.clear()
        return newQueries

    def setQuery(self, query, server):
        if server == 1:
            self.queriesS1.append(query)
        else:
            self.queriesS2.append(query)

def main():
    Pyro4.Daemon.serveSimple(
        {Queries: "biblioteca.queries"},
        host="10.0.0.13",
        port=17000,
        ns=False
    )

if __name__ == "__main__":
    print("es main")
    main()
