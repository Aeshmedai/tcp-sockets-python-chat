#!/usr/bin/env python3
import os, socket, sys, select, atexit, signal

gpid = os.fork()
if gpid==0:
   MAXBYTES = 4096

   if len(sys.argv) != 3:
       print('Usage:', sys.argv[0], 'hote port')
       sys.exit(1)

   HOST = sys.argv[1]
   PORT = int(sys.argv[2])

   sockaddr = (HOST, PORT)

   try:
        os.mkdir('./tmp/')
   except FileExistsError:
        pass
   cookie = None
   pseudo = None
   for d in os.listdir('./tmp'):
       if os.path.exists(f'./tmp/{d}/cookie'):
           fd = os.open(f'./tmp/{d}/cookie', os.O_RDONLY)
           pseudo = d
           cookie = os.read(fd,MAXBYTES)
           print(f'{cookie.decode()=}')
           print(f'{d=}')
           os.close(fd)
           break



   PATHFIFO= './tmp/killer.fifo'
   PATHLOG = './tmp/killer.log'


   def end(fifo,fifofd,log):
       try:
            os.unlink(fifo)
            os.close(log)
            os.close(fifofd)
       except FileNotFoundError:
            pass
       

   try:
       os.mkfifo(PATHFIFO)
   except FileExistsError:
       try:
           os.remove(PATHFIFO) 
       except PermissionError: 
           pid = os.fork()
           if pid == 0:
               os.execvp('sudo',['sudo','rm',PATHFIFO])
           else:
               os.waitpid(pid,0)

       os.mkfifo(PATHFIFO)



   logfd = os.open(PATHLOG, os.O_CREAT | os.O_WRONLY) #on le crée s'il existe pas déjà 
   fifofd = os.open(PATHFIFO, os.O_RDWR) #obligé d'ouvrir en RDWR pour éviter deadlock



   atexit.register(end,PATHFIFO,fifofd,logfd)

   XTERM = "xterm"
   SAISIE = [XTERM,"-e",f"cat >{PATHFIFO}"]
   AFFICHAGE = [XTERM,"-e","tail", "-f", PATHLOG]


   global pidaffichage, pidsaisie 

   def CHLDAffichage():
       global pidaffichage
       pidaffichage = os.fork()
       if pidaffichage == 0:
               try:
                   os.execvp(XTERM, AFFICHAGE)
               except:

                   os.write(2,"affichage n'a pas marché/télécharger xterm ".encode())
                   sys.exit(1)

   CHLDAffichage()


   def CHLDSaisie():
       global pidsaisie
       pidsaisie = os.fork()
       if pidsaisie == 0: 
           try:
               os.execvp(XTERM, SAISIE)
           except:

               os.write(2,"saisie n'a pas marché/télécharger xterm ".encode())
               sys.exit(1)

   CHLDSaisie()


   s_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

   def kill():
        os.kill(pidaffichage,signal.SIGKILL)
        os.kill(pidaffichage,signal.SIGKILL) 
        os.kill(pidsaisie,signal.SIGKILL)
        try:
            os.unlink(PATHFIFO)
            os.close(logfd)
        except: 
            pass
        s_client.close()
        os.kill(os.getpid(),signal.SIGKILL)

   try:
       s_client.connect(sockaddr)
   except ConnectionRefusedError:
       os.write(2,"Le serveur n'est pas encore lancé...\n".encode())
       kill()
       sys.exit(1)



   socketlist = [s_client,fifofd] 

   global TG
   TG = False 


   def suspend():
       global TG
       TG = True
       os.kill(pidsaisie,signal.SIGSTOP) 
       os.write(logfd,"YOU GOT SUSPENDED (hihi)\n".encode())
       

   def handlerSIGINT(sig,_frame):
       kill()

   def handlerSIGALARM(sig,_frame):
       global TG
       if not TG: 
           pass
       TG = False
    
   def handlerSIGCHLD(sig,_frame):
       global pidaffichage, pidsaisie
       '''ici on cherche à savoir si pid sera égal à celui de la saisie ou de l'affichage
       donc on met -1 pour attendre l'arrêt de l'importe quel enfant et WNOHANG permet de ne pas être bloquant'''
       (pid,_) = os.waitpid(-1,os.WNOHANG) 
       if pid == pidsaisie:
           CHLDSaisie()
       if pid == pidaffichage:
           CHLDAffichage()    
       else:
           pass
           

   def forgive():
       os.kill(pidsaisie,signal.SIGCONT) 
       signal.alarm(1) 


   if cookie != None:
       temp = s_client.sendall(cookie)

   os.write(logfd,"VEUILLEZ ENTRER UNE TOUCHE POUR CONFIRMER VOTRE ENTREE DANS LE SERVEUR.".encode())
   while True: 
       signal.signal(signal.SIGCHLD,handlerSIGCHLD) 
       signal.signal(signal.SIGINT,handlerSIGINT)  
       try:
           (rlist,_,_) = select.select(socketlist,[],[])
           
           for i in rlist:
               
               signal.signal(signal.SIGALRM,handlerSIGALARM)
               
               if TG and i==fifofd:
                   os.read(fifofd,MAXBYTES)

               elif not TG and i==fifofd:
                   line = os.read(fifofd,MAXBYTES) #on lit depuis le descripteur du fifo ouvert en LECTURE
                   if len(line) == 0:
                       s_client.shutdown(socket.SHUT_WR)
                       kill()
                   s_client.sendall(line)
               
                       
               
               elif i==s_client:
                   data = i.recv(MAXBYTES)
                   if data.decode() == "":
                       kill()
                   elif data.decode() == "DEL+":
                       try:
                           os.remove(f'./tmp/{pseudo}/cookie')
                           os.rmdir(f'./tmp/{pseudo}/')
                           os.remove(PATHFIFO)
                           os.remove(PATHLOG) 
                           os.rmdir('./tmp/') 
                       except FileNotFoundError:
                           pass
                       kill()
                   
                   elif data.decode().split()[0][0:2] == 'C+':
                       cookie = data.decode().split()[0]
                       
                       pseudo = data.decode().split()[1]
                       
                       os.mkdir(f'./tmp/{pseudo}')
                       
                       fd = os.open(f'./tmp/{pseudo}/cookie',os.O_WRONLY | os.O_CREAT)
                       
                       os.write(fd,cookie.encode())
                       temp = data.decode().lstrip(str(cookie))
                       temp = temp.lstrip(str(pseudo))
                       
                       
                       os.close(fd)
                       os.write(logfd,temp.encode())
                       

                   
                       
                   elif data.decode() == "THE GAME HAS STARTED. NO NEW CONNECTIONS WILL BE ACCEPTED.\n":
                       
                       kill()
                   elif len(data) == 0 or data.decode() == "": #serveur mort on supprime tout
                       os.remove(f'./tmp/{pseudo}/cookie')
                       os.rmdir(f'./tmp/{pseudo}/')
                       os.remove(PATHFIFO)
                       os.remove(PATHLOG)
                       os.rmdir('./tmp/') 
                       kill()
                       sys.exit(0)
                   elif data.decode().split()[0] == "231723172317": 
                       print('VOUS ETES banni')
                       os.write(logfd, data)
                       kill()
                       os.write(1,"YOU GOT BANNED!".encode())
                       sys.exit(0)
                   elif data.decode().split()[0] == "2317":
                       TG = True
                       os.kill(pidsaisie,signal.SIGSTOP)
                       
                       os.write(logfd, data)
                       break
                   elif data.decode().split()[0] == "23172317":
                       os.kill(pidsaisie,signal.SIGCONT) #ça change rien de recevoir un SIGCONT si on est pas SIGSTOP avant
                       signal.alarm(1) 
                         
                       os.write(logfd, data)
                                   
                   else:
                       os.write(logfd, data)
       except ValueError: #la partie a commencé, ValueError: file descriptor cannot be a negative integer (-1) si le serveur démarre
            os.kill(pidaffichage,signal.SIGKILL)
            os.kill(pidaffichage,signal.SIGKILL) 
            os.kill(pidsaisie,signal.SIGKILL)
            os.write(1,"THE GAME HAS STARTED\n".encode())
            kill()
            sys.exit(0)
       except :
           s_client.sendall("".encode())
           os.remove(PATHFIFO)
           
           
           kill()
           sys.exit(1)
           
       
else:
   sys.exit(0)
