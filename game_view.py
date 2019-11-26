import pygame, socket, pickle, time
from random import randrange

# starting the pygame library and variables
pygame.init()
pygame.display.set_caption('Jogo da Velha Online')
window = pygame.display.set_mode((700, 700), 0, 32)
gameFont = pygame.font.SysFont('Calibri', 32)

# global settings and variables
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
Player = 0
PlayerID = 0
Playing = False
player1Points = 0
player2Points = 0
connected = False

# components images
table = pygame.image.load('images/table.png').convert_alpha()
x = pygame.image.load('images/x.png').convert_alpha()
circle = pygame.image.load('images/circle.png').convert_alpha()
sleep = pygame.image.load('images/sleep.jpg').convert_alpha()


# transparent components
transparentX = x.copy()
transparentX.fill((255, 255, 255, 128), None, pygame.BLEND_RGBA_MULT)

transparentCircle = circle.copy()
transparentCircle.fill((255, 255, 255, 128), None, pygame.BLEND_RGBA_MULT)

# clickable areas
area = pygame.Surface((200, 200))

areas = [
  (area, (50, 50)),  (area, (265, 50)),  (area, (470, 50)),  # 1 2 3
  (area, (50, 270)), (area, (265, 270)), (area, (470, 270)), # 4 5 6
  (area, (50, 470)), (area, (265, 470)), (area, (470, 470)), # 7 8 9
]

# dinamyc lists
xList = []
circleList = []

def drawComponents():
  global Player
  window.fill((255, 255, 255))
  window.blit(table, (50, 50))

  points1 = 'Jogador X = {}'.format(player1Points)
  points2 = 'Jogador O = {}'.format(player2Points)

  text1 = gameFont.render(points1, True, (0, 0, 0))
  text2 = gameFont.render(points2, True, (0, 0, 0))

  window.blit(text1, (20, 10))
  window.blit(text2, (500, 10))

  for area in areas:
    if area[0].get_rect(topleft=area[1]).collidepoint(pygame.mouse.get_pos()):
      if Player == 1 and  PlayerID == 1:
        window.blit(transparentX, area[1])
      elif Player == 2 and  PlayerID == 2:
        window.blit(transparentCircle, area[1])
      else:
        window.blit(sleep, area[1])

  for position in xList:
    window.blit(x, position)

  for position in circleList:
    window.blit(circle, position)

def display():
  pygame.display.update()

def update():
  global Player, player1Points, player2Points

  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      pygame.quit()

    if Playing:
      if event.type == pygame.MOUSEBUTTONDOWN:
        for area in areas:
          if area[0].get_rect(topleft=area[1]).collidepoint(pygame.mouse.get_pos()):
            if not xList.__contains__(area[1]) and not circleList.__contains__(area[1]):
              if Player == 1 and PlayerID == 1:
                sendPlay(area[1], 1)
                
              elif Player == 2 and PlayerID == 2:
                sendPlay(area[1], 2)

def player1wins():
  for row in rows:
    if all(xList.__contains__(row[i]) for i in range(3)):
      return True

def player2wins():
  for row in rows:
    if all(circleList.__contains__(row[i]) for i in range(3)):
      return True

def newRound():
  xList.clear()
  circleList.clear()

def sendPlay(position, player):
  jogada = {}
  jogada["player"] = player
  jogada["position"] = position

  clientSocket.send(pickle.dumps(jogada))
  handleResponse(pickle.loads(clientSocket.recv(1096)), position, player)

def handleResponse(data, pos, player):
  global player1Points, player2Points, xList, circleList

  if data["code"] == 200:
    if player == 1:
      xList.append(pos)
      Player = data["player"]
    else:
      circleList.append(pos)
      Player = data["player"]

  elif data["code"] == 1:
    player1Points = data["p1Points"]
    player2Points = data["p2Points"]
    newRound()

  elif data["code"] == 2:
    player1Points = data["p1Points"]
    player2Points = data["p2Points"]
    newRound()

  elif data["code"] == 3:
    player1Points = data["p1Points"]
    player2Points = data["p2Points"]
    newRound()

def serverConnection():
  global Player, PlayerID, Playing
  host = socket.gethostname()
  port = 3330
  clientSocket.connect((host, port))
  data = pickle.loads(clientSocket.recv(4096))  

  data2 = pickle.loads(clientSocket.recv(4096))

  Playing = True
  PlayerID = data2["id"]
  Player = data2["firstPlayer"]
  print("Player {}".format(PlayerID))

while True:
  if not connected:
    serverConnection()
    connected = True
  update()
  drawComponents()
  display()