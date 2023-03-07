from enum import Enum
import random
from copy import deepcopy
import re

#maps the  indeces 0-53 to the given cube location, a tuple of (piece_type<'edge','corner'>, index<0-12>, pos<0,1,2>)
# also maps the other way. Useful for converting between representations. Note: indeces 4, 13, 22, 31, 40, and 49 are centers,
# and thus are not included in this map because they are represented in the serial string, but not the cube object.
serial_cube_index_map = {2*9 + 1:('edge',0,0),('edge',0,0):2*9 + 1,7:('edge',0,1),('edge',0,1):7,2*9 + 5:('edge',1,0),('edge',1,0):2*9 + 5,3*9 + 3:('edge',1,1),('edge',1,1):3*9 + 3,2*9 + 7:('edge',2,0),('edge',2,0):2*9 + 7,5*9 + 1:('edge',2,1),('edge',2,1):5*9 + 1,2*9 + 3:('edge',3,0),('edge',3,0):2*9 + 3,1*9 + 5:('edge',3,1),('edge',3,1):1*9 + 5,1*9 + 1:('edge',4,0),('edge',4,0):1*9 + 1,3:('edge',4,1),('edge',4,1):3,5:('edge',5,0),('edge',5,0):5,3*9 + 1:('edge',5,1),('edge',5,1):3*9 + 1,3*9 + 7:('edge',6,0),('edge',6,0):3*9 + 7,5*9 + 5:('edge',6,1),('edge',6,1):5*9 + 5,5*9 + 3:('edge',7,0),('edge',7,0):5*9 + 3,1*9 + 7:('edge',7,1),('edge',7,1):1*9 + 7,4*9 + 1:('edge',8,0),('edge',8,0):4*9 + 1,1:('edge',8,1),('edge',8,1):1,4*9 + 5:('edge',9,0),('edge',9,0):4*9 + 5,1*9 + 3:('edge',9,1),('edge',9,1):1*9 + 3,4*9 + 7:('edge',10,0),('edge',10,0):4*9 + 7,5*9 + 7:('edge',10,1),('edge',10,1):5*9 + 7,4*9 + 3:('edge',11,0),('edge',11,0):4*9 + 3,3*9 + 5:('edge',11,1),('edge',11,1):3*9 + 5,2*9 + 2:('corner',0,0),('corner',0,0):2*9 + 2,8:('corner',0,1),('corner',0,1):8,3*9 + 0:('corner',0,2),('corner',0,2):3*9 + 0,2*9 + 8:('corner',1,0),('corner',1,0):2*9 + 8,3*9 + 6:('corner',1,1),('corner',1,1):3*9 + 6,5*9 + 2:('corner',1,2),('corner',1,2):5*9 + 2,2*9 + 6:('corner',2,0),('corner',2,0):2*9 + 6,5*9 + 0:('corner',2,1),('corner',2,1):5*9 + 0,1*9 + 8:('corner',2,2),('corner',2,2):1*9 + 8,2*9 + 0:('corner',3,0),('corner',3,0):2*9 + 0,1*9 + 2:('corner',3,1),('corner',3,1):1*9 + 2,6:('corner',3,2),('corner',3,2):6,4*9 + 2:('corner',4,0),('corner',4,0):4*9 + 2,0:('corner',4,1),('corner',4,1):0,1*9 + 0:('corner',4,2),('corner',4,2):1*9 + 0,4*9 + 8:('corner',5,0),('corner',5,0):4*9 + 8,1*9 + 6:('corner',5,1),('corner',5,1):1*9 + 6,5*9 + 6:('corner',5,2),('corner',5,2):5*9 + 6,4*9 + 6:('corner',6,0),('corner',6,0):4*9 + 6,5*9 + 8:('corner',6,1),('corner',6,1):5*9 + 8,3*9 + 8:('corner',6,2),('corner',6,2):3*9 + 8,4*9 + 0:('corner',7,0),('corner',7,0):4*9 + 0,3*9 + 2:('corner',7,1),('corner',7,1):3*9 + 2,2:('corner',7,2),('corner',7,2):2}

