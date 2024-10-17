# Client to implement a simple program that will carry out an exchange of
# messages that contains elements of a zero knowledge
# proof. The client sends a hello message to the server. The server responds
# with a message containing a generator, a prime, some public information, and
# a "commitment" message. The client will respond with a challenge message that
# contains an integer. The server transforms that received integer and then
# sends a response message to the client. The client checks that this
# transformed integer shows that the server knows the secret (without the
# secret being revealed).

# Author: fokumdt
# Last modified: 2024-10-14
#!/usr/bin/python3

import socket
from socket import AF_INET, SOCK_STREAM
import sys
from random import SystemRandom
from NumTheory import NumTheory
from datetime import datetime 
import time as t
from random import randint

def serverHello():
  """Generates server hello message"""
  status = "100 Hello"
  return status

def AllGood():
  """Generates 220 Verified"""
  status = "220 OK"
  return status

def ErrorCondition():
  """Generates 400 Error"""
  status = "400 Error"
  return status

def UnexpectedError():
  """Generates 500 Error"""
  status = "500 Error"
  return status

def ChallengeMsg(c):
  """Generates 111 Challenge """
  status = "111 Challenge " + str(c)
  return status

states=dict() 
# s     = socket
# msg   = message being processed
# state = dictionary containing state variables
def processMsgs(s, msg, state):
  t.sleep(1)
  """This function processes messages that are read through the socket. It
     returns a status, which is an integer indicating whether the operation
     was successful."""

  if msg.startswith("105 Generator + Commitment"):
    print(f"{msg} : {datetime.now()}")
    state['expecting'] = "112 Response"
    #send a message to the client
    print(f"The value of p in the the 105 Generated string is: {msg.split(',')[-3]}")
    # this was 
    c = randint(0, int(msg.split(",")[-3]))
    print(f"Sending the vlaue of c: {c}")
    response = ChallengeMsg(c)
    s.send((response).encode())

    state['y'] = int(msg.split(",")[-1])
    state['t'] = int(msg.split(",")[-2])
    state['p'] = int(msg.split(",")[-3])
    state['g'] = int(msg.split(",")[-4][-1])
    state['c'] = c
    states=state

    return 1
  elif msg.startswith("112 Response"):
    print(f"{msg} : {datetime.now()}")
    state['expecting'] = "done"
    #send a message to the client
    
    z = int(msg.split(" ")[-1])

    compare1 = (state['g']**z)%state['p']
    compare2 = (state['t']*state['y']**state['c'])%state['p']
    states=state

    y = state['y']
    print(f"The value of compare1 is: {compare1} and the value of compare2 is: {compare2} ")
    if compare1 == compare2:
      s.send((AllGood()).encode())
      return 0
    else:
      s.send((ErrorCondition()).encode())
      return 0
  else:
    s.send((UnexpectedError()).encode())
    return 0
  pass

def main():
  """Driver function for the project"""
  args = sys.argv
  if len(args) != 3:
    print("Please supply a server address and port.")
    sys.exit()
  serverHost = str(args[1])  #The remote host
  serverPort = int(args[2])  #The port used by the server

  print(f"Client of ___({serverHost}:{serverPort})___") ## added
  print("""
  The purpose of this program is to collect two prime numbers from the client, and then
  send them to the server. The server will compute their LCM and send it back to the
  client. If the server-computed LCM matches the locally computed LCM, the
  clientsends the server a 200 OK status code. Otherwise it sends a 400 error status code,
  and then closes the socket to the server.
  """) 
  #Add code to initialize the socket
  client_socket = socket.socket(AF_INET, SOCK_STREAM)
  client_socket.connect((serverHost, serverPort))

  if client_socket:
    print("The connectionto the server has been established. Timestamp: ",datetime.now().strftime("%H:%M:%S"))

  msg = serverHello()

  #Add code to send data into the socket

  client_socket.send(msg.encode())

  while True:
    msg = client_socket.recv(1024).decode()
    #Handle the data that is read through the socket by using processMsgs(s, msg, state)
    if not processMsgs(client_socket, msg, state=states):
      break
  

  #Close the socket
  client_socket.close()
if __name__ == "__main__":
    main()
  