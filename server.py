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

def timestamp():
  # t.sleep(1)
  return f">>>  {datetime.now().strftime("%a %H:%M:%S")}\n"

def primeValidation(val):
  """
    primeValidation takes a prime number as input
    
    Parameters:
    val (int): prime number
    
    Returns:
    Boolean: True if val is prime number and False otherwise
  """
  if val < 1:
      return False 
  if val == 2 or val == 3:
      return True
  for i in range(3,val//2+1):
      if val%i==0:
          return False
  return True
      



#inputPrime(q)
  ##The prime number, 
  # 𝑝, must be of the form 2𝑞 + 1, where 
  # 𝑞 is another prime, and 𝑞 divides 𝑝 − 1.

def inputPrime(p):
  #added 
  ##primeInputisValidation take a prime number and returns true if the result of 2 
  # multiplied by that prime number plus 1 is a prime number and  𝑞 is another prime, and 𝑞 divides 𝑝 − 1
  #check if p is and whole number 
  """
  inputPrime takes a prime number as input

  Parameters:
  p (int): prime number

  Returns:
  Boolean: True if p is a prime number and q is another prime where q divides p-1 and q = (p-1)/2. False otherwise"""
  if p < 127 or p > 7919:
      print("Invalid entry. The Prime number must be between 127 and 7919")
      return False
  q = (p-1)/2
  if int(q) == q:
      q = int(q)
      return primeValidation(p) and  primeValidation(q) and (p-1)%q == 0
       
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
  """
  This function processes messages that are read through the socket. 
  It returns a status, which is an integer indicating whether the 
  operation was successful.

  Parameters:
  s (socket)  : socket
  msg (string)   : message being processed
  state (dictionary) : dictionary containing state variables

  Returns:
  status : integer indicating whether the operation was successful
  """
  #handle the state when the '100 Hello' message is received
  # t.sleep(1)
  if msg.startswith("100 Hello"):
    print(f'{msg}  \n{timestamp()}')
        
    #send a message to the client
    response = clientHello(state['g'], state['p'], state['x'], state['r'])
    s.send(response.encode())
    print(f'100 Hello message received. \nserver generates response: {response}')
    print(f"response sent to the client...\n{timestamp()}")

    state['expecting'] = "111 Challenge"
    print(f"server updates its state to expecting '{state['expecting']}' \n{timestamp()}")
    states=state
    return 1
  elif msg.startswith(state['expecting']):
    print(f'{msg} \n{timestamp()}')

    state['c'] = int(msg.split(" ")[-1])
    print(f"server receieves 111 Challenge C from the client, where C = {state['c']} \n{timestamp()}")
    state['expecting'] = "220 500 400"
    
    #send a message to the client
    response = genChallengeResponse(state['r'], state['x'], state['c'])
    s.send(response.encode())
    
    print(f"Server generates '112 Response B' and sends it to the client., where B = {response.split(" ")[-1]} \n{timestamp()}")

    print(f"server awaiting client's status...\n{timestamp()}")
    states=state
    return 1
  elif msg[:3] in state['expecting'].split(" "):
    status_meaning = {"220":"Success, client's commitment matches server's commitment", "400": "Error, client's commitment does not match server's commitment", "500": "Bad request. The server received and unexpected message"}
    print(f'{msg} \n{timestamp()}')

    print(f"server receives 'status {msg[:3]}' from the client. \nInterpretation: {status_meaning[msg[:3]]} \n{timestamp()}")
    state['expecting'] = "done"
    states = state
    return 0
  else:
    return 0

  pass




def isGenerator(g,p):
    """
    Checks whether the given number `g` is a generator for the prime number `p`.

    An integer g is a generator of a prime number, p, if g^k mod p gives all 
    integers between 1 and p - 1 for k between 1 and p - 1, ie 1,2,3,...,p-1

    Parameters:
    g (int): The generator.
    p (int): A prime number.

    Returns:
    bool: True if `g` is a generator of `p`, False otherwise.
    """
    between_prime = sorted([i for i in range(1,p)])
    gernerator_accumulation = []
    for k in range(1,p):
        check = (g**k) % p
        gernerator_accumulation.append(check) 
    gernerator_accumulation = sorted(gernerator_accumulation)
    # print(f"gernerator_accumulation: {gernerator_accumulation}")
    return gernerator_accumulation == between_prime

def main():
  
  """Driver function for the server."""
  args = sys.argv

  if len(args) != 2:
    print ("Please supply a server port.")
    sys.exit()
  
  HOST = '0.0.0.0'              #Symbolic name meaning all available interfaces
  PORT = int(args[1])    #The port on which the server is listening.


  if (PORT < 1023 or PORT > 65535):
    print("Invalid port specified.")
    sys.exit()

  device_name = socket.gethostname()
    
 
  print("Server of",device_name)


  with socket.socket(AF_INET, SOCK_STREAM) as s:
    p = 0
    try:
      p = int(PrimeCollect())
    except ValueError:
      pass

    while inputPrime(p) == False:
      print(f"Enter 'p' such that 'p = 2*q + 1' where'q' is also prime:\n\nRe",end="")
      p = int(PrimeCollect())

    
    
    g = int(GeneratorCollect())
    while isGenerator(g,p) == False:
      print(f"Invalid Entry. Enter a generator 'g' such that 'g**k % p' produces 1,2,3,...,p-1 for k between 1 and p-1.\n{timestamp()}")
      g = int(GeneratorCollect())
    
    if g and p:
      print(f"\nInput stored.The values are: 'g' = {g} and 'p' = {p} \n{timestamp()}")
    x = randint(1,p)
    r = randint(1,p)
    

    print(f"The server has generated the random values 'x' and 'r' such that 1>=x<=p and 1>=r<=p \n  x = {x} \n  r = {r} \n{timestamp()}")

    # Bind socket
    # listen 
    s.bind((HOST, PORT)) ##aded 
    s.listen(1) #added
    print(f"Server listening on port {PORT}...")

    conn, addr = s.accept() ##added # accept connections using socket
    
    client_count = 0
    with conn:
      print(f"Client_{client_count} connected from:", addr)
      print(timestamp())

      #Process messages received from socket using 
      states = {"server": "server", "expecting": "100 Hello", "g": g, "p": p, "x": x, "r": r} 
      while True:
        msg = conn.recv(1024).decode()
        if not processMsgs(conn, msg, state = states):
          break
      conn.close()
  
if __name__ == "__main__":
    main()

