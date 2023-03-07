import subprocess
import time
import re

#maps the various moves on the cube to subroutine indeces on the mini masestro so they can be called
sub_routine_map = \
{
    'in': '0',
    'out': '1',
    'D': '2',
    'D\'': '3',
    'D2': '4',
    'L': '5',
    'L\'': '6',
    'L2': '7',
    'R': '8',
    'R\'': '9',
    'R2': '10',
    'U': '11',
    'U\'': '12',
    'U2': '13',
    'Y': '14',
    'X': '15',
    'clear_side': '16',
    'undo_clear': '17',
}

#holds a mapping of sides. Essentially says, face X is now found on absolute side face_map[X]
face_map = \
{
    'U': 'U',
    'R': 'R',
    'L': 'L',
    'D': 'D',
    'F': 'F',
    'B': 'B'
}

#holds a reverse map of the map above
reverse_face_map = \
{
    'U': 'U',
    'R': 'R',
    'L': 'L',
    'D': 'D',
    'F': 'F',
    'B': 'B'
}


#updates the face map based upon a rotation (X or Y)
def update_face_map(x_rot: bool): #updates the facce map when rotating the cube
    if x_rot:
        face_map['U'], face_map['F'], face_map['D'], face_map['B'] = \
            face_map['B'], face_map['U'], face_map['F'], face_map['D']
        
        reverse_face_map['B'], reverse_face_map['U'], reverse_face_map['F'], reverse_face_map['D'] = \
            reverse_face_map['U'], reverse_face_map['F'], reverse_face_map['D'], reverse_face_map['B']
         

    else: #Y rotation
        tmp = face_map['B']
        face_map['B'] = face_map['R']
        face_map['R'] = face_map['F']
        face_map['F'] = face_map['L']
        face_map['L'] = tmp

        reverse_face_map['F'], reverse_face_map['R'], reverse_face_map['B'], reverse_face_map['L'] = \
                reverse_face_map['R'], reverse_face_map['B'], reverse_face_map['L'], reverse_face_map['F']



current_faces = ['U', 'R', 'L', 'D']

#returns false if the script is busy, else true
def script_done():
    res = subprocess.run(["maestro-linux/UscCmd", "--status"], capture_output=True)
    return "SCRIPT DONE" in res.stdout.decode()

#excecutes a single move in the sub_routine_map, and waits until it finishes
def exec_script(move: str):
    subprocess.run(["maestro-linux/UscCmd", "--sub", sub_routine_map[move]], capture_output=True)

    while not script_done():
        time.sleep(0.01)
    print(move, "mapped to", sub_routine_map[move], "done")

#excecutes a valid algorithm string, not including X, Y, Z moves. ASSUMES THE CUBE IS ALREADY IN. IF NOT, EXCECUTE SUBROUTINE 'in'
def excecute_alg_string(alg_str: str):
    if not re.fullmatch(re.compile('([RLFBUD][\'2]?)+'), alg_str):
            raise Exception("Invalid move string")

    #get a list of moves, not executed unless the full alg string is valid
    moves = re.compile('([RLFBUD][\'2]?)').findall(alg_str)
        
    #execute the moves
    for move in moves:
        if face_map[move[0]] in 'FB':
            exec_script('Y')
            update_face_map(x_rot=False)

        if len(move) > 1:
            exec_script(face_map[move[0]] + move[1])
        else:
            exec_script(face_map[move[0]])

def rotate_cube(move: str="X"):
    if move == "X":
        exec_script("X")
        update_face_map(x_rot=True)
    elif move == "Y":
        exec_script("Y")
        update_face_map(x_rot=False)
    else:
        raise Exception("Not X or Y move. Invalid rotation!")

#excecute_alg_string('BRUF\'')


