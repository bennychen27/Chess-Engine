'''
The main driver file. Responsible for handling user input and displaying current Game State Object
'''
import os

import numpy as np
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import math
import pygame as pg
import ChessEngine
import ChessAI
from multiprocessing import Process, Queue

pg.init()
BOARD_WIDTH, BOARD_HEIGHT = 768, 768
MOVELOG_WIDTH, MOVELOG_HEIGHT = 256, BOARD_HEIGHT
DIMENSION = 8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}
WHITE = pg.Color('white')
BLACK = pg.Color('black')
DARKGRAY = pg.Color('darkgray')
GREEN = pg.Color('green2')
FONT = pg.font.SysFont('Helvitca', 30, True, False)
SMALLFONT = pg.font.SysFont('Helvitca', 20, True, False)
BG = pg.transform.scale(pg.image.load('images/tournament.png'), (BOARD_WIDTH, BOARD_HEIGHT))

'''
Initialize a global dictionary of images. Only called once, since it will be expensive to call multiple times
'''
def loadImages():

    pieces = ['tournamentwP', 'tournamentwR', 'tournamentwN', 'tournamentwB', 'tournamentwQ', 'tournamentwK', 
    'tournamentbP', 'tournamentbR', 'tournamentbN', 'tournamentbB', 'tournamentbQ', 'tournamentbK',
    'classicwP', 'classicwR', 'classicwN', 'classicwB', 'classicwQ', 'classicwK', 'classicbP', 'classicbR', 'classicbN', 'classicbB', 'classicbQ', 'classicbK',
    'neowP', 'neowR', 'neowN', 'neowB', 'neowQ', 'neowK', 'neobP', 'neobR', 'neobN', 'neobB', 'neobQ', 'neobK',
    'woodwP', 'woodwR', 'woodwN', 'woodwB', 'woodwQ', 'woodwK', 'woodbP', 'woodbR', 'woodbN', 'woodbB', 'woodbQ', 'woodbK',
    'glasswP', 'glasswR', 'glasswN', 'glasswB', 'glasswQ', 'glasswK', 'glassbP', 'glassbR', 'glassbN', 'glassbB', 'glassbQ', 'glassbK']
    backgrounds = ['green', 'walnut', 'tournament', 'sand', 'icysea']
    #now we can access an image at any board with 'IMAGES['__']'
    for piece in pieces:

        IMAGES[piece] = pg.transform.scale(pg.image.load('images/' + piece + '.png'), (SQ_SIZE, SQ_SIZE))

    for background in backgrounds:

        IMAGES[background] = pg.transform.scale(pg.image.load('images/' + background + '.png'), (BOARD_WIDTH, BOARD_HEIGHT))

