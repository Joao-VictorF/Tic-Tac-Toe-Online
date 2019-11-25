import socket, pickle, queue, threading
from random import randrange
"""
response codes
  0 - move ok
  1 - player 1 wins
  2 - player 2 wins
  3 - draft
"""

# global game variables
connections = []
players = 0
firstPlayer = randrange(2) + 1
player1Points = 0
player2Points = 0

#global connection variables
  # create server socket object
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  # get local machine name
host = socket.gethostname()
port = 3330

# bind to port
serversocket.bind((host, port))
serversocket.listen(100)

# dinamyc lists
xList = []
circleList = []
shifts = []

# win conditions
rows = [ 
    # Vertical lines 
    ((50, 50),  (50, 270),  (50, 470)),  # 1 4 7
    ((265, 50), (265, 270), (265, 470)), # 2 5 8
    ((470, 50), (470, 270), (470, 470)), # 3 6 9

    # Horizontal lines
    ((50, 50),  (265, 50),  (470, 50)),  # 1 2 3
    ((50, 270), (265, 270), (470, 270)), # 4 5 6
    ((50, 470), (265, 470), (470, 470)), # 7 8 9

    # Diagonal lines
    ((50, 50),  (265, 270), (470, 470)), # 1 5 9
    ((470, 50), (265, 270), (50, 470)),  # 3 5 7
]

print("[-] Server socket started!\n")

def client_thread(conn1, conn2):
  response = {}
  response["code"] = 9
  response["firstPlayer"] = firstPlayer
  conn1.send(pickle.dumps(response))
  conn2.send(pickle.dumps(response))

  global player1Points, player2Points
  while True:
    data1 = pickle.loads(conn1.recv(1024))
    data2 = pickle.loads(conn2.recv(1024))

    if data1:
      if not xList.__contains__(data1["position"]) and not circleList.__contains__(data1["position"]):
        if data1["player"] == 1:
          xList.append(data1["position"])
        else:
          circleList.append(data1["position"])
      
        shifts.append((xList, circleList))

        if player1wins():
          player1Points = player1Points + 1
          print('Player 1 wins!')
          newRound(conn1, conn2, 1)

        if player2wins():
          player2Points = player2Points + 1
          print('Player 2 wins!')
          newRound(conn1, conn2, 2)

        if draft():
          print("Draft!")
          newRound(conn1, conn2, 3)
    
    if data2:
      if not xList.__contains__(data2["position"]) and not circleList.__contains__(data2["position"]):
        if data2["player"] == 1:
          xList.append(data2["position"])
        else:
          circleList.append(data2["position"])
      
        shifts.append((xList, circleList))

        if player1wins():
          player1Points = player1Points + 1
          print('Player 1 wins!')
          newRound(conn1, conn2, 1)

        if player2wins():
          player2Points = player2Points + 1
          print('Player 2 wins!')
          newRound(conn1, conn2, 2)

        if draft():
          print("Draft!")
          newRound(conn1, conn2, 3)
    
    response = {}
    response["code"] = 0
    conn1.send(pickle.dumps(response))
    conn2.send(pickle.dumps(response))

  conn1.close()
  conn2.close()

def player1wins():
  for row in rows:
    if all(xList.__contains__(row[i]) for i in range(3)):
      return True

def player2wins():
  for row in rows:
    if all(circleList.__contains__(row[i]) for i in range(3)):
      return True

def draft():
  if shifts.__len__() == 9:
    return True

def newRound(conn1, conn2, code):
  xList.clear()
  circleList.clear()
  shifts.clear()

  response = {}
  response["code"] = code
  conn1.send(pickle.dumps(response))
  conn2.send(pickle.dumps(response))

while True:
  if players == 0:
    # estabilish a connection
    clientsocket1, addr1 = serversocket.accept()
    players = players + 1
    print("[-] New connection from {}\n[-] {} player online.".format( clientsocket1.getsockname(), players))
    response = {}
    response["code"] = 10
    clientsocket1.send(pickle.dumps(response))

  if players == 1:
    clientsocket2, addr2 = serversocket.accept()
    players = players + 1
    print("[-] New connection from {}\n[-] {} players online.".format( clientsocket2.getsockname(), players))

  if players == 2:
    # threading._start_new_thread(client_thread, (clientsocket1, clientsocket2,))
    client_thread(clientsocket1, clientsocket2)


clientsocket1.close()
clientsocket2.close()
