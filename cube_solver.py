#this file's job is to take an arbitrary (but valid) cube object and output a list of moves that solves the cube
import cube
#from rubik_solver import utils
import kociemba

#takes a cube and a scramble string, and returns a string of moves to convert the passed cube into that
# scramble. By default, there is no scramble, thus the goal state is solved
# This function should be the main function to be called in this file.
def solve_to_scramble(cube_obj: cube.Cube, scramble_alg: str = "") -> str:
    if scramble_alg == "":
        return "".join(solve(cube_obj))
    else:
        mapped_cube = cube_obj.map_to_goal(cube.Cube().parseAlgString(scramble_alg))
        sol = solve(mapped_cube)
        return "".join(sol)

#returns true if the passed cube is solved to a specific scramble, false otherwise
# pass no scramble_alg to test if a cube is solved
def is_cube_solved_to_scramble(cube_obj: cube.Cube, scramble_alg: str = "") -> bool:
    sol_cube = cube.Cube()
    if scramble_alg != "":
        sol_cube.parseAlgString(scramble_alg)

    #check if cube_obj is equivilant
    #check if edges are equivilant
    for edge_num in range(12):
        for colors in range(2):
            if sol_cube.edges[edge_num].colors[colors] != cube_obj.edges[edge_num].colors[colors]:
                return False
    #check if corners are equivilant
    for corner_num in range(8):
        for colors in range(3):
            if sol_cube.corners[corner_num].colors[colors] != cube_obj.corners[corner_num].colors[colors]:
                return False
    return True

#solves the given cube with the Kociemba method, returns a list of moves
def solve(cube_obj: cube.Cube) -> list:
    #convert the color map to make it play nice with the solver library:
    cube_internal_state_list = cube_obj.getColorMap()
    color_converter_map = {cube.Color.YELLOW: 'B', cube.Color.WHITE: 'F', cube.Color.ORANGE: 'U', cube.Color.RED: 'D', cube.Color.GREEN: 'L', cube.Color.BLUE: 'R'}
    cube_state_string = "".join(list(map(color_converter_map.get, cube_internal_state_list)))
    #reorder the cube faces how the library expects
    cube_state_string = cube_state_string[0:9]  + cube_state_string[27:36] + cube_state_string[18:27] \
         + cube_state_string[45:54]  + cube_state_string[9:18]  + cube_state_string[36:45]  
    #get the solution string
    sol = kociemba.solve(cube_state_string)
    solution = sol.split(' ')
    
    #account for cube rotation expected by solution
    move_list = []
    for move in solution:
        move_str = move.__str__()
        #replace moves because solving algorithm expects the cube to be rotated
        if 'U' in move_str:
            move_str = move_str.replace('U', 'F')
        elif 'F' in move_str:
            move_str = move_str.replace('F', 'D')
        elif 'D' in move_str:
            move_str = move_str.replace('D', 'B')
        elif 'B' in move_str:
            move_str = move_str.replace('B', 'U')
        move_list.append(move_str)   
    return move_list

# A driver function to demonstrate solving abilities. Should not be called
def main():
    import threading#only import if main is executed
    import pygame_visualizer as pg
    from time import sleep
    displayer = threading.Thread(target=pg.pygame_process, args=[800, 600])
    displayer.start()

    cube_obj = cube.Cube().scramble()
    pg.add_cube(cube_obj)#add the cube to the queue to be displayed

    #cube_obj.print()
    move_list = solve(cube_obj)

    timer_thread = threading.Thread(target=sleep, args=[1.0])
    timer_thread.start()
    
    #get input alg
    while True:
        if not timer_thread.is_alive():
            if len(move_list) != 0:
                try:
                    #execute the moves on the cube
                    move = move_list.pop(0)
                    print(move)
                    cube_obj.parseAlgString(move)
                    pg.add_cube(cube_obj)
                except Exception as e:
                    print(e)

                #restart the thread
                timer_thread = threading.Thread(target=sleep, args=[1.0])
                timer_thread.start()
        if not displayer.is_alive():
            break

    displayer.join()#wait for the thread to finish
    #exit

if __name__ == "__main__":
    main()
    
    '''
    goal_scramble_alg = "D\'U2F\'UB\'D\'BLUD2F2BD\'R2B\'L2F2L2FD\'R\'F2D2F\'R2"
    init_cube = cube.Cube().parseAlgString("L2FU2B\'L2R\'U2D2F2U2R2BLD2ULDBR2DB2RBD2U\'")

    solution_alg = solve_to_scramble(init_cube, goal_scramble_alg)
    print(solution_alg)
    from copy import deepcopy

    test_cube = deepcopy(init_cube)

    test_cube.parseAlgString(solution_alg)
    test_cube.print()
    '''
