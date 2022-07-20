'''
This class handles the AI moves.
'''
import numpy as np
#Evaluation scores taken from https://www.chessprogramming.org/Simplified_Evaluation_Function
pieceScore = {'K': 20000, 'Q': 900, 'R': 500, 'N': 320, 'B': 330, 'P': 100}
#Board evaluations for each piece are given for white side, mirrored for black side
pawnScores = [[ 0,  0,  0,  0,  0,  0,  0,  0],
              [50, 50, 50, 50, 50, 50, 50, 50], 
              [10, 10, 20, 30, 30, 20, 10, 10], 
              [ 5,  5, 10, 25, 25, 10,  5,  5], 
              [ 0,  0,  0, 20, 20,  0,  0,  0], 
              [ 5, -5,-10,  0,  0,-10, -5, -5], 
              [ 5, 10, 10,-20,-20, 10, 10,  5], 
              [ 0,  0,  0,  0,  0,  0,  0,  0]]

rookScores = [[ 0,  0,  0,  0,  0,  0,  0,  0],
              [ 5, 10, 10, 10, 10, 10, 10, 10], 
              [-5,  0,  0,  0,  0,  0,  0,  0], 
              [-5,  0,  0,  0,  0,  0,  0,  0], 
              [-5,  0,  0,  0,  0,  0,  0,  0], 
              [-5,  0,  0,  0,  0,  0,  0,  0], 
              [-5,  0,  0,  0,  0,  0,  0,  0], 
              [ 0,  0,  0,  5,  5,  0,  0,  0]]

knightScores = [[-50,-40,-30,-30,-30,-30,-40,-50],
                [-40,-20,  0,  0,  0,  0,-20,-40], 
                [-30, 0 , 10, 15, 15, 10,  0,-30], 
                [-30,  5, 15, 20, 20, 15,  5,-30], 
                [-30,  5, 15, 20, 20, 15,  5,-30], 
                [-30, 0 , 10, 15, 15, 10,  0,-30], 
                [-40,-20,  0,  0,  0,  0,-20,-40],
                [-50,-40,-30,-30,-30,-30,-40,-50]]

bishopScores = [[-20,-10,-10,-10,-10,-10,-10,-20],
                [-10,  0,  0,  0,  0,  0,  0,-10], 
                [-10,  0,  5, 10, 10,  5,  0,-10], 
                [-10,  5,  5, 10, 10,  5,  5,-10], 
                [-10,  0, 10, 10, 10, 10,  0,-10], 
                [-10, 10, 10, 10, 10, 10, 10,-10], 
                [-10,  5,  0,  0,  0,  0,  5,-10], 
                [-20,-10,-10,-10,-10,-10,-10,-20]]

queenScores = [[-20,-10,-10, -5, -5,-10,-10,-20],
               [-10,  0,  0,  0,  0,  0,  0,-10], 
               [-10,  0,  5,  5,  5,  5,  0,-10], 
               [ -5,  0,  5,  5,  5,  5,  0, -5], 
               [  0,  0,  5,  5,  5,  5,  0, -5], 
               [-10,  0,  5,  5,  5,  5,  0,-10], 
               [-10,  0,  5,  0,  0,  0,  0,-10], 
               [-20,-10,-10, -5, -5,-10,-10,-20]]

kingScores = [[-30,-40,-40,-50,-50,-40,-40,-30],
              [-30,-40,-40,-50,-50,-40,-40,-30], 
              [-30,-40,-40,-50,-50,-40,-40,-30], 
              [-30,-40,-40,-50,-50,-40,-40,-30],
              [-20,-30,-30,-40,-40,-30,-30,-20],
              [-10,-20,-20,-20,-20,-20,-20,-10],
              [ 20, 20,  0,  0,  0,  0, 20, 20],
              [ 20, 30, 10,  0,  0, 10, 30, 20]]

endGameKingScores = [[-50,-40,-30,-20,-20,-30,-40,-50],
                     [-30,-20,-10,  0,  0,-10,-20,-30], 
                     [-30,-10, 20, 30, 30, 20,-10,-30], 
                     [-30,-10, 30, 40, 40, 30,-10,-30],
                     [-30,-10, 30, 40, 40, 30,-10,-30],
                     [-30,-10, 20, 30, 30, 20,-10,-30], 
                     [-30,-30,  0,  0,  0,  0,-30,-30], 
                     [-50,-30,-30,-30,-30,-30,-30,-50]]

piecePositionScores = {'wP': pawnScores, 'bP': np.flip(pawnScores), 'wR': rookScores, 'bR': np.flip(rookScores), 'wN': knightScores, 'bN': np.flip(knightScores), 
                       'wB': bishopScores, 'bB': np.flip(bishopScores), 'wQ': queenScores, 'bQ': np.flip(queenScores), 'wK': kingScores, 'bK': np.flip(kingScores),
                       'endGameWK': endGameKingScores, 'endGameBK': np.flip(endGameKingScores)} #flip the values if black piece

