import socket, pickle, time
from random import randrange
"""
response codes
    0 - waiting game start
    1 - player 1 wins
    2 - player 2 wins
    3 - draft
   10 - 2 players online -> Game should start
  200 - move ok
"""
# global game variables
connections = []
players = 0
firstPlayer = randrange(2) + 1 # 1 or 2
player1Points = 0
player2Points = 0

#global connection variables
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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

def handleGame(connection1, connection2):
  global player1Points, player2Points

  response1 = {}
  response2 = {}

  response1["code"] = 10
  response2["code"] = 10

  response1["firstPlayer"] = firstPlayer
  response2["firstPlayer"] = firstPlayer

  response1["id"] = 1
  response2["id"] = 2

  connection1.send(pickle.dumps(response1))
  connection2.send(pickle.dumps(response2))

  handleRounds(connection1, connection2)

def handleRounds(connection1, connection2):
  global player1Points, player2Points
  while True:
    Movement = pickle.loads(connection1.recv(4096))
    print(Movement)
    if not xList.__contains__(Movement["position"]) and not circleList.__contains__(Movement["position"]):
      if Movement["player"] == 1:
        xList.append(Movement["position"])
      else:
        circleList.append(Movement["position"])

    shifts.append((xList, circleList))

    if player1wins():
      player1Points = player1Points + 1
      print('Player 1 wins!')
      handleResult(connection1, connection2, 1) # 1 = player 1 wins code
      newRound()

    elif player2wins():
      player2Points = player2Points + 1
      print('Player 2 wins!')
      handleResult(connection1, connection2, 2) # 2 = player 2 wins code
      newRound()

    elif draft():
      print("Draft!")
      handleResult(connection1, connection2, 3) # 3 = draft code
      newRound()
    
    else:
      response = {}
      response["code"] = 200
      
      if Movement["player"] == 1: response["player"] = 2
      else: response["player"]: 1

      connection1.send(pickle.dumps(response))
      connection2.send(pickle.dumps(response))

def handleResult(connection1, connection2, code):
  response = {}
  response["code"] = code
  response["p1Points"] = player1Points
  response["p2Points"] = player2Points
  connection1.send(pickle.dumps(response))
  connection2.send(pickle.dumps(response))

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

def newRound():
  xList.clear()
  circleList.clear()
  shifts.clear()

while True:
  if players == 0:
    clientsocket1, addr1 = serversocket.accept()
    players = players + 1
    print("[-] New connection\n[-] {} player online.".format(players))
    response = {}
    response["code"] = 0
    clientsocket1.send(pickle.dumps(response))

  if players == 1:
    clientsocket2, addr2 = serversocket.accept()
    players = players + 1 
    response["code"] = 0
    clientsocket2.send(pickle.dumps(response))
    print("[-] New connection\n[-] {} players online.".format(players))
    time.sleep(2)
    # 2 Players online
    handleGame(clientsocket1, clientsocket2)

clientsocket1.close()
clientsocket2.close()
