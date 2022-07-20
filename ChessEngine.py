'''
Stores all the information about the current state of a chess game. It will also determine the valid moves at the current state.
'''
class GameState():

    def __init__(self):
        '''
        Board is an 8x8 2d list, each element in list has 2 characters. 
        First character: 'b' for black, 'w' for white. 
        Second character: 'P' for pawn, 'R' for rook, 'N' for knight, 'B' for bishop, 'Q' for queen, 'K' for king.
        A '--' represents an empty space with no piece
        '''
        self.board = [['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
                      ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
                      ['--', '--', '--', '--', '--', '--', '--', '--'],
                      ['--', '--', '--', '--', '--', '--', '--', '--'], 
                      ['--', '--', '--', '--', '--', '--', '--', '--'], 
                      ['--', '--', '--', '--', '--', '--', '--', '--'],
                      ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
                      ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']]
        
        self.moveFunctions = {'P': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves, 'B': self.getBishopMoves,
                        'Q': self.getQueenMoves, 'K': self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.ROWS, self.COLS = len(self.board), len(self.board[0])
        self.whiteKingLocation, self.blackKingLocation = (7, 4), (0, 4)
        self.checkmate, self.stalemate = False, False
        self.pins, self.checks = [], []
        self.enPassantPossible = () #coordinates for the square where en-passant is possible
        self.enPassantLog = [(self.enPassantPossible)]
        self.wLRMove, self.wRRMove, self.wKMove, self.bLRMove, self.bRRMove, self.bKMove = False, False, False, False, False, False #flag variable for if piece moved
        self.castleLog = [(self.wLRMove, self.wRRMove, self.wKMove, self.bLRMove, self.bRRMove, self.bKMove)]
        self.boardMaterial = {'wP': 0, 'bP': 0, 'wR': 0, 'bR': 0, 'wN': 0, 'bN': 0, 'wB': 0, 'bB': 0, 'wQ': 0, 'bQ': 0, 'wK': 0, 'bK': 0}

    '''
    Takes a Move as a parameter and executes it. Updates the flag variable for if king or rook moved.
    If move is an enpassant move: store it into enpassant log and store the coordinates where its possible
    If move is a pawn promotion: automatically change the piece to a queen. TO-DO: allow user/AI to select which piece they want to promote to
    If move is a castle move: store it into castle log and move the appropriate rook and king pieces.
    '''
    def makeMove(self, move):

        self.board[move.startSq[0]][move.startSq[1]] = '--'
        self.board[move.endSq[0]][move.endSq[1]] = move.pieceMoved
        self.moveLog.append(move) #store the move, to be displayed later or if user wants to undo
        self.whiteToMove = not self.whiteToMove #white moved, now black's turn to move
        #update king's location if moved
        if move.pieceMoved == 'wK':

            self.whiteKingLocation = (move.endSq[0], move.endSq[1])
            self.wKMove = True

        elif move.pieceMoved == 'bK':

            self.blackKingLocation = (move.endSq[0], move.endSq[1])
            self.bKMove = True

        if move.pieceMoved == 'wR':

            if move.startSq[1] == 0:

                self.wLRMove = True
            
            if move.startSq[1] == 7:
                
                self.wRRMove = True

        elif move.pieceMoved == 'bR':

            if move.startSq[1] == 0:
            
                self.bLRMove = True
                
            if move.startSq[1] == 7:
                
                self.bRRMove = True

        if move.isPawnPromotion:

            # choosePromotionPiece = input("Enter into console promotion piece. Type 'q' for queen, 'r' for rook, 'b' for bishop, 'n' for knight. \n")
            self.board[move.endSq[0]][move.endSq[1]] = move.pieceMoved[0] + 'Q' #choosePromotionPiece.upper()

        if move.isEnpassantMove:

            self.board[move.startSq[0]][move.endSq[1]] = '--'

        if move.pieceMoved[1] == 'P' and abs(move.startSq[0] - move.endSq[0]) == 2:

            self.enPassantPossible = ((move.startSq[0] + move.endSq[0]) // 2, move.endSq[1])

        else:

            self.enPassantPossible = ()

        if move.isCastleMove:

            if move.endSq[1] - move.startSq[1] == 2:

                self.board[move.endSq[0]][move.endSq[1] - 1] = self.board[move.endSq[0]][move.endSq[1] + 1]
                self.board[move.endSq[0]][move.endSq[1] + 1] = '--'

            else:

                self.board[move.endSq[0]][move.endSq[1] + 1] = self.board[move.endSq[0]][move.endSq[1] - 2]
                self.board[move.endSq[0]][move.endSq[1] - 2] = '--'

        self.enPassantLog.append(self.enPassantPossible)
        self.castleLog.append((self.wLRMove, self.wRRMove, self.wKMove, self.bLRMove, self.bRRMove, self.bKMove))
        
    '''
    Returns board back to its previous state by one move if possible
    '''
    def undoMove(self):

        if len(self.moveLog) > 0: #if there exists a move to undo, revert the board back by 1 move

            move = self.moveLog.pop()
            self.board[move.startSq[0]][move.startSq[1]] = move.pieceMoved
            self.board[move.endSq[0]][move.endSq[1]] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove #switch turns back
            #update king's location if moved
            if move.pieceMoved == 'wK':

                self.whiteKingLocation = (move.startSq[0], move.startSq[1])

            elif move.pieceMoved == 'bK':

                self.blackKingLocation = (move.startSq[0], move.startSq[1])

            if move.isEnpassantMove:

                self.board[move.endSq[0]][move.endSq[1]] = '--'
                self.board[move.startSq[0]][move.endSq[1]] = move.pieceCaptured
                self.enPassantPossible = (move.endSq[0], move.endSq[1])

            self.enPassantLog.pop()
            self.enPassantPossible = self.enPassantLog[-1]

            self.castleLog.pop()
            self.wLRMove, self.wRRMove, self.wKMove, self.bLRMove, self.bRRMove, self.bKMove = self.castleLog[-1]

            if move.isCastleMove:
                
                if move.endSq[1] - move.startSq[1] == 2:

                    self.board[move.endSq[0]][move.endSq[1] + 1] = self.board[move.endSq[0]][move.endSq[1] - 1]
                    self.board[move.endSq[0]][move.endSq[1] - 1] = '--'

                else:

                    self.board[move.endSq[0]][move.endSq[1] - 2] = self.board[move.endSq[0]][move.endSq[1] + 1]
                    self.board[move.endSq[0]][move.endSq[1] + 1] = '--'
        
        else:
            
            print('Unable to undo')

    '''
    All moves considering checks
    '''
    def getValidMoves(self):
        
        moves = []
        self.checked, self.pins, self.checks = self.checkForPinsAndChecks()
        #get current turn's king's coordinates
        if self.whiteToMove:

            kingRow, kingCol = self.whiteKingLocation[0], self.whiteKingLocation[1]

        else:

            kingRow, kingCol = self.blackKingLocation[0], self.blackKingLocation[1]

        if self.checked: #if in check

            if len(self.checks) == 1: #only 1 check, must block or move king

                moves = self.getAllPossibleMoves()
                checkRow, checkCol = self.checks[0][0], self.checks[0][1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = [] #list of squares that pieces can move to

                if pieceChecking[1] == 'N': #if checking piece is knight, must capture knight or move king

                    validSquares = [(checkRow, checkCol)]

                else:

                    for scale in range(1, 8):
                        #check all squares between the checking piece and king in the direction of the check
                        validSquare = (kingRow + self.checks[0][2] * scale, kingCol + self.checks[0][3] * scale) 
                        validSquares.append(validSquare)

                        if validSquare[0] == checkRow and validSquare[1] == checkCol: #once we reach the checking piece, stop the loop

                            break
                #for all moves in list, remove the ones that has the king still in check
                #note: when iterating through list and removing elements, better to iterate in reverse
                for move in range(len(moves) - 1, -1, -1):

                    if moves[move].pieceMoved[1] != 'K': #not king, must block check or capture checking piece

                        if not (moves[move].endSq[0], moves[move].endSq[1]) in validSquares:

                            if moves[move].isEnpassantMove:

                                capturedCol = moves[move].endSq[1]
                                capturedRow = moves[move].endSq[0] + 1 if self.whiteToMove else moves[move].endSq[0] - 1

                                if not (capturedRow, capturedCol) in validSquares:

                                    moves.remove(moves[move])
                            
                            else:

                                moves.remove(moves[move])

            else: #more than 1 check, so king must move

                self.getKingMoves(kingRow, kingCol, moves)

        else: #not in check, every move is valid

            moves = self.getAllPossibleMoves()
            self.getCastleMoves(kingRow, kingCol, moves)

        if len(moves) == 0: #no possible moves to make, either checkmate or stalemate

            if self.inCheck():

                self.checkmate = True
                
            else:
                
                self.stalemate = True
        #if 1 side has 1 knight or 1 bishop and no other pieces are on the board besides the kings, then stalemate due to insufficient material
        elif ((self.boardMaterial['wP'] == 0 and self.boardMaterial['bP'] == 0 and self.boardMaterial['wR'] == 0 and self.boardMaterial['bR'] == 0 and
               self.boardMaterial['wQ'] == 0 and self.boardMaterial['bQ'] == 0 and self.boardMaterial['wK'] == 1 and self.boardMaterial['bK'] == 1) and
              ((self.boardMaterial['wN'] == 1 and self.boardMaterial['bN'] == 0 and self.boardMaterial['wB'] == 0 and self.boardMaterial['bB'] == 0) or 
              (self.boardMaterial['wN'] == 0 and self.boardMaterial['bN'] == 1 and self.boardMaterial['wB'] == 0 and self.boardMaterial['bB'] == 0) or
              (self.boardMaterial['wN'] == 0 and self.boardMaterial['bN'] == 0 and self.boardMaterial['wB'] == 1 and self.boardMaterial['bB'] == 0) or
              (self.boardMaterial['wN'] == 0 and self.boardMaterial['bN'] == 0 and self.boardMaterial['wB'] == 0 and self.boardMaterial['bB'] == 1) or
               (self.boardMaterial['wN'] == 0 and self.boardMaterial['bN'] == 0 and self.boardMaterial['wB'] == 0 and self.boardMaterial['bB'] == 0))):

            self.stalemate = True

        else:

            self.checkmate, self.stalemate = False, False
        
        sortedMoves = sorted(moves, key=lambda moves: moves.priorityScore) #sort the moves based on their priority score (captures/pawn promotions are higher prio)
        return sortedMoves

    '''
    If player is in check, returns a list of pins and checks
    '''
    def checkForPinsAndChecks(self):

        pins, checks = [], []
        checked = False
        if self.whiteToMove:

            startRow, startCol = self.whiteKingLocation[0], self.whiteKingLocation[1]
            allyColor, enemyColor = 'w', 'b'

        else:

            startRow, startCol = self.blackKingLocation[0], self.blackKingLocation[1]
            allyColor, enemyColor = 'b', 'w'

        #8 possible directions that can threaten the king
        kingDirections = [(-1, 0), (0, -1), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

        for idx, dir in enumerate(kingDirections):

            possiblePin = () #reset possible pins when looking in new direction

            for scale in range(1, 8):

                endRow, endCol = startRow + dir[0] * scale, startCol + dir[1] * scale #starting from kings location, continue searching in the direction

                if endRow >= 0 and endCol >= 0 and endRow < self.ROWS and endCol < self.COLS: #ensure endRow, endCol in bounds

                    pieceColor = self.board[endRow][endCol][0]
                    piece = self.board[endRow][endCol][1]

                    if pieceColor == allyColor and piece != 'K': #if ally piece

                        if possiblePin == (): #1st piece that could be pinned

                            possiblePin = (endRow, endCol, dir[0], dir[1])

                        else: #more than 1 piece pinned, so king is safe in this direction

                            break

                    elif pieceColor == enemyColor: #if enemy piece
                        #if rook, check adj squares. if bishop, check corners. if enemy white pawn, check bottom corners. if black, check top corners
                        if (piece == 'R' and 0 <= idx <= 3) or (piece == 'B' and 4 <= idx <= idx) or (piece == 'P' and scale == 1 and ((enemyColor == 'w' and
                            6 <= idx <= 7) or (enemyColor == 'b' and 4 <= idx <= 5))) or (piece == 'Q') or (scale == 1 and piece == 'K'):

                            if possiblePin == (): #no pins, so check

                                checked = True
                                checks.append((endRow, endCol, dir[0], dir[1]))
                                break

                            else: #piece pinning, so possible pin

                                pins.append(possiblePin)
                                break

                        else: #no enemy piece can check king in current board state

                            break
        #look for knight checks
        knightDirections = [(-2, -1), (-1, -2), (2, -1), (1, -2), (-2, 1), (-1, 2), (2, 1), (1, 2)]
        for r, c in knightDirections:

            endRow, endCol = startRow + r, startCol + c
            if endRow >= 0 and endCol >= 0 and endRow < self.ROWS and endCol < self.COLS:

                pieceColor = self.board[endRow][endCol][0]
                piece = self.board[endRow][endCol][1]

                if pieceColor == enemyColor and piece == 'N': #if enemy piece is knight, king is in check

                    checked = True
                    checks.append((endRow, endCol, r, c))
         
        return checked, pins, checks

    '''
    Calling helper function to determine if current player's king is under check
    '''
    def inCheck(self):

        if self.whiteToMove:
            
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])

        else:

            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    '''
    Determine if current player turn's square is under attack by enemy piece
    '''
    def squareUnderAttack(self, row, col):

        #swap to other side, get all possible moves from that side, and swap back to original side
        self.whiteToMove = not self.whiteToMove 
        enemyMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove

        for move in enemyMoves:

            if move.endSq[0] == row and move.endSq[1] == col: #if square is under attack, return true, else false

                return True
        
        return False

    '''
    All moves without considering checks
    '''
    def getAllPossibleMoves(self):

        moves = []

        #iterate through whole board, store all possible white or black moves into list
        for row in range(0, self.ROWS):

            for col in range(0, self.COLS):
                
                turn = self.board[row][col][0]

                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):

                    piece = self.board[row][col][1]
                    self.moveFunctions[piece](row, col, moves)

        return moves

    '''
    Get all pawn moves for pawn at (row, col) and store these moves into the list. 
    '''
    def getPawnMoves(self, row, col, moves):

        piecePinned = False
        pinDirection = ()
        #iterate through pins list, if pawn is a pinned piece, then remove it from the list
        for i in range(len(self.pins) - 1, -1, -1):

            if self.pins[i][0] == row and self.pins[i][1] == col:

                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        
        if self.whiteToMove:

            moveAmount = -1
            startRow = 6
            enemyColor = 'b'
            kingRow, kingCol = self.whiteKingLocation

        else:

            moveAmount = 1
            startRow = 1
            enemyColor = 'w'
            kingRow, kingCol = self.blackKingLocation

        self.isPawnPromotion = False

        if self.board[row + moveAmount][col] == '--': #1 square pawn advance

            if not piecePinned or pinDirection == (moveAmount, 0):

                moves.append(Move(5, (row, col), (row + moveAmount, col), self.board))
                
                if row == startRow and self.board[row + (moveAmount * 2)][col] == '--': #if 1 square pawn advance is valid, then check if 2 square pawn advance

                    moves.append(Move(5, (row, col), (row + (moveAmount * 2), col), self.board))

        if col - 1 >= 0: #capture to the left

            if not piecePinned or pinDirection == (moveAmount, -1):

                if self.board[row + moveAmount][col - 1][0] == enemyColor: #enemy piece that can be captured

                    moves.append(Move(2, (row, col), (row + moveAmount, col - 1), self.board))

                if (row + moveAmount, col - 1) == self.enPassantPossible: #if enpassant move, check if it results in king being checked

                    attackingPiece, blockingPiece = False, False

                    if kingRow == row:

                        if kingCol < col: #king is on the left side of the pawn

                            insideRange = range(kingCol + 1, col - 1) #inside: between king and the pawn
                            outsideRange = range(col + 1, 8) #outside: between pawn and the outer border

                        else: #king is on the right side of the pawn

                            insideRange = range(kingCol - 1, col, -1)
                            outsideRange = range(col - 2, -1, -1)

                        for i in insideRange:

                            if self.board[row][i] != '--': #there exists a piece between the king and pawn

                                blockingPiece = True
                                break
                        
                        if not blockingPiece:
                            
                            for i in outsideRange:

                                if self.board[row][i][0] == enemyColor and (self.board[row][i][1] == 'R' or self.board[row][i][1] == 'Q'): 

                                    attackingPiece = True #if enemy queen or rook is on same row as king, then enpassant capture leads to check
                                    break

                                elif self.board[row][i] != '--':

                                    blockingPiece = True
                                    break

                    if not attackingPiece or blockingPiece: #if theres no attacking piece or blocking piece exists, then enpassant is a valid move

                        moves.append(Move(1, (row, col), (row + moveAmount, col - 1), self.board, isEnpassantMove = True))

        if col + 1 < self.COLS: #capture to the right. same logic applies here as left-side capture

            if not piecePinned or pinDirection == (moveAmount, 1):

                if self.board[row + moveAmount][col + 1][0] == enemyColor:

                    moves.append(Move(2, (row, col), (row + moveAmount, col + 1), self.board))

                if (row + moveAmount, col + 1) == self.enPassantPossible:

                    attackingPiece, blockingPiece = False, False

                    if kingRow == row:

                        if kingCol < col:

                            insideRange = range(kingCol + 1, col)
                            outsideRange = range(col + 2, 8)

                        else:

                            insideRange = range(kingCol - 1, col + 1, -1)
                            outsideRange = range(col - 1, -1, -1)

                        for i in insideRange:

                            if self.board[row][i] != '--':

                                blockingPiece = True
                                break
                        
                        if not blockingPiece:
                            
                            for i in outsideRange:

                                if self.board[row][i][0] == enemyColor and (self.board[row][i][1] == 'R' or self.board[row][i][1] == 'Q'):

                                    attackingPiece = True
                                    break

                                elif self.board[row][i] != '--':

                                    blockingPiece = True
                                    break

                    if not attackingPiece or blockingPiece:

                        moves.append(Move(1, (row, col), (row + moveAmount, col + 1), self.board, isEnpassantMove = True))

    '''
    Get all rook moves for rook at (row, col) and store these moves into the list
    '''
    def getRookMoves(self, row, col, moves):

        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):

            if self.pins[i][0] == row and self.pins[i][1] == col:

                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[row][col][1] != 'Q':

                    self.pins.remove(self.pins[i])

                break

        enemyColor = 'b' if self.whiteToMove else 'w'
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)] #up, down, left, right

        for r, c in directions: #look through adjacent cells

            for scale in range(1, 8):

                endRow, endCol = row + r * scale, col + c * scale #takes current (row, col), add each direction up/down/left/right, then scale it
            
                if endRow >= 0 and endCol >= 0 and endRow < self.ROWS and endCol < self.COLS: #ensure that the new row/col is in bounds

                    if not piecePinned or pinDirection == (r, c) or pinDirection == (-r, -c):

                        if self.board[endRow][endCol][0] == enemyColor: #if enemy piece, then capture and cant progress any further

                            moves.append(Move(2, (row, col), (endRow, endCol), self.board))
                            break

                        elif self.board[endRow][endCol] == '--': #empty space, can keep going

                            moves.append(Move(4, (row, col), (endRow, endCol), self.board))

                        else:

                            break    

    '''
    Get all knight moves for knight at (row, col) and store these moves into the list
    '''
    def getKnightMoves(self, row, col, moves):    

        piecePinned = False
        for i in range(len(self.pins) - 1, -1, -1):

            if self.pins[i][0] == row and self.pins[i][1] == col:

                piecePinned = True
                self.pins.remove(self.pins[i])
                break
        
        enemyColor = 'b' if self.whiteToMove else 'w'
        #8 directions: 2left-1up, 1left-2up, 2right-1up, 1right-2up, 2left-1down, 1left-2down, 2right-1down, 1right-2down
        directions = [(-2, -1), (-1, -2), (2, -1), (1, -2), (-2, 1), (-1, 2), (2, 1), (1, 2)]

        for r, c in directions:

            endRow, endCol = row + r, col + c

            if endRow >= 0 and endCol >= 0 and endRow < self.ROWS and endCol < self.COLS: #ensure endRow, endCol in bounds

                if not piecePinned:

                    #since max number of moves are the 8 directions, empty space or capturable enemy piece doesnt matter
                    if self.board[endRow][endCol][0] == enemyColor or self.board[endRow][endCol] == '--':

                        moves.append(Move(3, (row, col), (endRow, endCol), self.board))

    '''
    Get all bishop moves for bishop at (row, col) and store these moves into the list
    '''
    def getBishopMoves(self, row, col, moves):

        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):

            if self.pins[i][0] == row and self.pins[i][1] == col:

                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        
        enemyColor = 'b' if self.whiteToMove else 'w'
        directions = [(-1, -1), (1, 1), (-1, 1), (1, -1)] #4 diagonals: top-left, bot-right, top-right, bot-left

        for r, c in directions:

            for scale in range(1, 8):

                endRow, endCol = row + r * scale, col + c * scale

                if endRow >= 0 and endCol >= 0 and endRow < self.ROWS and endCol < self.COLS: #ensure endRow, endCol in bounds:

                    if not piecePinned or pinDirection == (r, c) or pinDirection == (-r, -c):

                        if self.board[endRow][endCol][0] == enemyColor: #if enemy piece, then capture and cant progress any further

                            moves.append(Move(2, (row, col), (endRow, endCol), self.board))
                            break
                    
                        elif self.board[endRow][endCol] == '--': #if empty space, then can continue in that direction

                            moves.append(Move(3, (row, col), (endRow, endCol), self.board))

                        else:

                            break

    '''
    Get all queen moves for queen at (row, col) and store these moves into the list
    '''
    def getQueenMoves(self, row, col, moves):

        #abstraction: queen moves like rook and bishop, so we can call those functions for the queen's moves
        self.getRookMoves(row, col, moves)
        self.getBishopMoves(row, col, moves)

    '''
    Get all king moves for king at (row, col) and store these moves into the list
    '''
    def getKingMoves(self, row, col, moves):
        
        allyColor = 'w' if self.whiteToMove else 'b'
        enemyColor = 'b' if self.whiteToMove else 'w'
        #8 directions: same as queen, but cant scale
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

        for r, c in directions:

            endRow, endCol =  row + r, col + c #every direction
                
            if endRow >= 0 and endCol >= 0 and endRow < self.ROWS and endCol < self.COLS: #ensure endRow, endCol in bounds

                if self.board[endRow][endCol][0] == enemyColor or self.board[endRow][endCol] == '--': #same logic applies as the knight

                    if allyColor == 'w':

                        self.whiteKingLocation = (endRow, endCol)

                    else:

                        self.blackKingLocation = (endRow, endCol)

                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:

                        moves.append(Move(5, (row, col), (endRow, endCol), self.board))

                    if allyColor == 'w':

                        self.whiteKingLocation = (row, col)

                    else:

                        self.blackKingLocation = (row, col)

    '''
    Generates all valid castle moves for the king at (row, col) and add them to the list of moves.
    '''
    def getCastleMoves(self, row, col, moves):

        if self.squareUnderAttack(row, col):

            return #cant castle if king is in check
        #if white / black's turn and left rook / king hasnt moved yet.
        if (self.whiteToMove and self.wLRMove == False and self.wKMove == False and self.board[7][0]) == 'wR' or (
            not self.whiteToMove and self.bLRMove == False and self.bKMove == False and self.board[0][0] == 'bR'):
            #if all 1, 2, and 3 squares to the left of the king isnt under attack, then castle queen side is valid
            if self.board[row][col - 1] == '--' and self.board[row][col - 2] == '--' and self.board[row][col - 3] == '--':

                if not self.squareUnderAttack(row, col - 1) and not self.squareUnderAttack(row, col - 2):

                    moves.append(Move(2, (row, col), (row, col - 2), self.board, isCastleMove = True))
        #if white / black's turn and right rook / king hasnt moved yet
        if (self.whiteToMove and self.wRRMove == False and self.wKMove == False and self.board[7][7] == 'wR') or (
            not self.whiteToMove and self.bRRMove == False and self.bKMove == False and self.board[0][7] == 'bR'):
            #if 1 and 2 squares to the right of the king isnt under attack, then castle king side is valid
            if self.board[row][col + 1] == '--' and self.board[row][col + 2] == '--':

                if not self.squareUnderAttack(row, col + 1) and not self.squareUnderAttack(row, col + 2):

                    moves.append(Move(2, (row, col), (row, col + 2), self.board, isCastleMove = True))
    
    '''
    Updates the count of all pieces remaining on the current board
    '''
    def getBoardMaterial(self):

        self.boardMaterial = {piece: 0 for piece in self.boardMaterial}

        for row in range(0, self.ROWS):

            for col in range(0, self.COLS):

                if self.board[row][col] != '--':
                
                    self.boardMaterial[self.board[row][col]] += 1

