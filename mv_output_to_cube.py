import utils
#import maestro_interface
import cube 

#takes a list of six sides, each with 9 elements, and returns a cube object
def output_cube(sides: list) -> cube.Cube:

    #rotate the faces to be correct based on the photos that were taken
    rotations = []
    with open("photos/cube_out/rotations.txt", "r") as f:
        x = f.read()
        for rot in x.strip()[1:-1].split(', '):
            rotations.append(int(rot))
    
    for sideNum in range(6):
        for _i in range(4 - rotations[sideNum]):
          utils.rotate_face(sides[sideNum])

    # now read the sides into a cube object in a specified order
    return cube.Cube(sides[3] + sides[1] + sides[5] + \
                        sides[4] + sides[2] + sides[0])
    
if __name__ == "__main__":
    res_cube = output_cube([['2', '5', '2', '6', '6', '1', '1', '3', '3'], \
                            ['5', '2', '6', '3', '4', '5', '2', '1', '5'],\
                            ['4', '4', '4', '3', '2', '2', '3', '5', '1'],\
                            ['2', '5', '1', '4', '5', '6', '3', '1', '1'],\
                            ['5', '2', '3', '6', '3', '4', '6', '4', '6'],\
                            ['5', '2', '6', '1', '1', '6', '4', '3', '4']])

    import threading#only import if main is executed
    import pygame_visualizer as pg
    from time import sleep
    import cube_solver
    displayer = threading.Thread(target=pg.pygame_process, args=[800, 600])
    displayer.start()

    pg.add_cube(res_cube)#add the cube to the queue to be displayed
    print(cube_solver.solve(res_cube))
    #get input alg
    while True:
        if not displayer.is_alive():
            break

    displayer.join()#wait for the thread to finish