#The Color enum defines the six colors of the cube to use for the internal representation. 
# Note: Even if the colors differ from the physical cube, this does not matter
# since this only defines the internal representation, and the real colors of the
# cube do not matter for the representation. Moves and their outputs will be the same
# regardless.
class Color(Enum):
    WHITE = 0
    GREEN = 1
    ORANGE = 2
    YELLOW = 3
    BLUE = 4
    RED = 5

    def getOppositeColor(color):
        if color == Color.WHITE:
            return Color.YELLOW
        elif color == Color.YELLOW:
            return Color.WHITE
        elif color == Color.BLUE:
            return Color.GREEN
        elif color == Color.GREEN:
            return Color.BLUE
        elif color == Color.RED:
            return Color.ORANGE
        else:#color == Color.ORANGE
            return Color.RED
    def convertToString(color):
        if color == Color.WHITE:
            return 'w'
        elif color == Color.YELLOW:
            return 'y'
        elif color == Color.BLUE:
            return 'b'
        elif color == Color.GREEN:
            return 'g'
        elif color == Color.RED:
            return 'r'
        else:#color == Color.ORANGE
            return 'o'

#Edge defines an edge on the cube. It has two stickers (different colors) 
# and an orientation defined by their order
class Edge:
    def __init__(self, color1, color2) -> None:
        self.colors = (color1, color2)
    def flip(self):
        self.colors = (self.colors[1], self.colors[0])
        return self

#Corner defines a corner of the cube. It has three stickers, and can be
# in three rotations.
class Corner:
    def __init__(self, color1, color2, color3):
        self.colors = (color1, color2, color3)
    def rotateClockwise(self):
        self.colors = ( self.colors[2], self.colors[0], self.colors[1] )
        return self
    def rotateCounterclockwise(self):
        self.colors = ( self.colors[1], self.colors[2], self.colors[0] )
        return self

