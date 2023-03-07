import get_image
import os
import re

import random

#compares what the MV system thought to the truth data of the cube, then prints out a grade, and which cubes were missed.
def main():
    missed_cubes = [] #list of file paths to missed cubes
    grade = 0 #grade will increment by 1 if a cube is correctly classified
    total = 0 #total will increment by 1 every cube
    
    #root_path = "photos/failed"
    root_path = "photos/samples"
    #root_path = "photos/stickerless_sample"
    dirs = os.listdir(root_path)
    

    for folder in dirs:
        path = root_path + '/' + folder

        mv_pass = True

        try:
            mv_res = get_image.get_cube_classification_list(path)
            #print(mv_res)
            truth_data = [] #list of sides
            with open(path + "/truth_data.txt", "r") as f:
                x = f.readlines()
                for side in range(6):
                    truth_data.append(re.compile('[012345]').findall(x[side]))
            #truth_data = random.shuffle(truth_data)
            #go through the mv_res, and the truth data, make a map, and see if it is ever violated.
            truth_map = {}
            for side in range(6):
                for square in range(9):
                    if truth_data[side][square] in truth_map:
                        predicted_value = truth_map[truth_data[side][square]]
                        if predicted_value != mv_res[side][square]:
                            mv_pass = False   
                    else:
                        truth_map[truth_data[side][square]] = mv_res[side][square]
            if len(truth_map) != 6:
                mv_pass = False    
            print(f"Passed {root_path + '/' + folder}? {mv_pass}")
        except:
            mv_pass = False
            grade -= 0.5 #extra penalty for crashing
            print(f"Crashed {root_path + '/' + folder}?")
        if mv_pass:
            grade += 1
        total += 1
    print(f'\n\nGrade is {grade}/{total}')

if __name__ == "__main__":
    main()