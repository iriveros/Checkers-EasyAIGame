# [[file:checker.org::*questions][questions:1]]
# !/usr/bin/env python3


#################################################################################################################
# Ivan Riveros													#
# Project 1 for CAP4630												#
# Date: 6/17/2022												#
# Description:													#
# Implemented functions: make_move(self,pos); lose(self), is_over(self) and scoring(self).			#
# Modified functions: possible_moves_on_white_turn(self), possible_moves_on_black_turn(self), show(self)	#
#################################################################################################################


from easyAI import TwoPlayerGame, Human_Player, AI_Player, Negamax
from easyAI import solve_with_iterative_deepening
import numpy as np

# black_square
even = [0,2,4,6] #Just Even Numbers
odd = [1,3,5,7]  #Just Odd Numbers

# init
even_row = [(i,j) for i in even for j in odd] #This defines the black tiles for every even row
odd_row = [(i,j) for i in odd for j in even]  #This defines the white tiles for every odd row

black_squares = even_row + odd_row #Combine the two arrays into one

class Checker(TwoPlayerGame):

    def __init__(self, players):
        self.players = players
        # self.board = np.arange(8 * 8).reshape(8,8)
        self.blank_board = np.zeros((8,8), dtype=object) #defines a black 8x8 matrix
        self.board = self.blank_board.copy()
        self.black_pieces = [				 #starting locations for black pieces
            (0,1), (0,3), (0,5), (0,7),
            (1,0), (1,2), (1,4), (1,6)
        ]
        self.white_pieces = [				#Starting locations for white pieces
            (6,1), (6,3), (6,5), (6,7),
            (7,0), (7,2), (7,4), (7,6)
        ]
        for i,j in self.black_pieces:			#Setting starting black piece locations to B 
            self.board[i,j] = "B"
        for i,j in self.white_pieces:			#Setting starting white piece locations to W
            self.board[i,j] = "W"

        self.white_territory = [(7,0), (7,2), (7,4), (7,6)]	#Defining last row for white
        self.black_territory = [(0,1), (0,3), (0,5), (0,7)]	#Defining last row for black 


        self.players[0].pos = self.white_pieces			#Setting starting locations for player one with white pieces
        self.players[1].pos = self.black_pieces			#Setting starting locations for player two with black pieces

        self.current_player = 1  # player 1 starts. 

    def possible_moves_on_white_turn(self):

        table_pos = []
        old_new_piece_pos = []

        # board position before move
        board = self.blank_board.copy()
        for (p,l) in zip(self.players, ["W", "B"]):		#zip() makes tuple from lists (iterables), here it makes a tuple = {(Players[1],W), (Players[2],B)}
            for x,y in p.pos:					#Creates the board based on current positions of players, in similar way as constructor.
                board[x,y] = l

        # get legal move of each pieces. (old piece location, new piece location)
        # get position of each move (list of all table position)
        for v in self.players[self.current_player-1].pos:	#current_player is an int of the "current player". Values are 1 or 2. This iterates over all pieces.
            old_piece_pos = v

            step_pos = [(v[0]-1, v[1]-1), (v[0]-1, v[1]+1)]	#Bcuz white starts at row 7, subtract from index X to go "forward", and either add or subtract from Y index to go left or right.
            # if no piece at step_pos, step
            # otherwise jump until no piece at next step_pos
            for n in step_pos:
                if (n[0] >= 0 and n[0] <= 7) and (n[1] >= 0 and n[1] <= 7) and (n in black_squares): #if potential piece position is within the board and on a black square
                    if ((board[n[0], n[1]] in ["B","W"]) and (board[n[0], n[1]] != ["W","B"][self.current_player-1])): #if position has a B or W piece already and piece is not of player:
                        y = ((n[0] - old_piece_pos[0]) * 2) + old_piece_pos[0]			     		#New X pos = (x - x_old) * 2 + x_old. If x_old = 7, then ""y"" will equal 5. Naming is strange...
                        x = ((n[1] - old_piece_pos[1]) * 2) + old_piece_pos[1]					#New Y pos = (y - y_old) * 2 + y_old. If y_old = 0, then ""x"" will equal either 2 or -2. This is jumping over a piece
                        j = (y,x)										#New coordinates of piece, after jumping.
                        is_inside_board = (j[0] >= 0 and j[0] <= 7) and (j[1] >= 0 and j[1] <= 7)		#If new coords are in the board, record to bool
                        if (j[0] <= 7) and (j[1] <=7):								#If new coords are within upper boundaries of board
                            is_position_empty = (board[j[0], j[1]] == 0)						#Make bool for if board at new position has no piece on it
                        else:											#Else, board is not within upper bounds, say position is not empty so piece is not moved to this position
                            is_position_empty = False
                        if is_inside_board and (j in black_squares) and is_position_empty:			#If new piece coords are within board, within black squares, and position is empty: record new position.
                            # print(old_piece_pos,j)									#Otherwise, try to move in other direction bcuz only 1 jump is allowed. Or do not record change as no move is possible
                            old_new_piece_pos.append((old_piece_pos,j))
                    elif(not (board[n[0], n[1]] in ["B","W"])):							#if position does not have a B or W piece, move piece to that position, no jumping needed.
#                        print(n)
                        old_new_piece_pos.append((old_piece_pos,n))

        # board position after  move
        for i,j in old_new_piece_pos:									#Update a copy board to apply piece movement.
