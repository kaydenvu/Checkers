import sys, os

import pygame
from pygame.locals import QUIT, MOUSEBUTTONDOWN, MOUSEMOTION

pygame.init()
screenSize = 600
display = pygame.display.set_mode((screenSize, screenSize), pygame.FULLSCREEN)
pygame.display.set_caption('Checkers')

tileSize = screenSize // 8
pieceSize = tileSize // 2 - 5
board = list()
white = (255, 255, 255)
black = (0, 0, 0)
red = (230, 0, 0)
redPiece = pygame.image.load("Downloads/Checkers/red.png")
redPiece = pygame.transform.scale(redPiece, (tileSize, tileSize))
blackPiece = pygame.image.load("Downloads/Checkers/black.png")
blackPiece = pygame.transform.scale(blackPiece, (tileSize, tileSize))
redCrown = pygame.image.load("Downloads/Checkers/redCrown.png")
redCrown = pygame.transform.scale(redCrown, (tileSize, tileSize))
blackCrown = pygame.image.load("Downloads/Checkers/blackCrown.png")
blackCrown = pygame.transform.scale(blackCrown, (tileSize, tileSize))

class Tile():
  def __init__(self, color, piece, pos):
    self.color = color
    self.piece = piece
    self.pos = pos
    self.rect = pygame.Rect(self.pos.x, self.pos.y, tileSize, tileSize)
  def draw(self):
    pygame.draw.rect(display, self.color, self.rect)
    if self.piece:
      #pygame.draw.circle(display, self.piece.color, self.rect.center, pieceSize)
      display.blit(self.piece.icon, self.rect.topleft)
      

class Piece():
  def __init__(self, color):
    self.color = color
    self.king = False
    self.icon = redPiece if self.color == red else blackPiece
  def makeKing(self):
    self.king = True
    self.icon = redCrown if self.color == red else blackCrown

def populateBoard():
  for i in range(8):
    row = list()
    for j in range(8):
      color = red if (i + j) % 2 == 0 else black
      piece = None
      if j < 3 and color == black:
        piece = Piece(black)
      elif j > 4 and color == black:
        piece = Piece(red)
      row.append(Tile(color, piece, pygame.Vector2(i * tileSize, j * tileSize)))
    board.append(row)

