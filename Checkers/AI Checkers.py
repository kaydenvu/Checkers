import sys, os, copy

import pygame
from pygame.locals import QUIT, MOUSEBUTTONDOWN, MOUSEMOTION

pygame.init()
screenSize = 600
display = pygame.display.set_mode((screenSize, screenSize))
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
  def __init__(self, color, pos):
    self.color = color
    self.king = False
    self.pos = pos
    self.row = self.pos[0]
    self.col = self.pos[1]
    self.icon = redPiece if self.color == red else blackPiece
  def makeKing(self):
    self.king = True
    self.icon = redCrown if self.color == red else blackCrown
  def move(self, row, col):
    self.row = row
    self.col = col

def populateBoard():
    for i in range(8):
        row = list()
        for j in range(8):
            color = red if (i + j) % 2 == 0 else black
            piece = None
            if i < 3 and color == black:
                piece = Piece(black, (i, j))
            elif i > 4 and color == black:
                piece = Piece(red, (i, j))
            row.append(Tile(color, piece, pygame.Vector2(j * tileSize, i * tileSize)))  # Swap i and j
        board.append(row)

def simulate_move(piece, board, move):

    new_board = createBoardCopy(board)
    source, target, midTile = move[0], move[1], move[2]
    new_board[target[0]][target[1]].piece = piece
    new_board[source[0]][source[1]].piece = None
    new_board[midTile[0]][midTile[1]].piece = None
    if piece:
      piece.move(target[0], target[1])
    return new_board

def get_piece_moves(board, pos):
    """
    Generates all legal moves for the given piece.
    """
    moves = []
    piece = board[pos[0]][pos[1]].piece
    tile = board[pos[0]][pos[1]]
    if piece:
        dx = [1, -1]
        dy = [1, -1]
        for dxi in dx:
            for dyi in dy:
                newX = pos[0] + dxi
                newY = pos[1] + dyi
                if newX < 0 or newX > 7 or newY < 0 or newY > 7:
                    continue
                targetTile = board[newX][newY]
                if isValidDropArea(tile, targetTile):
                    moves.append([pos, (newX, newY), pos])
        dx = [2, -2]
        dy = [2, -2]
        for dxi in dx:
          for dyi in dy:
            newX = pos[0] + dxi
            newY = pos[1] + dyi
            midX = pos[0] + dxi // 2
            midY = pos[1] + dyi // 2
            if newX < 0 or newX > 7 or newY < 0 or newY > 7:
                continue
            targetTile = board[newX][newY]
            if isValidDropArea(tile, targetTile):
              moves.append([pos, (newX, newY), (midX, midY)])
    return moves

def get_all_pieces(board, color):
   pieces = []
   for row in board:
      for tile in row:
        if tile.piece and tile.piece.color == color:
          pieces.append(tile.piece)
   return pieces

def get_all_kings(board, color):
   kings = []
   for row in board:
      for tile in row:
        if tile.piece and tile.piece.color == color and tile.piece.king:
          kings.append(tile.piece)
   return kings


def get_all_possible_moves(board, color):
    """
    Generates all legal moves for the given player.
    """
    moves = []
    for piece in get_all_pieces(board, color):
        valid_moves = get_piece_moves(board, piece.pos)
        for move in valid_moves:
            temp_board = createBoardCopy(board)
            temp_piece = temp_board[move[0][0]][move[0][1]].piece
            new_board = simulate_move(temp_piece, board, move)
            moves.append(new_board)
    return moves

def game_over(board):
    """
    Checks if the game is over.
    Returns True if a player has no pieces left or cannot make any legal moves.
    """
    black_has_pieces, red_has_pieces = False, False
    black_can_move, red_can_move = False, False

    for row in board:
        for tile in row:
            if tile.piece:
                if tile.piece.color == black:
                    black_has_pieces = True
                    if canMove(tile, board):
                        black_can_move = True
                else:
                    red_has_pieces = True
                    if canMove(tile, board):
                        red_can_move = True

    return not (black_has_pieces and black_can_move) or not (red_has_pieces and red_can_move)

def evaluate_board(board, color):
    piece_weight = 1
    king_weight = 2

    player_pieces = get_all_pieces(board, color)
    opponent_pieces = get_all_pieces(board, getOpponentColor(color))
    player_kings = get_all_kings(board, color)
    opponent_kings = get_all_kings(board, getOpponentColor(color))

    player_score = len(player_pieces) * piece_weight + len(player_kings) * king_weight
    opponent_score = len(opponent_pieces) * piece_weight + len(opponent_kings) * king_weight

    # Positional Advantage: Add bonus for pieces closer to the king's row
    king_row = 0 if color == "red" else 7
    for piece in player_pieces:
        if piece.pos[0] >= king_row - 2:
            player_score += 2  # Adjust the bonus value as needed

    for piece in opponent_pieces:
        if piece.pos[0] <= 2 + king_row:
            opponent_score += 2  # Adjust the bonus value as needed

    return player_score - opponent_score

