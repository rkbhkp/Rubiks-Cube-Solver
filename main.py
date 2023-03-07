#the entry point for the program
import get_image
import mv_output_to_cube
import cube
import cube_solver
import threading
import os

#The entry point. If there is a physical machine, it will excecute various moves and take photos.
# if not, the photos must already be present, and a solution string will be printed
def main(photo_dir:str= "photos/cube_out", physical_machine: bool=True, display_pygame: bool=False):
    #specific imports impotant only to the physical machine
    if physical_machine:
        import take_photo
        import maestro_interface

    #specific import for pygame
    if display_pygame:
        import pygame_visualizer as pg

    #move to neutral out
    if physical_machine:
        maestro_interface.exec_script("out")

    #wait until user inserts cube
    if physical_machine:
        input("Press enter once the cube has been inserted properly")

    #move to neutral in
    if physical_machine:
        maestro_interface.exec_script("in")

    #get the target scramble alg
    if physical_machine:
        scramble = input("Enter the target scramble alg and press enter (No alg = solved):")

    #take the photos
    if physical_machine:
        take_photo.init_camera()
        take_photo.capture_cube(photo_dir)

    #use machine vision to get the cube state
    mv_output = get_image.get_cube_classification_list(photo_dir)
    print('\n\n\n', mv_output)
    #read it into a cube object
    cube_obj = mv_output_to_cube.output_cube(mv_output)
    cube_obj.print()
    #if it is not on the physical machine, display the cube with pygame
    if display_pygame:
        displayer = threading.Thread(target=pg.pygame_process, args=[800, 600])
        displayer.start()

        pg.add_cube(cube_obj)#add the cube to the queue to be displayed
        
    #compute the solution algorithm
    if not cube_solver.is_cube_solved_to_scramble(cube_obj, scramble):
        solution = cube_solver.solve_to_scramble(cube_obj, scramble)
    else:
        solution = ""

    
    print("Solution:", solution)

    #execute the solution algorithm on the cube
    if physical_machine and solution != "":
        maestro_interface.excecute_alg_string(solution)

    #move to neutral out
    if physical_machine:
        maestro_interface.exec_script("out")
    
    if display_pygame:
        while True:
            if not displayer.is_alive():
                break
        displayer.join()#wait for the thread to finish

if __name__ == "__main__":
    main(photo_dir="photos/cube_out", physical_machine=True,display_pygame=False)