'''
Main driver to handle user input and updating the graphics.
'''
def main():

    screen = pg.display.set_mode((BOARD_WIDTH + MOVELOG_WIDTH, BOARD_HEIGHT))
    clock = pg.time.Clock()
    screen.fill(WHITE)
    screen.blit(BG, (0, 0))
    gameState = ChessEngine.GameState()
    validMoves = gameState.getValidMoves() #expensive operation to call every time, store possible valid moves to reduce repetition
    moveMade = False #flag variable -- only update validMoves list if user makes a move in the validMoves list
    animate = False
    reset = False
    gameStart, gameOver = False, False
    whitePlayer, blackPlayer = True, True #flag variable -- if true, then human plays for that color, if false, then AI plays for that color
    AIThinking = False
    moveFinderProcess = None
    moveUndone = False
    fiftyMoveRuleCounter = 0
    firstPage = True
    choosingWhitePlayer, choosingBlackPlayer = True, True
    choosingPlayers, choosingBoardStyle, choosingPieceStyle = True, True, True
    choosing = True
    startPressed = False
    flipped = False
    rotate = False

    loadImages() #only do this once, before the while loop

    open = True
    sqClicked = () #keeps track of last click from user, (row, col)
    playerClicks = [] #keeps track of player clicks, max of 2 inputs. i.e [(1, 1), (2, 2)]
    whiteScore, blackScore = 0, 0
    gameState.getBoardMaterial()
    layout(screen, BLACK, FONT)
    chooseWhiteScreen(screen, DARKGRAY, DARKGRAY, BLACK, SMALLFONT)
    chooseBlackScreen(screen, DARKGRAY, DARKGRAY, BLACK, SMALLFONT)
    chooseBoardStyle(screen, DARKGRAY, DARKGRAY, DARKGRAY, DARKGRAY, BLACK, SMALLFONT)
    choosePieceStyle(screen, DARKGRAY, DARKGRAY, DARKGRAY, DARKGRAY, BLACK, SMALLFONT)  
    background = IMAGES['tournament'] #default board background
    backgroundColor = (164, 194, 91) #default board background color
    pieceStyle = 'tournament' #default piece style

    while open:

        humanTurn = (gameState.whiteToMove and whitePlayer) or (not gameState.whiteToMove and blackPlayer) or not startPressed

        for event in pg.event.get():

            #program ends if user X's out of window
            if event.type == pg.QUIT:

                open = False

            #mouse handlers
            elif event.type == pg.MOUSEBUTTONDOWN:

                if not gameOver and not reset and humanTurn:

                    coord = pg.mouse.get_pos() #get x, y coord point of mouse when click
                    row, col = coord[1] // SQ_SIZE, coord[0] // SQ_SIZE

                    if flipped: #if screen is flipped, revert the coordinates

                        row, col = gameState.ROWS - 1 - row, gameState.COLS - 1 - col

                    if not startPressed: #if game hasnt start yeted

                        if coord[0] < 8:

                            continue

                        elif coord[0] >= BOARD_WIDTH:
                            #choosing player selection for white/black
                            topLeft1 = pg.Rect(BOARD_WIDTH + 30, 30, 90, 60)
                            botLeft1 = pg.Rect(BOARD_WIDTH + 30, 110, 90, 60)
                            topRight1 = pg.Rect(BOARD_WIDTH + 140, 30, 90, 60)
                            botRight1 = pg.Rect(BOARD_WIDTH + 140, 110, 90, 60)
                            #choosing board style
                            topLeft2 = pg.Rect(BOARD_WIDTH + 30, 250, 90, 60)
                            botLeft2 = pg.Rect(BOARD_WIDTH + 30, 330, 90, 60)
                            topRight2 = pg.Rect(BOARD_WIDTH + 140, 250, 90, 60)
                            botRight2 = pg.Rect(BOARD_WIDTH + 140, 330, 90, 60)
                            #choosing piece style
                            topLeft3 = pg.Rect(BOARD_WIDTH + 30, 465, 90, 60)
                            botLeft3 = pg.Rect(BOARD_WIDTH + 30, 545, 90, 60)
                            topRight3 = pg.Rect(BOARD_WIDTH + 140, 465, 90, 60)
                            botRight3 = pg.Rect(BOARD_WIDTH + 140, 545, 90, 60)

                            if topLeft1.collidepoint(coord):

                                choosingWhitePlayer = False
                                whitePlayer = True
                                chooseWhiteScreen(screen, GREEN, DARKGRAY, BLACK, SMALLFONT)

                            elif topRight1.collidepoint(coord):

                                choosingBlackPlayer = False
                                blackPlayer = True
                                chooseBlackScreen(screen, GREEN, DARKGRAY, BLACK, SMALLFONT)

                            elif botLeft1.collidepoint(coord):

                                choosingWhitePlayer = False
                                whitePlayer = False
                                chooseWhiteScreen(screen, DARKGRAY, GREEN, BLACK, SMALLFONT)
                                
                            elif botRight1.collidepoint(coord):

                                choosingBlackPlayer = False
                                blackPlayer = False
                                chooseBlackScreen(screen, DARKGRAY, GREEN, BLACK, SMALLFONT)

                            elif topLeft2.collidepoint(coord):

                                choosingBoardStyle = False
                                background = IMAGES['green']
                                backgroundColor = (255, 255, 0)
                                chooseBoardStyle(screen, GREEN, DARKGRAY, DARKGRAY, DARKGRAY, BLACK, SMALLFONT)

                            elif topRight2.collidepoint(coord):

                                choosingBoardStyle = False
                                background = IMAGES['icysea']
                                backgroundColor = (94, 215, 241)
                                chooseBoardStyle(screen, DARKGRAY, DARKGRAY, GREEN, DARKGRAY, BLACK, SMALLFONT)

                            elif botLeft2.collidepoint(coord):

                                choosingBoardStyle = False
                                background = IMAGES['walnut']
                                backgroundColor = (209, 165, 45)
                                chooseBoardStyle(screen, DARKGRAY, GREEN, DARKGRAY, DARKGRAY, BLACK, SMALLFONT)

                            elif botRight2.collidepoint(coord):
                                
                                choosingBoardStyle = False
                                background = IMAGES['sand']
                                backgroundColor = (226, 188, 135)
                                chooseBoardStyle(screen, DARKGRAY, DARKGRAY, DARKGRAY, GREEN, BLACK, SMALLFONT)

                            elif topLeft3.collidepoint(coord):

                                choosingPieceStyle = False
                                choosePieceStyle(screen, GREEN, DARKGRAY, DARKGRAY, DARKGRAY, BLACK, SMALLFONT)
                                pieceStyle = 'classic'

                            elif topRight3.collidepoint(coord):

                                choosingPieceStyle = False
                                choosePieceStyle(screen, DARKGRAY, DARKGRAY, GREEN, DARKGRAY, BLACK, SMALLFONT)
                                pieceStyle = 'neo'

                            elif botLeft3.collidepoint(coord):

                                choosingPieceStyle = False
                                choosePieceStyle(screen, DARKGRAY, GREEN, DARKGRAY, DARKGRAY, BLACK, SMALLFONT)
                                pieceStyle = 'wood'

                            elif botRight3.collidepoint(coord):

                                choosingPieceStyle = False
                                choosePieceStyle(screen, DARKGRAY, DARKGRAY, DARKGRAY, GREEN, BLACK, SMALLFONT)
                                pieceStyle = 'glass'

                            if not choosingWhitePlayer and not choosingBlackPlayer:

                                choosingPlayers = False #once user chooses white/black players, change flag variable
                            #if user is done choosing settings, change flag variable to true, else false
                            if choosingPlayers or choosingBoardStyle or choosingPieceStyle:

                                choosing = True

                            else:

                                choosing = False

                            if choosing:

                                start(screen, DARKGRAY, BLACK) #while player is choosing, start button isnt clickable                                

                            elif not gameStart:

                                start(screen, GREEN, BLACK) #choosing and game hasnt start yet, then start button now clickable

                                startRect = pg.Rect((BOARD_WIDTH + 20, BOARD_HEIGHT / 2 + 278, 210, 80))
                                if startRect.collidepoint(coord):

                                    startPressed = True #if user clicks on start button, then change flag variable to true
                                    screen.fill(WHITE, (BOARD_WIDTH, 20, BOARD_WIDTH + MOVELOG_WIDTH, BOARD_HEIGHT)) #clear the settings menu
                                    gameStart = True #change flag variable to true
                     
                    elif sqClicked == (row, col) or col >= 8: #if user clicks same spot twice or outside of board, reset clicks

                        sqClicked = ()
                        playerClicks = []

                    else: #append the click

                        sqClicked = (row, col)
                        playerClicks.append(sqClicked)

                    if len(playerClicks) == 2: #if user's 2nd click
                        
                        move = ChessEngine.Move(0, playerClicks[0], playerClicks[1], gameState.board)
                        for validMove in validMoves:

                            if move == validMove:

                                if math.ceil(len(gameState.moveLog) / 2) >= 37 and firstPage and gameState.whiteToMove: #if 38th move, then clear move log display

                                    screen.fill(WHITE, (BOARD_WIDTH, 20, BOARD_WIDTH + MOVELOG_WIDTH, BOARD_HEIGHT))
                                    firstPage = False

                                gameState.makeMove(validMove)
                                displayMoveLog(screen, gameState, validMove)

                                if validMove.pieceCaptured != '--' or validMove.isEnpassantMove:

                                    gameState.boardMaterial[validMove.pieceCaptured] -= 1

                                if validMove.isPawnPromotion:

                                    gameState.boardMaterial[validMove.pieceMoved] -= 1
                                    gameState.boardMaterial[gameState.board[validMove.endSq[0]][validMove.endSq[1]]] += 1

                                if whitePlayer and blackPlayer:

                                    rotate = True #if both human players for white/black, then change rotate flag to true

                                moveMade = True
                                animate = True
                                #reset user clicks
                                sqClicked = ()
                                playerClicks = []

                        if not moveMade: #no move was made, 1st click is now our 2nd click

                            playerClicks = [(sqClicked)]    

            #key handlers
            elif event.type == pg.KEYDOWN:
                #clear previous move from board and move log display
                if event.key == pg.K_BACKSPACE and not gameOver and len(gameState.moveLog) > 0:
                    
                    if len(gameState.moveLog) % 2:

                        screen.fill(WHITE, (BOARD_WIDTH + 30, 20 * math.ceil(len(gameState.moveLog) / 2), 90, 20))

                    elif not len(gameState.moveLog) % 2:

                        screen.fill(WHITE, (BOARD_WIDTH + 150, 20 * math.ceil(len(gameState.moveLog) / 2), BOARD_WIDTH + MOVELOG_WIDTH, 20))

                    gameState.undoMove() #if user presses backspace, revert gameState back by one move
                    if math.ceil(len(gameState.moveLog) / 2) >= 37:

                        screen.fill(WHITE, (BOARD_WIDTH, 20, BOARD_WIDTH + MOVELOG_WIDTH, BOARD_HEIGHT))

                    gameState.getBoardMaterial()
                    moveMade = True
                    animate = False
                    gameOver = False

                    if AIThinking: #if ai is still calculating move, then terminate it 

                        moveFinderProcess.terminate()
                        AIThinking = False
                        moveUndone = True

                if event.key == pg.K_f: #flips the board

                    flipped = True if not flipped else False

                if event.key == pg.K_t:

                    if whitePlayer and blackPlayer: #if human white/black, switch to computer white/black

                        whitePlayer = False
                        blackPlayer = False
                    
                    elif not whitePlayer and not blackPlayer: #if computer white/black, switch to human white/black

                        whitePlayer = True
                        blackPlayer = True

                if event.key == pg.K_r:

                    reset = True

                if event.key == pg.K_y and reset: #if user presses y after r was pressed

                    if gameState.checkmate: #white's score +1 if white won, else black +1.

                        if not gameState.whiteToMove:

                            whiteScore += 1

                        else:

                            blackScore += 1
                    
                    elif gameState.stalemate: #white/black's score +0.5 if stalemate

                        whiteScore += 0.5
                        blackScore += 0.5
                    
                    #reset all variables, new game started
                    gameState = ChessEngine.GameState()
                    humanTurn = (gameState.whiteToMove and whitePlayer) or (not gameState.whiteToMove and blackPlayer)
                    validMoves = gameState.getValidMoves()
                    animate = False
                    moveMade = False
                    reset = False
                    gameOver = False
                    playerClicks = []
                    sqClicked = ()
                    gameState.getBoardMaterial()
                    if AIThinking:

                        moveFinderProcess.terminate()
                        AIThinking = False
                    
                    fiftyMoveRuleCounter = 0

                    screen.fill(WHITE, (BOARD_WIDTH, 20, BOARD_WIDTH + MOVELOG_WIDTH, BOARD_HEIGHT))

                if event.key == pg.K_n and reset: #if user presses n after pressing r, then print score +1 to whoever won the current game, then close the window

                    if gameState.checkmate:

                        if not gameState.whiteToMove:

                            whiteScore += 1

                        else:

                            blackScore += 1

                    elif gameState.stalemate:

                        whiteScore += 0.5
                        blackScore += 0.5

                    gameOver = True
                    reset = False
                    if gameOver:
                        
                        print('Thanks for playing!\nWhite score: ' + str(whiteScore) + '\nBlack score: ' + str(blackScore))
                        open = False

        if not gameOver and not humanTurn and not moveUndone and gameStart: #ai playing

            if not AIThinking:

                AIThinking = True
                returnQueue = Queue() #used to pass data between threads
                moveFinderProcess = Process(target = ChessAI.findBestNegaMaxAlphaBetaMove, args = (gameState, validMoves, returnQueue))
                moveFinderProcess.start()

            if not moveFinderProcess.is_alive():

                move = returnQueue.get()
                if move is None:

                    print('Could not find optimal move.')
                    move = ChessAI.findBestMove(gameState, validMoves)

                gameState.makeMove(move)
                highlightSquares(screen, gameState, validMoves, sqClicked, backgroundColor, flipped)
                displayMoveLog(screen, gameState, move) 

                if math.ceil(len(gameState.moveLog) / 2) >= 37 and firstPage and gameState.whiteToMove:

                    screen.fill(WHITE, (BOARD_WIDTH, 20, BOARD_WIDTH + MOVELOG_WIDTH, BOARD_HEIGHT))
                    firstPage = False     

                if move.pieceCaptured != '--' or move.isEnpassantMove:

                    gameState.boardMaterial[move.pieceCaptured] -= 1

                if move.isPawnPromotion:

                    gameState.boardMaterial[move.pieceMoved] -= 1
                    gameState.boardMaterial[gameState.board[move.endSq[0]][move.endSq[1]]] += 1

                moveMade = True
                animate = True
                AIThinking = False

        #if valid move was made, then we update the list of valid moves and reset flag variable
        if moveMade:

            if animate:

                animateMove(screen, gameState, clock, gameState.moveLog[-1], validMoves, sqClicked, background, backgroundColor, pieceStyle, flipped)

            validMoves = gameState.getValidMoves()
            moveMade = False
            moveUndone = False
            #Reset counter if piece was captured or pawn moved, else increment
            if move.pieceCaptured != '--' or move.pieceMoved[1] == 'P':

                fiftyMoveRuleCounter = 0

            else:

                fiftyMoveRuleCounter += 1

            if fiftyMoveRuleCounter >= 50: #If 50 moves without piece captured or pawn moving, then stalemate

                gameState.stalemate = True

        createBoard(screen, gameState, validMoves, sqClicked, background, backgroundColor, pieceStyle, flipped)
        if rotate: #human vs human, player made move, flip the board

            flipped = not flipped
            rotate = False

        while reset: #display new game text as long as reset is true

            newGame(screen)
            break

        if gameState.checkmate or gameState.stalemate:

            gameOver = True
            gameCompleted(screen, gameState)
            newGame(screen)
            reset = True
            gameState.getBoardMaterial()

        clock.tick(MAX_FPS)
        pg.display.flip()

