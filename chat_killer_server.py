#!/usr/bin/env python3
import os, sys, socket, select, signal, atexit

MAXBYTES = 4096


s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
if len(sys.argv) < 2:
    os.write(2,'utilisation : ./chat_killer_server.py PORT'.encode())
    sys.exit(1)

HOST = '127.0.0.1' 
try:
    port = int(sys.argv[1])
except ValueError:
    os.write(2,'veuillez entrer pour port un entier ()>1043 de préférence)...'.encode())
    sys.exit(1)


try: #finir
    s.bind((HOST,port))
    print(f"server {HOST}:{port} created.\n")
except OSError:
    temp = input("[Errno 48] : Veuillez libérer le port via cette commande : `sudo lsof -i :2317` ou choisir un autre port en tapant `1`> ") 
    if temp == '1':
        port = int(input('Nouveau port (>1043)> '))
        s.bind((HOST,port))
        print(f"server {HOST}:{port} created.\n")
    else:
        sys.exit(1)

socketlist= [s,sys.stdin]

class Client():
    def __init__(self,socket,pseudo,cookie=None):
        self.socket = socket
        self.pseudo:str = pseudo
        self.state = 1
        self.cookie = cookie

    def currentState(self)->str:
        if self.state == 0:
            return "DISCONNECTED/CRASHED"
        if self.state == 1:
            return "ALIVE"
        if self.state == 2:
            return "SUSPENDED"
        if self.state == 3:
            return "BANNED/DEAD"
    
def detectPseudo(phrase:str,L:list)->bool:
    pseudo = phrase.split()[0]
    for i in L:
        if i.pseudo == pseudo:
            return True
    return False

def givePseudo(pseudo:str,L:list):
    for i in L:
        if i.pseudo == pseudo:
            return i
    return None

def findPseudo(socket,L:list)->str:
    for i in L:
        if i.socket == socket:
            return i.pseudo
    return None

clients = []

cookies = {}


def handlerSIGINT(sig,_frame):
    kill()

def end(L:list):
    for i in L:
        if i.state == 1 or i.state == 2:
            i.socket.sendall("DEL+".encode())
    

def kill():
    os.write(1,"Vous venez de tuer le serveur.\n".encode())
    end(clients)
    sys.exit(0)

s.listen()
commands = 'Commandes : !start ; !list ; @PSEUDO message ; @PSEUDO1 @PSEUDO2 ... @PSEUDOn message ; @PSEUDO !ban ; @PSEUDO !suspend ; @PSEUDO !forgive\n'
commandesCLIENT= 'Commandes : !list ; @Admin message ; @PSEUDO message ; @PSEUDO1 @PSEUDO2 message ; message vide (ENTER) pour se déconnecter.\n'