#Cube defines a rubik's cube object. It is made of 12 edges and 8 corners.
class Cube():
    #The cube is made of 12 edges and 8 corners. The constructor, by default
    # makes a solved cube, but it can take an array of stickers if needed.
    #
    # If stickers are provided, they must be in a list 54 big of the following form,
    # where each location contains a comperable value to others (can test for
    # equality), hashable,  and only six distict values exist. Can use Color enum from this file,
    # but do not have to:
    #         ----------
    #         |0 |1 |2 |
    #         ----------
    #         |3 |4 |5 | <- F
    #         ----------
    #         |6 |7 |8 |
    #         ----------
    #-------------------------------------
    #|9 |10|11|18|19|20|27|28|29|36|37|38|
    #-------------------------------------
    #|12|13|14|21|22|23|30|31|32|39|40|41| <- U
    #-------------------------------------
    #|15|16|17|24|25|26|33|34|35|42|43|44|
    #-------------------------------------
    #         ----------
    #         |45|46|47|
    #         ----------
    #         |48|49|50| <- B
    #         ----------
    #         |51|52|53|
    #         ----------

    def __init__(self, stickers: list=None):
        self.edges = []
        self.corners = []

        if not stickers:
            #create a standard solved cube
            #add standard 12 edges
            self.edges += [Edge(Color.WHITE, Color.ORANGE), Edge(Color.WHITE, Color.BLUE), Edge(Color.WHITE, Color.RED), Edge(Color.WHITE, Color.GREEN),\
                        Edge(Color.GREEN, Color.ORANGE), Edge(Color.ORANGE, Color.BLUE), Edge(Color.BLUE, Color.RED), Edge(Color.RED, Color.GREEN),\
                        Edge(Color.YELLOW, Color.ORANGE), Edge(Color.YELLOW, Color.GREEN), Edge(Color.YELLOW, Color.RED), Edge(Color.YELLOW, Color.BLUE)]

            #add standard 8 corners
            self.corners += [Corner(Color.WHITE, Color.ORANGE, Color.BLUE), Corner(Color.WHITE, Color.BLUE, Color.RED), Corner(Color.WHITE, Color.RED, Color.GREEN),\
                            Corner(Color.WHITE, Color.GREEN, Color.ORANGE), Corner(Color.YELLOW, Color.ORANGE, Color.GREEN), Corner(Color.YELLOW, Color.GREEN, Color.RED),\
                            Corner(Color.YELLOW, Color.RED, Color.BLUE), Corner(Color.YELLOW, Color.BLUE, Color.ORANGE)]
        else:#stickers provided
            assert(len(stickers) == 54)#make sure all the stickers are provided
            color_map = {} #a dictionary from all six encountered values to the Color enum

            #these indeces represent the six centers, so should always be unique and enumerate the six colors of the cube
            color_map[stickers[4]] = Color.ORANGE
            color_map[stickers[13]] = Color.GREEN
            color_map[stickers[22]] = Color.WHITE
            color_map[stickers[31]] = Color.BLUE
            color_map[stickers[40]] = Color.YELLOW
            color_map[stickers[49]] = Color.RED
            
            #convert whatever form the sticker array came in as to Color enums
            stickers = list(map(color_map.get, stickers))

            for edge_num in range(12):
                #get the indeces in stickers, put the edge in self.edges
                color1 = stickers[serial_cube_index_map[('edge', edge_num, 0)]]
                color2 = stickers[serial_cube_index_map[('edge', edge_num, 1)]]
                assert(color1 in Color and color2 in Color)#make sure they are valid colors
                self.edges.append(Edge(color1, color2))
            for corner_num in range(8):
                #get the indeces in stickers, put the corner in self.corners
                color1 = stickers[serial_cube_index_map[('corner', corner_num, 0)]]
                color2 = stickers[serial_cube_index_map[('corner', corner_num, 1)]]
                color3 = stickers[serial_cube_index_map[('corner', corner_num, 2)]]
                assert(color1 in Color and color2 in Color and color3 in Color)#make sure they are valid colors
                self.corners.append(Corner(color1, color2, color3))

    #this function takes a goal cube which must be a valid cube, mapps the pieces of itself to the goal cube,
    # and returns it. This is useful for "solving" a cube into a specific scramble (goal_cube) since it allows
    # any solving algorithm to believe it is solving the cube normally, and give a string to achieve a 
    # specific scramble.
    def map_to_goal(self, goal_cube):
        mapped_cube = deepcopy(self)
        goal_cube_copy = deepcopy(goal_cube)
        solved_cube = Cube()
        # construct the map
        piece_map = {} #maps the edge in each position with the solved cube's edge
        for edge_num in range(12):
            piece_map[goal_cube_copy.edges[edge_num].colors] = solved_cube.edges[edge_num].colors
            piece_map[goal_cube_copy.edges[edge_num].flip().colors] = solved_cube.edges[edge_num].flip().colors

        for corn_num in range(8):
            piece_map[goal_cube_copy.corners[corn_num].colors] = solved_cube.corners[corn_num].colors
            piece_map[goal_cube_copy.corners[corn_num].rotateClockwise().colors] = solved_cube.corners[corn_num].rotateClockwise().colors
            piece_map[goal_cube_copy.corners[corn_num].rotateClockwise().colors] = solved_cube.corners[corn_num].rotateClockwise().colors

        #apply the map to the given cube
        for edge_num in range(12):
            mapped_cube.edges[edge_num].colors = piece_map[mapped_cube.edges[edge_num].colors]
        for corn_num in range(8):
            mapped_cube.corners[corn_num].colors = piece_map[mapped_cube.corners[corn_num].colors]

        return mapped_cube

    #generates a random algstring of random length in the given bounds and excecutes it
    def scramble(self, num_moves_min: int =30, num_moves_max: int = 50):
        assert(num_moves_min > 0 and num_moves_min <= num_moves_max) #check the number of moves bound
        
        num_moves = random.randint(num_moves_min, num_moves_max)
        return self.parseAlgString(self.get_rand_alg(num_moves))

    @staticmethod
    def get_rand_alg(num_moves: int=30) -> str:
        moves = []
        possible_moves = ['F','F2','F\'','R','R2','R\'','L','L2','L\'','B','B2','B\'','U','U2','U\'','D','D2','D\'']

        moves = []
        for i in range(num_moves):
            moves.append(random.choice(possible_moves))

        return "".join(moves)
        

    #prints a representation of the cube's state to the terminal
    def print(self):
        serial_cube = Cube.get_print_string(self.getColorMap())
        cur_index = 0
        for row in range(9):#9 rows of squares
            if row < 3 or row > 5:
                #print padding and only three squares
                print(' ' * 3, serial_cube[cur_index:cur_index+3], ' ' * 6, sep ='')
                cur_index += 3
            else:
                print(serial_cube[cur_index:cur_index+12])
                cur_index += 12

    #serializes the color map into a string that is ready to print
    def get_print_string(cmap: list) -> str:
        result = []#a list of chars
        #returns a string for the orange side, followed by green, white, blue, yellow slices, and the red side
        for row in range(9):
            for col in range(12):
                if row < 3:#the top
                    if col > 2 and col < 6:
                        #the orange side
                        result.append(cmap[row * 3 + (col - 3)].convertToString())
                elif row < 6:#the middle
                    if col < 3:#the green side
                        result.append(cmap[9 + (row-3) * 3 + col].convertToString())
                    elif col < 6:#the white side
                        result.append(cmap[18 + (row-3) * 3 + col - 3].convertToString())
                    elif col < 9:#the blue side
                        result.append(cmap[27 + (row-3) * 3 + col - 6].convertToString())
                    else:#the yellow side
                        result.append(cmap[36 + (row-3) * 3 + col - 9].convertToString())
                else: #row >=6
                    if col > 2 and col < 6:
                        #the red side
                        result.append(cmap[45 + (row-6) * 3 + (col - 3)].convertToString())
        return "".join(result)

    #returns a list of a 54 big list representing the [orangeSize, greenSide, whiteSide, blueSide, yellowSide, redSide]
    #   in these lists, elements are the color of the square converted to a string.
    def getColorMap(self):
        colorMap = [None] * 54

        #fill in the centers
        colorMap[4] = Color.ORANGE
        colorMap[9 + 4] = Color.GREEN
        colorMap[9*2 + 4] = Color.WHITE
        colorMap[9*3 + 4] = Color.BLUE
        colorMap[9*4 + 4] = Color.YELLOW
        colorMap[9*5 + 4] = Color.RED

        serialCenters = [4 + 9*x for x in range(6)]
        for i in range(54):
            if i not in serialCenters:
                location = serial_cube_index_map[i]
                if location[0] == 'edge':
                    colorMap[i] = self.edges[location[1]].colors[location[2]]
                elif location[0] == 'corner':
                    colorMap[i] = self.corners[location[1]].colors[location[2]]
        return colorMap

    #assumes the string is valid, that is, it is a sting of letters consisting of 
    # {R, R', R2, L, L', L2, U, U', U2, D, D', D2, F, F', F2, B, B', B2} and no other characters (cannot handle whitespace)
    # TODO : handle whitespace
    def parseAlgString(self, alg: str):
        if alg == "":
            return self#empty algoritm. Perform no moves
            
        if not re.fullmatch(re.compile('([RLFBUD][\'2]?)+'), alg):
            raise Exception("Invalid move string")

        #get a list of moves, not executed unless the full alg string is valid
        moves = re.compile('([RLFBUD][\'2]?)').findall(alg)
        
        #execute the moves
        for move in moves:
            if move == 'R':
                self.R()
            elif move == 'R\'':
                self.Rp()
            elif move == 'R2':
                self.R2()
            elif move == 'L':
                self.L()
            elif move == 'L\'':
                self.Lp()
            elif move == 'L2':
                self.L2()
            elif move == 'F':
                self.F()
            elif move == 'F\'':
                self.Fp()
            elif move == 'F2':
                self.F2()
            elif move == 'B':
                self.B()
            elif move == 'B\'':
                self.Bp()
            elif move == 'B2':
                self.B2()
            elif move == 'U':
                self.U()
            elif move == 'U\'':
                self.Up()
            elif move == 'U2':
                self.U2()
            elif move == 'D':
                self.D()
            elif move == 'D\'':
                self.Dp()
            elif move == 'D2':
                self.D2()
            else:
                raise Exception("Invalid move string that got past re check")
        return self
    
    ###### MOVE METHODS ######
    #functions that perform certain moves on the cube
    def R(self):
        self.edges[1], self.edges[5], self.edges[11], self.edges[6] =  self.edges[6].flip(), self.edges[1], self.edges[5], self.edges[11].flip()
        self.corners[0], self.corners[7], self.corners[6], self.corners[1] = \
            self.corners[1].rotateClockwise(), self.corners[0].rotateCounterclockwise(), self.corners[7].rotateClockwise(), self.corners[6].rotateCounterclockwise()
        return self

    def Rp(self):#implement a more efficient version later
        self.R()
        self.R()
        self.R()
        return self

    def R2(self):#implement a more efficient version later
        self.R()
        self.R()
        return self

    def L(self):
        self.edges[3], self.edges[7], self.edges[4], self.edges[9] = self.edges[4].flip(), self.edges[3], self.edges[9].flip(),  self.edges[7]
        self.corners[4], self.corners[3], self.corners[2], self.corners[5] = \
            self.corners[5].rotateClockwise(), self.corners[4].rotateCounterclockwise(), self.corners[3].rotateClockwise(), self.corners[2].rotateCounterclockwise()
        return self
    
    def Lp(self):#implement a more efficient version later
        self.L()
        self.L()
        self.L()
        return self
    
    def L2(self):#implement a more efficient version later
        self.L()
        self.L()
        return self

    def F(self):
        self.edges[4], self.edges[5], self.edges[8], self.edges[0] = self.edges[0], self.edges[8].flip(), self.edges[4],  self.edges[5].flip()
        self.corners[0], self.corners[3], self.corners[4], self.corners[7] = \
            self.corners[7].rotateCounterclockwise(), self.corners[0].rotateClockwise(), self.corners[3].rotateCounterclockwise(), self.corners[4].rotateClockwise()
        return self

    def Fp(self):#implement a more efficient version later
        self.F()
        self.F()
        self.F()
        return self

    def F2(self):#implement a more efficient version later
        self.F()
        self.F()
        return self

    def B(self):
        self.edges[2], self.edges[6], self.edges[10], self.edges[7] = self.edges[7].flip(), self.edges[2], self.edges[6],  self.edges[10].flip()
        self.corners[2], self.corners[1], self.corners[6], self.corners[5] = \
            self.corners[5].rotateCounterclockwise(), self.corners[2].rotateClockwise(), self.corners[1].rotateCounterclockwise(), self.corners[6].rotateClockwise()
        return self

    def Bp(self):#implement a more efficient version later
        self.B()
        self.B()
        self.B()
        return self

    def B2(self):#implement a more efficient version later
        self.B()
        self.B()
        return self

    def U(self):
        self.edges[8], self.edges[9], self.edges[10], self.edges[11] = self.edges[11], self.edges[8], self.edges[9],  self.edges[10]
        self.corners[7], self.corners[4], self.corners[6], self.corners[5] = \
            self.corners[6], self.corners[7], self.corners[5], self.corners[4]
        return self

    def Up(self):#implement a more efficient version later
        self.U()
        self.U()
        self.U()
        return self

    def U2(self):#implement a more efficient version later
        self.U()
        self.U()
        return self

    def D(self):
        self.edges[0], self.edges[1], self.edges[2], self.edges[3] = self.edges[3], self.edges[0], self.edges[1],  self.edges[2]
        self.corners[0], self.corners[1], self.corners[2], self.corners[3] = \
            self.corners[3], self.corners[0], self.corners[1], self.corners[2]
        return self
        
    def Dp(self):#implement a more efficient version later
        self.D()
        self.D()
        self.D()
        return self

    def D2(self):#implement a more efficient version later
        self.D()
        self.D()
        return self

def get_mappingTMP(self):
    for i in range(54):#for every sticker on a cube
        pass
    pass

def main():#runs if this is the main file
    x = Cube()
    print("Solved Cube vv")
    x.print()
    print("\nCheckerboard pattern vv")
    x.parseAlgString('R2L2U2D2F2B2').print()

    print("\nScrambled cube vv")
    Cube().scramble().print()

    y = Cube(stickers=['y', 'w', 'g', 'r', 'o', 'o', 'o', 'w', 'o',\
                        'g', 'g', 'w', 'y', 'g', 'o', 'b', 'o', 'w',\
                        'b', 'r', 'b', 'b', 'w', 'b', 'b', 'b', 'g',\
                        'y', 'y', 'r', 'w', 'b', 'g', 'o', 'w', 'y',\
                        'w', 'g', 'r', 'y', 'y', 'r', 'o', 'b', 'r',\
                        'r', 'y', 'w', 'g', 'r', 'o', 'y', 'r', 'g'])
    y.print()

if __name__ == '__main__':
    main()