'''
Highlight the square where piece is currently at and squares where piece can move to for the piece selected. Also highlights previous move.
'''
def highlightSquares(screen, gameState, validMoves, sqSelected, backgroundColor, flipped):

    surface = pg.Surface((SQ_SIZE, SQ_SIZE))
    surface.set_alpha(150)
    surface.fill(backgroundColor)
    flipValue = 7 if flipped else 0 #flipValue is so we can mirror the (row,col) if board is flipped

    if sqSelected != ():

        row, col = sqSelected
        if gameState.board[row][col][0] == ('w' if gameState.whiteToMove else 'b'): #if piece selected is a piece that can be moved

            screen.blit(surface, (abs(flipValue - col) * SQ_SIZE, abs(flipValue - row) * SQ_SIZE)) #highlight current square clicked

            for move in validMoves: #show the possible moves for that piece, small gray circle for empty space and large gray circle for capturable piece

                if move.startSq[0] == row and move.startSq[1] == col:

                    if gameState.board[move.endSq[0]][move.endSq[1]] == '--':

                        pg.draw.circle(screen, DARKGRAY, ((SQ_SIZE // 2) + SQ_SIZE * abs(flipValue - move.endSq[1]), 
                                        (SQ_SIZE // 2) + SQ_SIZE * abs(flipValue - move.endSq[0])), SQ_SIZE//5, 0)

                    else:

                        pg.draw.circle(screen, DARKGRAY, ((SQ_SIZE // 2) + SQ_SIZE * abs(flipValue - move.endSq[1]), 
                                        (SQ_SIZE // 2) + SQ_SIZE * abs(flipValue - move.endSq[0])), SQ_SIZE//2, 6)   

    if len(gameState.moveLog) > 0: #if at least 1 move in move log, then highlight the squares of previous move

        screen.blit(surface, (abs(flipValue - gameState.moveLog[-1].endSq[1]) * SQ_SIZE, abs(flipValue - gameState.moveLog[-1].endSq[0]) * SQ_SIZE))
        screen.blit(surface, (abs(flipValue - gameState.moveLog[-1].startSq[1]) * SQ_SIZE, abs(flipValue - gameState.moveLog[-1].startSq[0]) * SQ_SIZE))

'''
Draw the squares on the board, as well as the pieces using the current gameState board.
Note: The top left square is ALWAYS light regardless if black/white side. 
'''
def createBoard(screen, gameState, validMoves, sqClicked, background, backgroundColor, pieceStyle, flipped):
    screen.blit(background, (0, 0))
    surface = pg.Surface((BOARD_WIDTH, BOARD_HEIGHT))
    surface.set_alpha(0)
    for row in range(0, DIMENSION):

        for col in range(0, DIMENSION):

            if ((row + col) % 2 == 0):

                screen.blit(surface, (SQ_SIZE * col, SQ_SIZE * row))

            else:

                screen.blit(surface, (SQ_SIZE * col, SQ_SIZE * row))

    highlightSquares(screen, gameState, validMoves, sqClicked, backgroundColor, flipped)

    for row in range(0, DIMENSION):

        for col in range(0, DIMENSION):

            if not flipped:
                
                if gameState.board[row][col] != '--': #if curr board not empty, draw the piece

                    screen.blit(IMAGES[pieceStyle + gameState.board[row][col]], (SQ_SIZE * col, SQ_SIZE * row))    

            else:

                if np.flip(gameState.board)[row][col] != '--':

                    screen.blit(IMAGES[pieceStyle + np.flip(gameState.board)[row][col]], (SQ_SIZE * col, SQ_SIZE * row)) 
'''
Animates the valid move made
'''
def animateMove(screen, gameState, clock, move, validMoves, sqClicked, background, backgroundColor, pieceStyle, flipped):

    flipValue = 7 if flipped else 0

    dRow, dCol = abs(flipValue - move.endSq[0]) - abs(flipValue - move.startSq[0]), abs(flipValue - move.endSq[1]) - abs(flipValue - move.startSq[1])
    frameCount = (abs(dRow) + abs(dCol)) #total amount of frames to move from start to end square

    for frame in range(0, frameCount + 1):

        row, col = abs(flipValue - move.startSq[0]) + dRow * frame / frameCount, abs(flipValue - move.startSq[1]) + dCol * frame / frameCount
        createBoard(screen, gameState, validMoves, sqClicked, background, backgroundColor, pieceStyle, flipped)
        #erase the piece moved from the ending square
        endSquare = pg.Rect(abs(flipValue - move.endSq[1]) * SQ_SIZE, abs(flipValue - move.endSq[0]) * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        pg.draw.rect(screen, backgroundColor, endSquare)
        #blit captured piece onto the screen
        if move.pieceCaptured != '--':

            screen.blit(IMAGES[pieceStyle + move.pieceCaptured], endSquare)
        #draw moving piece
        screen.blit(IMAGES[pieceStyle + move.pieceMoved], pg.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        pg.display.flip()
        clock.tick(60)
'''
Displays text on screen
'''
def newGame(screen):

    font = pg.font.SysFont('Helvitca', 40, True, False)
    text = font.render('Start a new game? Press y/n', True, pg.Color('black'))
    screen.blit(text, text.get_rect(center = (BOARD_WIDTH / 2, BOARD_HEIGHT / 2)))

'''
Displays text on screen based on if checkmate or stalemate. 
'''
def gameCompleted(screen, gameState):

    font = pg.font.SysFont('Helvitca', 40, True, False)
    checkmateText = font.render('Checkmate. White wins.' if not gameState.whiteToMove else 'Checkmate. Black wins.', True, BLACK)
    stalemateText = font.render('Stalemate. The game is a draw.', True, BLACK)
    if gameState.checkmate:

        screen.blit(checkmateText, checkmateText.get_rect(center  = (BOARD_WIDTH / 2, (BOARD_HEIGHT / 2) - 50)))

    elif gameState.stalemate:

        screen.blit(stalemateText, stalemateText.get_rect(center  = (BOARD_WIDTH / 2, (BOARD_HEIGHT / 2) - 50)))

'''
Displays the move's chess notation for white / black on right side of the screen
'''
def displayMoveLog(screen, gameState, move):

    font = pg.font.SysFont('Helvitca', 24, True, False)
    displayMove = font.render(str(move.getChessNotation()), False, BLACK)
    displayRows = font.render(str(math.ceil(len(gameState.moveLog) / 2)) + '.', False, BLACK)
    newPage = 0

    if math.ceil(len(gameState.moveLog) / 2) >= 38:
    
        newPage = ((BOARD_HEIGHT - 20) // 20)
    
    if len(gameState.moveLog) > 0 and len(gameState.moveLog) % 2:

        screen.blit(displayRows, displayRows.get_rect(topleft = (BOARD_WIDTH + 15, 20 * (math.ceil(len(gameState.moveLog) / 2) - newPage))))

    if not gameState.whiteToMove:

        screen.blit(displayMove, displayMove.get_rect(topleft = (BOARD_WIDTH + 40, 20 * (math.ceil(len(gameState.moveLog) / 2) - newPage))))

    if gameState.whiteToMove:

        screen.blit(displayMove, displayMove.get_rect(topleft = (BOARD_WIDTH + 150, 20 * (math.ceil(len(gameState.moveLog) / 2) - newPage))))

'''
Creates buttons for white's player options at the top of the move log display screen
'''    
def chooseWhiteScreen(screen, button1Color, button2Color, textColor, smallFont):

    pg.draw.rect(screen, button1Color, (BOARD_WIDTH + 30, 30, 90, 60))
    pg.draw.rect(screen, button2Color, (BOARD_WIDTH + 30, 110, 90, 60))
    screen.blit(smallFont.render('Human', True, textColor), (BOARD_WIDTH + 50, 55))
    screen.blit(smallFont.render('Computer', True, textColor), (BOARD_WIDTH + 40, 135))

'''
Creates buttons for black's player options at the top of the move log display screen
'''
def chooseBlackScreen(screen, button1Color, button2Color, textColor, smallFont):

    pg.draw.rect(screen, button1Color, (BOARD_WIDTH + 140, 30, 90, 60))
    pg.draw.rect(screen, button2Color, (BOARD_WIDTH + 140, 110, 90, 60))
    screen.blit(smallFont.render('Human', True,textColor), (BOARD_WIDTH + 160, 55))
    screen.blit(smallFont.render('Computer', True, textColor), (BOARD_WIDTH + 150, 135))

'''
Creates buttons for board styles in the middle of the move log display screen
'''
def chooseBoardStyle(screen, button1Color, button2Color, button3Color, button4Color, textColor, smallFont):

    pg.draw.rect(screen, button1Color, (BOARD_WIDTH + 30, 250, 90, 60))
    pg.draw.rect(screen, button2Color, (BOARD_WIDTH + 30, 330, 90, 60))
    pg.draw.rect(screen, button3Color, (BOARD_WIDTH + 140, 250, 90, 60))
    pg.draw.rect(screen, button4Color, (BOARD_WIDTH + 140, 330, 90, 60))
    screen.blit(smallFont.render('Green', True, textColor), (BOARD_WIDTH + 55, 275))
    screen.blit(smallFont.render('Icy Sea', True,textColor), (BOARD_WIDTH + 157, 275))
    screen.blit(smallFont.render('Wood', True, textColor), (BOARD_WIDTH + 55, 352))
    screen.blit(smallFont.render('Sand', True, textColor), (BOARD_WIDTH + 165, 352))

'''
Creates buttons for piece styles at the bottom of the move log display screen
'''
def choosePieceStyle(screen, button1Color, button2Color, button3Color, button4Color, textColor, smallFont):

    pg.draw.rect(screen, button1Color, (BOARD_WIDTH + 30, 465, 90, 60))
    pg.draw.rect(screen, button2Color, (BOARD_WIDTH + 30, 545, 90, 60))
    pg.draw.rect(screen, button3Color, (BOARD_WIDTH + 140, 465, 90, 60))
    pg.draw.rect(screen, button4Color, (BOARD_WIDTH + 140, 545, 90, 60))
    screen.blit(smallFont.render('Classic', True, textColor), (BOARD_WIDTH + 49, 487))
    screen.blit(smallFont.render('Neo', True,textColor), (BOARD_WIDTH + 170, 487))
    screen.blit(smallFont.render('Wood', True, textColor), (BOARD_WIDTH + 53, 565))
    screen.blit(smallFont.render('Glass', True, textColor), (BOARD_WIDTH + 162, 565)) 

'''
Creates a start button at the bottom of the move log display screen
'''
def start(screen, buttonColor, textColor):

    startFont = pg.font.SysFont('Helvitca', 60, True, False)
    startText = startFont.render('START', True, textColor)
    pg.draw.rect(screen, buttonColor, (BOARD_WIDTH + 20, BOARD_HEIGHT / 2 + 278, 210, 80))
    screen.blit(startText, startText.get_rect(topleft = (BOARD_WIDTH + 47, BOARD_HEIGHT / 2 + 300)))

'''
UI layout for move log display screen
'''   
def layout(screen, textColor, font):

    whiteText = font.render('White', True, textColor)
    blackText = font.render('Black', True, textColor)
    screen.blit(whiteText, whiteText.get_rect(topleft = (BOARD_WIDTH + 40, 0)))
    screen.blit(blackText, blackText.get_rect(topleft = (BOARD_WIDTH + 150, 0)))
    screen.blit(font.render('Select Player Choice', True, textColor), (BOARD_WIDTH + 5, BOARD_HEIGHT / 2 - 190))
    screen.blit(font.render('Select Board Style', True, textColor), (BOARD_WIDTH + 20, BOARD_HEIGHT / 2 + 25))
    screen.blit(font.render('Select Piece Style', True, textColor), (BOARD_WIDTH + 25, BOARD_HEIGHT / 2 + 240))
    pg.draw.line(screen, textColor, (BOARD_WIDTH, BOARD_HEIGHT / 2 - 150), (BOARD_WIDTH + MOVELOG_WIDTH, BOARD_HEIGHT / 2 - 150), 10)
    pg.draw.line(screen, textColor, (BOARD_WIDTH, BOARD_HEIGHT / 2 + 60), (BOARD_WIDTH + MOVELOG_WIDTH, BOARD_HEIGHT / 2 + 60), 10)
    start(screen, DARKGRAY, textColor)

#this is convention to protect from accidentally running the program when we import another class
if __name__ == '__main__':

    main()