def isValidDropArea(sourceTile, targetTile):
  if sourceTile is None or targetTile is None:
    return False
  dx = targetTile.pos.x - sourceTile.pos.x
  dy = targetTile.pos.y - sourceTile.pos.y
  piece = sourceTile.piece
  if piece is None or targetTile.piece is not None:
    return False
  if piece.king:
    if abs(dx) == tileSize * 2 and abs(dy) == tileSize * 2:
      midX = (targetTile.pos.x + sourceTile.pos.x) // 2
      midY = (targetTile.pos.y + sourceTile.pos.y) // 2
      midTile = board[int(midX // tileSize)][int(midY // tileSize)]
      if midTile and midTile.piece and midTile.piece.color == getOpponentColor(piece.color):
        midTile.piece = None
        return True
    else:
      return abs(dx) == tileSize and abs(dy) == tileSize
  if piece.color == red:
    if dy < 0:
      if abs(dx) == tileSize * 2 and abs(dy) == tileSize * 2:
        midX = (targetTile.pos.x + sourceTile.pos.x) // 2
        midY = (targetTile.pos.y + sourceTile.pos.y) // 2
        midTile = board[int(midX // tileSize)][int(midY // tileSize)]
        if midTile and midTile.piece and midTile.piece.color == black:
          midTile.piece = None
          if targetTile.pos.y == 0:
            piece.makeKing()
          return True
      else:
        if targetTile.pos.y == 0:
          piece.makeKing()
        return abs(dx) == tileSize and abs(dy) == tileSize
  if piece.color == black:
    if dy > 0:
      if abs(dx) == tileSize * 2 and abs(dy) == tileSize * 2:
        midX = (targetTile.pos.x + sourceTile.pos.x) // 2
        midY = (targetTile.pos.y + sourceTile.pos.y) // 2
        midTile = board[int(midX // tileSize)][int(midY // tileSize)]
        if midTile and midTile.piece and midTile.piece.color == red:
          midTile.piece = None
          if targetTile.pos.y == tileSize * 7:
            piece.makeKing()
          return True
      else:
        if targetTile.pos.y == tileSize * 7:
          piece.makeKing()
        return abs(dx) == tileSize and abs(dy) == tileSize
  return False

def createTileCopy(tile):
  return Tile(tile.color, tile.piece, tile.pos)
    
def checkWin(playerColor, board):
  opponentColor = getOpponentColor(playerColor)
  for row in board:
    for tile in row:
      if tile.piece and tile.piece.color == opponentColor:
        return None
  return playerColor

def hasLegalMoves(playerColor, board):
  for row in board:
    for tile in row:
      if tile.piece and tile.piece.color == playerColor:
        if canMove(tile, board):
          return True
  return False

def canMove(sourceTile, board):
  dx = [tileSize, -tileSize]
  dy = [tileSize, -tileSize]
  
  for dxi in dx:
    for dyi in dy:
      newX = sourceTile.pos.x + dxi
      newY = sourceTile.pos.y + dyi
      targetTile = findTile(newX, newY, board)
      if isValidDropArea(sourceTile, targetTile):
        return True
  return False

def findTile(x, y, board):
  # Given x, y coordinates, find the corresponding tile on the board
  for row in board:
    for tile in row:
      if tile.rect.collidepoint(x, y):
        return tile
  return None

def isStalemate(playerColor, board):
  # Check if the current player has any legal moves left
  return not hasLegalMoves(playerColor, board)

def getOpponentColor(playerColor):
  # Returns the opposite color of the current player's color
  return red if playerColor == black else black
  
selectedPiece = None
sourceTile = None
copyTile = None
targetTile = None
selectedPiecePos = pygame.Vector2(0, 0)
selectedPieceOffset = pygame.Vector2(-pieceSize // 2, -pieceSize // 2)
currentPlayerColor = red
chessFont = pygame.sysfont.SysFont('dejavuserif', 36)
colors = {red : "Red", black : "Black"}

populateBoard()
      
print("Selected Piece:", selectedPiece)
print("Source Tile:", copyTile.pos if copyTile else None)
print("Target Tile:", targetTile.pos if targetTile else None)

while True:
  for event in pygame.event.get():
    if event.type == QUIT:
        pygame.quit()
        sys.exit()
    elif event.type == MOUSEBUTTONDOWN:
      os.system('clear')
      pos = pygame.mouse.get_pos()
      for row in board:
        for tile in row:
          if tile.rect.collidepoint(pos):
            if not selectedPiece:
              # First click: Select a piece
              if tile.piece and tile.piece.color == currentPlayerColor:
                sourceTile = tile
                copyTile = createTileCopy(tile)
                tile.piece = None
                selectedPiece = copyTile.piece
                selectedPiecePos = pygame.Vector2(
                  pos[0] - selectedPieceOffset.x,
                  pos[1] - selectedPieceOffset.y
                )
            else:
            # Second click: Drop the selected piece
              targetTile = tile
              if isValidDropArea(copyTile, targetTile):
                targetTile.piece = selectedPiece
                print("Piece moved successfully!")
                selectedPiece = None  # Reset the selected piece
                copyTile.piece = None # Reset the source tile
                winner = checkWin(currentPlayerColor, board)
                if winner:
                    text = f"{colors[currentPlayerColor]} wins!"
                    textRender = chessFont.render(text, True, white)
                    textRect = textRender.get_rect(center = (screenSize // 2, screenSize // 2))
                    display.blit(textRender, textRect)
                    pygame.display.flip()
                    pygame.time.wait(5000)
                    pygame.quit()
                    sys.exit()
                currentPlayerColor = getOpponentColor(currentPlayerColor)
                if isStalemate(currentPlayerColor, board):
                  text = "Stalemate! The game is a draw."
                  textRender = chessFont.render(text, True, white)
                  textRect = textRender.get_rect(center = (screenSize // 2, screenSize // 2))
                  display.blit(textRender, textRect)
                  pygame.display.flip()
                  pygame.time.wait(5000)
                  pygame.quit()
                  sys.exit()
              else:
                # If the drop area is not valid, return the piece to its source
                sourceTile.piece = selectedPiece
                print("Invalid move. Piece returned to its source.")
              selectedPiece = None  # Reset the selected piece
              copyTile = None
      print("Selected Piece:", selectedPiece)
      print("Source Tile:", copyTile.pos if copyTile else None)
      print("Target Tile:", targetTile.pos if targetTile else None)
    elif event.type == MOUSEMOTION:
      if selectedPiece:
          pos = pygame.mouse.get_pos()
          selectedPiecePos = pygame.Vector2(
            pos[0] - selectedPieceOffset.x,
            pos[1] - selectedPieceOffset.y
          )
  for row in board:
    for tile in row:
      tile.draw()
  if selectedPiece:
    #pygame.draw.circle(display, selectedPiece.color, selectedPiecePos, pieceSize) 
    display.blit(selectedPiece.icon, selectedPiecePos + selectedPieceOffset * 3)
  pygame.display.update()