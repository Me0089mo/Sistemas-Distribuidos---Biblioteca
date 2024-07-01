import sys
import Pyro4

queries = Pyro4.Proxy("PYRO:biblioteca.queries@localhost:57607")
queries.setQuery("INSERT into usuario values()")