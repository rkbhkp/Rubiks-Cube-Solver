import cube
import cube_solver
import random

# for testing. Gets the frequency of the three main typed of moves on the cube. Used for tuning the hardware system
def test_frequency():
    prime = 0
    norm = 0
    double = 0
    for i in range(1000):
        cube_obj = cube.Cube().scramble()
        move_list = cube_solver.solve(cube_obj)
        for move in move_list:
            if "\'" in move:
                prime += 1
            elif '2' in move:
                double += 1
            else:
                norm += 1
    print("normal:", norm, "prime:", prime, "double:", double)

#executes random algorithm strings on the machine to test mechanics
def test_machine_mechanics(num_moves: int =1):
    import maestro_interface
    alg = cube.Cube.get_rand_alg(num_moves)
    maestro_interface.excecute_alg_string(alg)

#map that takes the front face, and the face that is up, and returns number of times to rotate data structure to match image

rotation_map = {\
    ('F', 'U'): 0,
    ('F', 'L'): 1,
    ('F', 'D'): 2,
    ('F', 'R'): 3,

    ('R', 'F'): 0,
    ('R', 'D'): 1,
    ('R', 'B'): 2,
    ('R', 'U'): 3,

    ('L', 'F'): 0,
    ('L', 'U'): 1,
    ('L', 'B'): 2,
    ('L', 'D'): 3,

    ('U', 'F'): 0,
    ('U', 'R'): 1,
    ('U', 'B'): 2,
    ('U', 'L'): 3,

    ('D', 'F'): 0,
    ('D', 'L'): 1,
    ('D', 'B'): 2,
    ('D', 'R'): 3,

    ('B', 'D'): 0,
    ('B', 'L'): 1,
    ('B', 'U'): 2,
    ('B', 'R'): 3,

}

#the starting index for that side in the colormap string
color_map_index = {\
    'F': 0,
    'L': 9,
    'D': 18,
    'R': 27,
    'U': 36,
    'B': 45
}
import maestro_interface
#returns a list 9 big based on what the cube's back face should be (with top left cube as 0 index) based on the passed 
# cube_obj. Assumes that initially, red faced the camera, and yellow was up, and all cube rotations have updated the
# maestro_interface map.
def get_current_side_truth_data(cube_obj: cube.Cube) -> list:
    back_face = maestro_interface.reverse_face_map['B']
    up_face = maestro_interface.reverse_face_map['U']

    face = cube_obj.getColorMap()[color_map_index[back_face]:color_map_index[back_face] + 9]

    for i in range(rotation_map[(back_face, up_face)]):
        rotate_face(face)   
    
    return face

#outputs images and their truth data under the parent directery/0-/num_cubes -1. Assumes that the cube
# is initially solved, and the red face faces the camera, and the yellow face faces up.
def get_mult_cube_truth_data(parent_dir:str, num_cubes: int=2):
    import take_photo
    import os#to check for and make directories
    #import maestro_interface

    cube_obj = cube.Cube()
    take_photo.init_camera()
    
    for i in range(num_cubes):
        if i % 3  == 0:
            input("change lighting then hit enter!")
        #get a random alg of length 10
        alg = cube_obj.get_rand_alg(5)
        #execute it on the cube object
        cube_obj.parseAlgString(alg)
        #do it on the machine's cube
        maestro_interface.excecute_alg_string(alg)
        print("Done executing algorithm " + str(i))

        #compute the directory
        directory = parent_dir + '/' + str(i)
        #if it doesn't already exist, create it
        if not os.path.exists(directory):
            os.makedirs(directory)

        #take the photos, and get the truth data
        take_photo.capture_cube(directory, cube_obj)    


#rotates the passed face by 90 degrees clockwise. The face is a list of 9 values.
def rotate_face(face: list):
    face[2], face[5], face[8], face[1], face[7], face[0], face[3], face[6] =\
        face[0], face[1], face[2], face[3], face[5], face[6], face[7], face[8]



if __name__ == "__main__":
    #test_frequency()
    #get_mv_truth_data(20)
    #print(get_current_side_truth_data(cube.Cube()))
    get_mult_cube_truth_data("photos/samples", num_cubes=20)
    #test_machine_mechanics()