'''
Stores all information regarding a given move.
'''
class Move():
    #Maps the board's (row, col) notation into proper chess notation. 
    #(In chess, rows go from 1-8 from bottom to top and cols go from a-h from left to right)
    ranksToRows = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}
    rowsToRanks = {values: keys for keys, values in ranksToRows.items()}
    colsToFiles = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h'}
    filesToCols = {values: keys for keys, values in colsToFiles.items()}

    def __init__(self, priorityScore, startSq, endSq, board, isEnpassantMove = False, isCastleMove = False):

        self.priorityScore = priorityScore #Lower score is higher priority
        self.startSq = startSq
        self.endSq = endSq
        self.pieceMoved = board[self.startSq[0]][self.startSq[1]]
        self.pieceCaptured = board[self.endSq[0]][self.endSq[1]]
        #True if white or black pawn reaches opposite side of the board, false otherwise
        self.isPawnPromotion = (self.pieceMoved == 'wP' and self.endSq[0] == 0) or (self.pieceMoved == 'bP' and self.endSq[0] == 7)
        self.isEnpassantMove = isEnpassantMove #true if en passant is possible, else false
        if self.isEnpassantMove: #if move is an enpassant move, then the piececaptured will be '--', so we have to manually set it to 'wP' or 'bP'

            self.pieceCaptured = 'bP' if self.pieceMoved == 'wP' else 'wP'

        self.isCastleMove = isCastleMove #castle move
        self.moveID = self.startSq[0] * 1000 + self.startSq[1] * 100 + self.endSq[0] * 10 + self.endSq[1] #Unique moveID, similar to hashfunction

    '''
    Overriding the equals method
    '''
    def __eq__(self, other):

        if isinstance(other, Move): #ensures that the two objects being compared are Move objects

            return self.moveID == other.moveID

        return False

    '''
    Returns the chess notation for starting (row,col) and end (row,col) as seen in chess. TO-DO: Check/mate moves
    '''
    #To Do: add additional notation for castle, en passant, check, etc
    def getChessNotation(self):

        if self.pieceMoved == 'wP' or self.pieceMoved == 'bP': #if pawn move

            if self.pieceCaptured != '--': #return starting file, x if piece captured, ending rank + file, =P if pawn promotion

                return self.getRankFile(self.startSq[0], self.startSq[1])[0] + 'x' + self.getRankFile(self.endSq[0], self.endSq[1]) + '=P' if \
                self.isPawnPromotion else self.getRankFile(self.startSq[0], self.startSq[1])[0] + 'x' + self.getRankFile(self.endSq[0], self.endSq[1])

            elif self.isPawnPromotion: #pawn promotion but no capture

                return self.getRankFile(self.endSq[0], self.endSq[1]) + '=P'

            else: #standard pawn move, return end file and rank

                return self.getRankFile(self.endSq[0], self.endSq[1])

        elif self.isCastleMove: #castle move, return 'O-O' if king side, 'O-O-O' if queen side
                
            return 'O-O' if self.endSq[1] == 6 else 'O-O-O'

        else: #piece is not a pawn, return the piece + x if piece captured + end file and rank

            if self.pieceCaptured != '--': 

                return self.pieceMoved[1] + 'x' + self.getRankFile(self.endSq[0], self.endSq[1])
            
            else:

                return self.pieceMoved[1] + self.getRankFile(self.endSq[0], self.endSq[1])
            
    '''
    Returns the chess notation for current coordinate
    '''
    def getRankFile(self, row, col):

        return self.colsToFiles[col] + self.rowsToRanks[row]