#            print(f"i = {i}")
            b = board.copy()
            b[i[0], i[1]] = 0 # old position
            b[j[0], j[1]] = "W" # new position
            # print(b)
            table_pos.append(b)										#Record of boards with possible moves.
            assert len(np.where(b != 0)[0]) == 16, f"In possible_moves_on_white_turn(), there are {len(np.where(b != 0)[0])} pieces on the board  \n {b}" #Write how many pieces are on the board??


        self.board = board										#board is updated with pieces prior to movement
        return table_pos										#Array of all possible movements for all pieces

    def possible_moves_on_black_turn(self):
        table_pos = []
        old_new_piece_pos = []

        # board position before move
        board = self.blank_board.copy()
        for (p,l) in zip(self.players, ["W", "B"]):
            for x,y in p.pos:
                board[x,y] = l

        # get legal move of each pieces. (old piece location, new piece location)
        # get position of each move (list of all table position)
        for v in self.players[self.current_player-1].pos:						#Identical to white, but pieces move in positive x to move "forward"
            old_piece_pos = v

            step_pos = [(v[0]+1, v[1]-1), (v[0]+1, v[1]+1)]
            # if no piece at step_pos, step
            # otherwise jump until no piece at next step_pos
            for n in step_pos:
                if (n[0] >= 0 and n[0] <= 7) and (n[1] >= 0 and n[1] <= 7) and (n in black_squares):
                    if ((board[n[0], n[1]] in ["B","W"]) and (board[n[0], n[1]] != ["W","B"][self.current_player-1])):
                        y = ((n[0] - old_piece_pos[0]) * 2) + old_piece_pos[0]
                        x = ((n[1] - old_piece_pos[1]) * 2) + old_piece_pos[1]
                        j = (y,x)
                        is_inside_board = (j[0] >= 0 and j[0] <= 7) and (j[1] >= 0 and j[1] <= 7)
                        if (j[0] <= 7) and (j[1] <=7):
                            is_position_empty = (board[j[0], j[1]] == 0)
                        else:
                            is_position_empty = False
                        if is_inside_board and (j in black_squares) and is_position_empty:
                            # print(old_piece_pos,j)
                            old_new_piece_pos.append((old_piece_pos,j))
                    elif(not (board[n[0], n[1]] in ["B","W"])): 
                        old_new_piece_pos.append((old_piece_pos,n))

        # board position after  move

        for i,j in old_new_piece_pos:
            b = board.copy()
            b[i[0], i[1]] = 0
            b[j[0], j[1]] = "B"
            table_pos.append(b)
            assert len(np.where(b != 0)[0]) == 16, f"In possible_moves_on_black_turn(), there are {len(np.where(b != 0)[0])} pieces on the board  \n {b}"

        self.board = board
        return table_pos

    def possible_moves(self):
        """
        """

        if self.current_player == 2:
            return self.possible_moves_on_black_turn()				#Get black piece moves b/c player 2 uses black pieces
        else:
            return self.possible_moves_on_white_turn()				#Same but for player 1 with white pieces

    def get_piece_pos_from_table(self, table_pos):				#Gets all positions with pieces for current player
        if self.current_player-1 == 0:
            x = np.where(table_pos == "W")
        elif self.current_player-1 == 1:
            x = np.where(table_pos == "B")
        else:
            raise ValueError("There can be at most 2 players.")

        assert len(np.where(table_pos != 0)[0]) == 16, f"In get_piece_pos_from_table(), there are {len(np.where(table_pos != 0)[0])} pieces on the board  \n {table_pos}"
        return [(i,j) for i,j in zip(x[0], x[1])]

    def make_move(self, pos):
        """
        assign pieces index of pos array to current player position.
        parameters
        -------
        pos = position of all pieces on the (8 x 8) boards. type numpy array.
        example of pos
        [[0,B,0,B,0,B,0,B],
         [B,0,B,0,B,0,B,0],
         [0,0,0,0,0,0,0,0],
         [0,0,0,0,0,0,0,0],
         [0,0,0,0,0,0,0,0],
         [0,W,0,W,0,W,0,W],
         [W,0,W,0,W,0,W,0]]
        ------
        """
        newpos = [(i,j) for i in range(8) for j in range(8) if pos[i,j] == ["W","B"][self.current_player - 1]] #Make array of tuples with positions of respective piece for current player
        self.players[self.current_player - 1].pos = newpos #Update positions of piece with array.
        pass

    def lose(self):
        """
        black lose if white piece is in black territory
        white lose if black piece is in black territory ?? white territory**
        """
        if(self.current_player == 2):
            in_territory = any(p in self.players[0].pos for p in self.black_territory) #Check if player 1 is in territory of player 2.
            return in_territory
        else:
            in_territory = any(p in self.players[1].pos for p in self.white_territory) #Check if player 2 is in territory of player 1
            return in_territory
        pass

    def is_over(self):
        """
        game is over immediately when one player get one of its piece into opponent's territory.
        """
        return (self.possible_moves() == []) or self.lose()	#If opponent has piece in current player's territory, or no more moves are possble, end game.
        pass

    def show(self):
        """
        show 8*8 checker board.
        """

        # board position before move
        board = self.blank_board.copy()
#        print(f"player 1 positions = {self.players[0].pos}")
#        print(f"player 2 positions = {self.players[1].pos}")
        for (p,l) in zip(self.players, ["W", "B"]):
            for x,y in p.pos:
                board[x,y] = l
        print('\n')
        for x in range(8):				#Instead of printing the board in Numpy format, print it to look a bit nicer so its easier to follow.
            for y in range(8):
                print(f"{board[x,y]} ", end ="")
            print("")
#        print(board)

    def scoring(self):
       """
       win = 0
       lose = -100
       """
       return -100 if self.lose() else 0		#If loses
       pass

if __name__ == "__main__":
    ai = Negamax(1) # The AI will think 13 moves in advance
    game = Checker( [ AI_Player(ai), AI_Player(ai) ] )
    history = game.play()
# questions:1 ends here
