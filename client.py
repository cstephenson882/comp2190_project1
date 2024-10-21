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


def timestamp():
  # t.sleep(1)
  return f">>>  {datetime.now().strftime("%a %H:%M:%S")}\n"

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
  # t.sleep(1)
  """This function processes messages that are read through the socket. It
     returns a status, which is an integer indicating whether the operation
     was successful."""
  if not msg:
    print("No message received.  Exiting")
    return 0
  

  if msg.startswith("105 Generator + Commitment"):
    msg_split =  msg[27:].split(",")
  
    state['g'] = int(msg_split[0])
    state['p'] = int(msg_split[1])
    state['t'] = int(msg_split[2])
    state['y'] = int(msg_split[3])
    
    print (f"105 Generator + Commitment {state['g']}, {state['p']}, {state['t']}, {state['y']}")
    print(f"{timestamp()}")
    print(f"response received from the server. 105 Generator + Commitment g={state['g']}, p={state['p']}, t={state['t']}, y=V={state['y']}. \n{timestamp()}") 

   
    state['c'] = randint(0, state['p']-1)
    print(f"Client generates value for 'c' such that 0 <= c < p. \nc = {state['c']} \n{timestamp()}")
    
    
    client_challenge = ChallengeMsg(state['c'] )
    # client_challenge = f"111 Challenge {[i for i in range(1,state['p'])][randint(0,state['p']-1)]}"
    s.send((client_challenge).encode()) 
    print(f"Client sends 'Challenge C' to server as '111 Challenge {state['c']}'. Awaiting response... \n{timestamp()}")

    
    state['expecting'] = "112 Response"  
    print(f"Client updates its state to expecting '112 Response B' \n{timestamp()}") 
  
    states=state
    return 1
  elif msg.startswith("112 Response"):
    print(f"{msg}  \n{timestamp()}")
    print(f"112 Response B received from the server, where B={msg.split(' ')[-1]}. \n{timestamp()}")
    
    #send a message to the client
    z = int(msg.split(" ")[-1])

    print (f"Computed the value for 'z = r + cx'. \nz = {z}.\n{timestamp()}")

    client_calculated_commitment = (state['g']**z)%state['p']
    server_calculated_commitment = (state['t']*state['y']**state['c'])%state['p']
    
    print(f"calculated client commitment given by (t * y^c) mod p. Where, t = {state['t']}, y = {state['y']} and p = {state['p']}. c = {state['c']}. \nclient_calculated_commitment = {client_calculated_commitment}") 
    print(f"calculated server commitment given by (g^z) mod p. Where, g = {state['g']}, z = {z} and p = {state['p']}. \nserver_calculated_commitment = {server_calculated_commitment} \n{timestamp()}")           
    state['expecting'] = "done"
    states=state

    y = state['y']

    if client_calculated_commitment == server_calculated_commitment:
      print(f"Sucess: Computed commitment matches. '{AllGood()}' status sent to server.  \n{timestamp()}")
      s.send((AllGood()).encode())
      return 0
    else:
      print(f"Error: Computed commitment does not match. client_calculated_commitment = {client_calculated_commitment}, server_calculated_commitment = {server_calculated_commitment}. '{ErrorCondition()}' status sent to server.\n{timestamp()}")
      s.send((ErrorCondition()).encode())
      return 0
  else:
    s.send((UnexpectedError()).encode())
    print(f"Unexpected error. '{UnexpectedError()}' status sent to server. \n{timestamp()}")
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

  print(f"Client of Client of {socket.gethostname()}") ## added
  print("""
  The purpose of this program is to collect two prime numbers from the client, and then
  send them to the server. The server will compute their LCM and send it back to the
  client. If the server-computed LCM matches the locally computed LCM, the
  clientsends the server a 200 OK status code. Otherwise it sends a 400 error status code,
  and then closes the socket to the server.
  """) 
  #Add code to initialize the socket
  client_socket = socket.socket(AF_INET, SOCK_STREAM)
  try:
    client_socket.connect((serverHost, serverPort))
  except:
    print(f"Could not connect to the server on port {serverPort}. \n{timestamp()} ")
    sys.exit()

  if client_socket:
    print(f"The connection to the server has been established on port {serverPort}. \n{timestamp()} ")

  #Add code to send data into the socket
  msg = serverHello()
  client_socket.send(msg.encode())
  print(f"client sends 'hello message' to the server. Awaiting response... \n{timestamp()} ")

  while True:
    msg = client_socket.recv(1024).decode()
    #Handle the data that is read through the socket by using processMsgs(s, msg, state)
    if not processMsgs(client_socket, msg, state=states):
      break
  

  #Close the socket
  client_socket.close()
if __name__ == "__main__":
    main()
  