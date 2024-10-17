# Server to implement a simple program that will carry out an exchange of
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
from random import SystemRandom, randint
from NumTheory import NumTheory
from datetime import datetime 
import time as t
"""
Your server will create a string containing its name (e.g., “Server of Joan A. Smith”). On start-up, the server
will prompt the user for a prime number, 𝑝, of the form 𝑝 = 2𝑞 + 1, where 𝑞 is prime. The user will also
be prompted for a valid generator 𝑔. The server will also generate a random number, 𝑥, that is between
1 and p"""

def primeValidation(q):
  # base cases
  if q == 2 or q == 3 or q == 5 or q == 7 or q == 11:
    return True
  
  if q<=1 or q%2==0 or q%3==0 or q%5==0 or q%7==0 or q%11==0:
    return False
  #code to validate the prime number 

  for i in range(2,q):
    if q%i == 0:
      return False
  return True


#inputPrime(q)
  ##The prime number, 
  # 𝑝, must be of the form 2𝑞 + 1, where 
  # 𝑞 is another prime, and 𝑞 divides 𝑝 − 1.

def inputPrime(q):
  #added 
  ##primeInputisValidation take a prime number and returns true if the result of 2 
  # multiplied by that prime number plus 1 is a prime number and  𝑞 is another prime, and 𝑞 divides 𝑝 − 1
  if primeValidation(q):
    p = 2*q + 1
    return primeValidation(p) and (p-1)%q == 0
  else:
    return False



def PrimeCollect():
  """Accepts a prime number to send to the client"""
  primeNbr = input("Enter a prime number between 127 and 7919: ")
  return primeNbr

def GeneratorCollect():
  """Accepts a generator for the prime"""
  generator = input("Enter a generator for the prime number: ")
  return generator


def clientHello(g, p, x, r):
  """Generates an acknowledgement for the client heGeneratoressage"""
  msg = "105 Generator + Commitment "+ str(g) + ", " + str(p) + ", "+ str(NumTheory.expMod(g,r,p)) + ", " + str(NumTheory.expMod(g,x,p))
  return msg

# r is the nonce chosen by the server
# x is the server's secret integer
# c is the client's challenge integer
def genChallengeResponse(r, x, c):
  """Generates the 107 LCM string"""
  z = r + c*x
  msg = "112 Response " + str(z)
  return msg

states = dict()

#s      = socket
#msg    = message being processed
#state  = dictionary containing state variables
def processMsgs(s, msg, state):
  """This function processes messages that are read through the socket. 
  It returns a status, which is an integer indicating whether the operation was successful."""
  #handle the state when the '100 Hello' message is received
  t.sleep(1)
  if msg.startswith("100 Hello"):
    print(f"{msg} : {datetime.now().strftime("%H:%M:%S")}")
    state['expecting'] = "111 Challenge"
    #send a message to the client
    
    response = clientHello(state['g'], state['p'], state['x'], state['r'])
    s.send(response.encode())
    states=state
    return 1
  elif msg.startswith(state['expecting']):
    print(f"{msg} : {datetime.now().strftime("%H:%M:%S")}")
    state['expecting'] = "Verified"
    state['c'] = int(msg.split(" ")[-1])
    #send a message to the client
    response = genChallengeResponse(state['r'], state['x'], state['c'])
    s.send(response.encode())
    states=state
    return 1
  elif msg.startswith("220") or msg.startswith("500") or msg.startswith("400"):
    print(f"{msg} : {datetime.now().strftime("%H:%M:%S")}")
    state['expecting'] = "done"
    states = state
    return 0
  else:
    return 0

  pass


#p is the prime number
#g is the generator
#returns true if g creates an list using g**k % p such that the list is equal to [1,2,3,...,p-1] or false otherwise
def isGenerator(p,g):
    between_prime = sorted([i for i in range(1,p)])
    actual_prime = []
    for k in range(1,p):
        check = (g**k) % p
        actual_prime.append(check) 
    actual_prime = sorted(actual_prime)
    return actual_prime == between_prime

def main():
  
  """Driver function for the server."""
  args = sys.argv

  if len(args) != 2:
    print ("Please supply a server port.")
    sys.exit()
  
  HOST = ''              #Symbolic name meaning all available interfaces
  PORT = int(args[1])    #The port on which the server is listening.


  if (PORT < 1023 or PORT > 65535):
    print("Invalid port specified.")
    sys.exit()

  print("Server of _____")


  with socket.socket(AF_INET, SOCK_STREAM) as s:
    print("Enter a prime number 'q' such that '2*q + 1':: ",end="")
    q = int(PrimeCollect())
    while inputPrime(q) == False:
      print("Invalid Entry. Enter a prime 'q' such that '2*q + 1': ")
      q = int(PrimeCollect())

    g = int(GeneratorCollect())
    while isGenerator(q,g) == False:
      print("Invalid Entry. Enter a generator 'g' such that 'g**k % q' = 1: ",end="")
      g = int(GeneratorCollect())
    
    p = 2*q + 1
    x = randint(1,p)
    r = randint(1,p-1)
    print(f"The secret integer 'x' is {x}")

    # Bind socket
    # listen 
    s.bind((HOST, PORT)) ##aded 
    s.listen(1) #added

    conn, addr = s.accept() ##added # accept connections using socket
    
    with conn:
      print("Connected from: ", addr)
      #Process messages received from socket using 
      
      states = {"expecting": "100 Hello", "g": g, "p": p, "x": x, "r": r} 
      while True:
        msg = conn.recv(1024).decode()
        if not processMsgs(conn, msg, state = states):
          break
      conn.close()
  
if __name__ == "__main__":
    main()