CHECKMATE = 60000 #must be greater 9Q's + 1K. Since if both sides promotes all pawns to queens, board score must be < 60000
STALEMATE = 0
DEPTH = 4 #how far deep we want to look for best move

'''
Looks through every valid move in the current game state for current side's turn. Finds the 'best' move based on board score, and returns it.
'''
def findBestMove(gameState, validMoves):

    turnMultiplier = 1 if gameState.whiteToMove else -1 #If white, we want highest positive score. if black, we want highest negative score
    maxScore = -CHECKMATE #start at the lowest possible score

    #iterate through validMoves, make the move, return move if checkmate. else, get board score, and if highest score, set it as our new best move. undo the move
    for AImove in validMoves:

        gameState.makeMove(AImove)

        if gameState.checkmate:

            return AImove

        elif gameState.stalemate:

            score = STALEMATE

        else:

            score = turnMultiplier * boardScore(gameState)

        if score > maxScore:

            maxScore = score
            bestMove = AImove

        gameState.undoMove()

    return bestMove

'''
Calls a helper function to get the best valid move and adds it to the return queue.
'''
def findBestNegaMaxAlphaBetaMove(gameState, validMoves, returnQueue):

    global nextMove
    nextMove = None
    findNegaMaxAlphaBetaMove(gameState, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gameState.whiteToMove else -1)
    returnQueue.put(nextMove)

'''
Uses nega-max algorithm to recursively find the best possible move at certain depth. For each valid move, find the opponents valid moves and get their
best valid move. Includes alpha-beta pruning to improve search efficiency so we don't need to search through the unneccesary subtrees if there exists a 
subtree that contains a better move for opponent.
'''
def findNegaMaxAlphaBetaMove(gameState, validMoves, depth, alpha, beta, turnMultiplier):

    global nextMove
    if depth == 0:
        
        return turnMultiplier * boardScore(gameState) #once we reach the max depth, evaluate the board state and return it (white wants +score, black -score)

    maxScore = -CHECKMATE #start at the lowest possible score
    for move in validMoves:

        gameState.makeMove(move)
        nextMoves = gameState.getValidMoves()
        #recursive call on next validmoves, go down another depth. now its the other players turn, so we negate our values
        score = -findNegaMaxAlphaBetaMove(gameState, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier)
        if score > maxScore: #if found new max score, update it

            maxScore = score
            if depth == DEPTH: #if reach max depth, then we found new best move

                nextMove = move

        gameState.undoMove()
        if maxScore > alpha:

            alpha = maxScore

        if alpha >= beta: #if we already found a move thats better than current move, then dont need to search down this subtree

            break

    if gameState.stalemate:

        maxScore = 0

    return maxScore
'''
Evaluates the current board. Positive score is better for white. Negative score is better for black.
'''
def boardScore(gameState):
    #If there are no more queens or one side has no rooks, then scale is set to 2
    scale = 2 if (gameState.boardMaterial['wQ'] == 0 and gameState.boardMaterial['bQ'] == 0 and
                 (gameState.boardMaterial['wR'] == 0 or gameState.boardMaterial['bR'] == 0)) else 1
    
    if gameState.checkmate:

        if gameState.whiteToMove:

            return -CHECKMATE #Black wins

        else:

            return CHECKMATE #White wins

    elif gameState.stalemate:

        return STALEMATE #Tie

    score = 0
    #Iterate through entire board
    for row in range(0, gameState.ROWS):

        for col in range(0, gameState.COLS):

            square = gameState.board[row][col]

            if square[1] != '--':

                if square[1] == 'K':
                    #If piece is a king and no more queens on board, use endgame king positional scores
                    if gameState.boardMaterial['wQ'] == 0 and gameState.boardMaterial['bQ'] == 0:

                        if square[0] == 'w':

                            score += (pieceScore[square[1]] + piecePositionScores['endGameWK'][row][col])

                        elif square[0] == 'b':

                            score -= (pieceScore[square[1]] + piecePositionScores['endGameBK'][row][col])

                    else:

                        if square[0] == 'w':

                            score += pieceScore[square[1]]

                        elif square[0] == 'b':

                            score -= pieceScore[square[1]]

                elif square[1] != 'K':

                    if square[0] == 'w':

                        score += (pieceScore[square[1]] + piecePositionScores[square][row][col] * scale)

                    elif square[0] == 'b':

                        score -= (pieceScore[square[1]] + piecePositionScores[square][row][col] * scale)

    return score