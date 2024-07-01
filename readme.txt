A continuación se definen algunos de los puertos asignados a cada operación:
En clientes:
    Los puertos se asignan arbitrariamente al crear el socket para conectar con el servidor
En servidor de aplicación:
    Puerto 7900 - Se usa para interactuar con los clientes  
                    Se asignan los puertos secuencialmente (7900, 7901, ...)
    Puerto 8000 - Se usa para interactura con el servidor de tiempo
                    Se asignan los Se asignan los puertos secuencialmente (8000, 8001, ...)
    Puerto 17000 - Puerto donde se encuentra el servidor de Pyro para llamadas a procedimientos remotos
En servidor de tiempo:
    Puerto 9000 - Se usa para interactuar con los servidores y ajustar sus relojes