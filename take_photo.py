from time import sleep
from picamera import PiCamera
import maestro_interface
import cube
import utils
import os

camera = None

def init_camera():
    global camera
    camera = PiCamera()
    camera.rotation = 270
    camera.resolution = (2000,2000)

def capture_image(filename: str):
    maestro_interface.exec_script('clear_side')
    camera.capture(filename)
    maestro_interface.exec_script('undo_clear')

def capture_cube(folder: str, truth_cube: cube.Cube=None):
    if not os.path.exists(folder):
            os.makedirs(folder)
    
    side_id = 0

    #captures the image, and gets the truth data if a truth cube was provided
    def capture(truth_cube: cube.Cube=None):
        if truth_cube:
            truth_data[side_id] = utils.get_current_side_truth_data(truth_cube)
        capture_image(folder + "/" + str(side_id) + ".jpg")

    #returns the number of clockwise rotations the truth cube would have to undergo to match the image
    def get_rotations():
        back_face = maestro_interface.reverse_face_map['B']
        up_face = maestro_interface.reverse_face_map['U']
        return utils.rotation_map[(back_face, up_face)]

    num_rotations = []# a 6 big list of ints representing the number of clockwise rotations to make the cube's face match the image.
    truth_data = [[],[],[],[],[],[]] # a 6 big list
    
    capture(truth_cube)
    #save the number of rotations for undoing later
    num_rotations.append(get_rotations())

    side_id += 1
    maestro_interface.rotate_cube("Y")
    
    capture(truth_cube)
    #save the number of rotations for undoing later
    num_rotations.append(get_rotations())
    
    side_id += 1
    maestro_interface.rotate_cube("X")
    
    capture(truth_cube)
    #save the number of rotations for undoing later
    num_rotations.append(get_rotations())
   
    side_id += 1
    maestro_interface.rotate_cube("Y")
    
    capture(truth_cube)
    #save the number of rotations for undoing later
    num_rotations.append(get_rotations())
    
    side_id += 1
    maestro_interface.rotate_cube("X")
    
    capture(truth_cube)
    #save the number of rotations for undoing later
    num_rotations.append(get_rotations())
   
    side_id += 1
    maestro_interface.rotate_cube("Y")
    
    capture(truth_cube)
    #save the number of rotations for undoing later
    num_rotations.append(get_rotations())

    #output the rotations to a file called rotations.txt 
    # this allows the cube to be reconstructed later, even if the cube rotations are not knows
    with open(folder + "/rotations.txt", "w") as f:
        f.write(str(num_rotations))

    if truth_cube:
        #write the truth data to a text file in that folder
        with open(folder + "/truth_data.txt", "w") as f:
            for i in range(6):
                f.write(str(truth_data[i]) + "\n")
    maestro_interface.rotate_cube("X")
    

if __name__ == "__main__":
    init_camera()
    capture_cube("./photos/cube_out", cube.Cube().parseAlgString("RUL\'D2F2L\'"))