def minimax(board, depth, is_maximizing, current_color):
    """
    Minimax algorithm with alpha-beta pruning.
    """
    if depth == 0 or game_over(board):
        return evaluate_board(board, current_color), board

    if is_maximizing:
        max_eval = float('-inf')
        best_move = None

        for move in get_all_possible_moves(board, current_color):
            evaluation = minimax(move, depth - 1, False, current_color)[0]
            max_eval = max(max_eval, evaluation)

            if max_eval == evaluation:
                best_move = move

        return max_eval, best_move
    else:
        min_eval = float('inf')
        best_move = None

        for move in get_all_possible_moves(board, getOpponentColor(current_color)):
            evaluation = minimax(move, depth - 1, True, current_color)[0]
            min_eval = min(min_eval, evaluation)

            if min_eval == evaluation:
                best_move = move

        return min_eval, best_move
    
def checkingKinging(piece, targetTile):
    if piece.color == red:
        if targetTile.pos.y == 0:
            piece.makeKing()
    elif piece.color == black:
        if targetTile.pos.y == tileSize * 7:
            piece.makeKing()

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
      midY = (targetTile.pos.x + sourceTile.pos.x) // 2
      midX = (targetTile.pos.y + sourceTile.pos.y) // 2
      midTile = board[int(midX // tileSize)][int(midY // tileSize)]
      if midTile and midTile.piece and midTile.piece.color == getOpponentColor(piece.color):
        midTile.piece = None
        return True
    else:
      return abs(dx) == tileSize and abs(dy) == tileSize
  if piece.color == red:
    if dy < 0:
      if abs(dx) == tileSize * 2 and abs(dy) == tileSize * 2:
        midY = (targetTile.pos.x + sourceTile.pos.x) // 2
        midX = (targetTile.pos.y + sourceTile.pos.y) // 2
        midTile = board[int(midX // tileSize)][int(midY // tileSize)]
        if midTile and midTile.piece and midTile.piece.color == black:
          midTile.piece = None
          return True
      else:
        return abs(dx) == tileSize and abs(dy) == tileSize
  if piece.color == black:
    if dy > 0:
      if abs(dx) == tileSize * 2 and abs(dy) == tileSize * 2:
        midY = (targetTile.pos.x + sourceTile.pos.x) // 2
        midX = (targetTile.pos.y + sourceTile.pos.y) // 2
        midTile = board[int(midX // tileSize)][int(midY // tileSize)]
        if midTile and midTile.piece and midTile.piece.color == red:
          midTile.piece = None
          return True
      else:
        return abs(dx) == tileSize and abs(dy) == tileSize
  return False

def createTileCopy(tile):
  return Tile(tile.color, tile.piece, tile.pos)
    
def createBoardCopy(board):
    new_board = []
    for row in board:
        new_row = []
        for tile in row:
            new_tile = Tile(tile.color, tile.piece, tile.pos)
            new_row.append(new_tile)
        new_board.append(new_row)
    return new_board

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
  for row in board:
    for tile in row:
      if tile.rect.collidepoint(x, y):
        return tile
  return None

def isStalemate(playerColor, board):
  return not hasLegalMoves(playerColor, board)

def getOpponentColor(playerColor):
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

def printBoard(board):
  for row in board:
    for tile in row:
        if tile.piece:
          if tile.piece.color == black:
              print("B", end = " ")
          else:
              print("R", end = " ")
        else:
          print("0", end = " ")
    print()

printBoard(board)

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
              targetTile = tile
              if isValidDropArea(copyTile, targetTile):
                targetTile.piece = selectedPiece
                checkingKinging(selectedPiece, targetTile)
                print("Selected Piece:", selectedPiece)
                print("Source Tile:", copyTile.pos if copyTile else None)
                print("Target Tile:", targetTile.pos if targetTile else None)
                print("Piece moved successfully!")
                targetTile = None
                selectedPiece = None  
                copyTile.piece = None
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
                if currentPlayerColor == black:
                    new_board = createBoardCopy(board)
                    value, new_board = minimax(new_board, 5, True, currentPlayerColor)
                    if new_board:
                      board = new_board
                    currentPlayerColor = getOpponentColor(currentPlayerColor)
                # printBoard(board)
              else:
                sourceTile.piece = selectedPiece
                print("Invalid move. Piece returned to its source.")
              selectedPiece = None
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