if __name__ == '__main__':
    signal.signal(signal.SIGINT,handlerSIGINT)
    os.write(1,commands.encode())
    START=False
    x=0
    
    while len(socketlist)>1:
        x+=2
        (rlist,_,_) = select.select(socketlist,[],[])
        
        for i in rlist:
            if i == s:
                new_cookie = 'C+'+ str(os.getpid()*999+x) 
                if not START:
                    
                    Xfd,(Xaddr,Xport) = s.accept()
                    print("\nconnection from: {}:{} \n".format(Xaddr,Xport))
                    socketlist.append(Xfd) 
                    
                     
                    data = Xfd.recv(MAXBYTES)
                    PSEUDO = False
                    print(data.decode())
                    try:
                        if data.decode()[0:2] != 'C+':
                            print(data.decode())
                            Xfd.sendall("\nServer: Please enter your pseudo in the following format '@pseudo'> \n".encode())

                            while not PSEUDO:
                                data = Xfd.recv(MAXBYTES)
                                
                                temp = data.decode().rstrip(' '+'\n') 
                                if not temp[0] == '@' or temp == '@' or ' ' in temp: 
                                
                                    Xfd.sendall("\nTHE CORRECT FORMAT IS '@pseudo'> ".encode())
                                    
                                elif temp == '@Admin':
                                    Xfd.sendall('\n YOU ARE NOT THE ADMIN... PLEASE CHOOSE ANOTHER PSEUDO >'.encode())
                                elif not detectPseudo(temp, clients):
                                    
                                    os.write(1,(temp +' HAS JUST CONNECTED\n').encode())
                                    pseudo = Client(Xfd,temp,new_cookie)
                                    Xfd.sendall((new_cookie+' ' + temp + ' '+ '\n'+ commandesCLIENT + f'\nServer: Welcome {temp}\n').encode())
                                    clients.append(pseudo)
                                    print(f'{pseudo.cookie=},{pseudo.pseudo=}')
                                    Xfd.sendall(('\nServer: Welcome {}\n'.format(temp)).encode()) 
                                    PSEUDO = True
                                    Xfd.sendall(commandesCLIENT.encode())
                                    
                                else:
                                    Xfd.sendall('\n THIS PSEUDO HAS ALREADY BEEN CHOSEN... PLEASE CHOOSE ANOTHER >'.encode())
                        else:
                            
                                
                                
                            tempcookie = data.decode().rstrip(' '+'\n')
                            print(f'{tempcookie=}')
                            for j in clients:
                                print(j)
                                if j.cookie == tempcookie:
                                    print(j.cookie)
                                    print(j.state)
                                    if j.state == 3:
                                        
                                        Xfd.sendall("231723172317".encode())
                                        socketlist.remove(Xfd)
                                        Xfd.close()
                                        break
                                    if j.state != 3:
                                        PSEUDO = True
                                        j.state = 1
                                        j.socket = Xfd

                                        Xfd.sendall(('\nServer: Welcome back {}\n'.format(temp)).encode())
                                        Xfd.sendall(commandesCLIENT.encode())
                                        break
                            Xfd.sendall("DEL+".encode()) 
                            break
                                    
                            
                    except IndexError:    
                        print("1")
                        Xfd.close()
                        
                        socketlist.remove(Xfd)
                        os.write(2,('{}:{} was shutdown.\n'.format(Xaddr,Xport)).encode())
                        break 
                    except ConnectionResetError:
                        print("2")
                        os.write(2,('{}:{} was shutdown.\n'.format(Xaddr,Xport)).encode())
                        break
                    except OSError:
                        os.write(2,('{}:{} was shutdown.\n'.format(Xaddr,Xport)).encode())

                        break
                         
                else:
                    os.write(1,"THE GAME HAS STARTED. NO NEW CONNECTIONS WILL BE ACCEPTED.\n".encode())
                    Xfd, (t1,t2)= s.accept()
                    Xfd.sendall("THE GAME HAS STARTED. NO NEW CONNECTIONS WILL BE ACCEPTED.\n".encode())
                    os.write(1,('{}:{} was refused.\n'.format(t1,t2).encode()))
                    Xfd.close()
                            
            elif i == sys.stdin:
                line = sys.stdin.readline()
                if len(line) == 0:
                    break

                elif line[0] == '@':
                    if detectPseudo(line,clients): 
                        client = givePseudo(line.split()[0],clients)
                        if client.state == 1 or client.state == 2:
                            if len(line.split()) > 1:
                                if line.split()[1] == '!ban':
                                    os.write(1,f"{client.pseudo} a été banni\n".encode())
                                    try:
                                        client.socket.sendall("231723172317\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nYOU HAVE BEEN BANNED\n".encode())
                                    except OSError:
                                        os.write(1,"Ce joueur n'est pas connecté\n".encode())
                                    for j in clients:
                                        if j.state == 1 or j.state == 2:
                                            j.socket.sendall(f"{client.pseudo} A ETE BANNI\n".encode())
                                    client.state = 3
                                    client.socket.close()
                                    socketlist.remove(client.socket)
                                elif line.split()[1] == "!suspend":
                                    os.write(1,f"{client.pseudo} est suspendu de parler.\n".encode())
                                    try:
                                        client.socket.sendall("2317\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nYOU HAVE BEEN SUSPENDED\n".encode())
                                    except OSError:
                                        os.write(1,"Ce joueur n'est pas connecté\n".encode())
                                    for j in clients: 
                                        if j.state == 1 or j.state == 2:
                                            j.socket.sendall(f"{client.pseudo} HAS BEEN SUSPENDED.\n".encode())
                                    client.state = 2
                                    

                                elif line.split()[1] == "!forgive":
                                    os.write(1,f"{client.pseudo} HAS BEEN FORGIVEN\n".encode())
                                    try:
                                        client.socket.sendall("23172317\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nYOU HAVE BEEN FORGIVEN\n".encode())
                                    except OSError:
                                        os.write(1,"Ce joueur n'est pas connecté\n".encode())
                                    for j in clients: 
                                        if j.state == 1 or j.state == 2:
                                            j.socket.sendall(f"{client.pseudo} HAS BEEN FORGIVEN\n".encode())
                                    client.state = 1
                                else:
                                    line = line.lstrip(client.pseudo) 
                                    client.socket.sendall(('Server to ' + client.pseudo + ':'+ line).encode()) 
                                break 
                            else:
                                os.write(1,"Ecrivez un message, pas que le pseudo...".encode())
                        else:
                            os.write(1,"Ce client n'est pas connecté.\n".encode())
                    else:
                        os.write(2,"Le pseudo choisi n'existe pas.\n".encode())

                elif line == '!list\n':
                    os.write(1,"Liste des joueurs : \n".encode())
                    if len(clients) == 0:
                        os.write(1,"Il n'y a pas encore de joueur connecté.\n".encode())
                    else:
                        for j in clients:
                            os.write(1,(j.pseudo+': '+j.currentState()+"\n").encode())
                
                elif line == "!start\n":
                    os.write(1,"THE GAME HAS STARTED.\n".encode())
                    for j in clients:
                        if j.state == 1 or j.state == 2:
                            j.socket.sendall("THE GAME HAS STARTED.\n".encode())
                    START=True

                else:
                    line = 'Server: '+line
                    for client in clients: 
                        if client.state == 2 or client.state == 1:
                            client.socket.sendall(line.encode())
                        
                    

            else:  
    
                    data = i.recv(MAXBYTES)
                    pseudo = findPseudo(i,clients)
                    client = givePseudo(pseudo,clients)
                
                    if data.decode()=='\n' or len(data)==0 or data.decode()=="": 
                        if findPseudo(i,clients)!=None: 
                            os.write(1,("{} HAS DISCONNECTED\n".format(pseudo)).encode())
                            i.close()   
                            socketlist.remove(i)
                            client.state = 0
                            break
                            
                    elif data.decode().split()[0] == '@Admin':
                        os.write(1,data)
                        i.sendall(f'{pseudo} to @Admin: {data.decode().lstrip("@Admin")}'.encode())

                    elif data.decode() == "!list\n": 
                        i.sendall("Liste des joueurs : \n".encode())
                        for j in clients:
                            i.sendall((j.pseudo+': '+j.currentState()+"\n").encode())
                        
                    

                    elif data.decode()[0] == '@': 
                        data = data.decode()
                        pseudoListe = []
                        if detectPseudo(data,clients):
                            if len(data.rstrip('\n').split())>1:
                                for w in data.split():
                                    if detectPseudo(w,clients):
                                        pseudoListe.append(w)
                                        w = w  
                                        data = data.lstrip(w)
                                        data= data.lstrip(' ') 
                                        print(f"{data=}") 
                                    else: 
                                        break

                                for t in pseudoListe:
                                    destination = givePseudo(t,clients)
                                    if destination.state != 0 and destination.state != 3:
                                        os.write(1,(pseudo + ' to '+ destination.pseudo + ": " + data +"\n").encode())
                                        destination.socket.sendall((pseudo + ' to '+ destination.pseudo + ": " + data+"\n").encode())
                                    else:
                                        i.sendall("Serveur: Ce joueur n'est pas connecté\n".encode())
                            else:
                                i.sendall("Serveur : Ecrivez un message derrière le pseudo..\n")
                        else:
                            i.sendall("Serveur : Ce joueur n'existe pas\n".encode())
                            break
                    else:
                        os.write(1,(f'{pseudo}: {data.decode()}').encode())
                        for j in clients: 
                            if j.state == 1 or j.state == 2:
                                try:
                                    j.socket.sendall((pseudo+ ": "+data.decode()).encode())
                                except TypeError: 
                                    os.write(2,"tu peux pas écrire hihi ".encode())
