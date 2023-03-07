import cube
import pygame

from queue import Queue #threadsafe queue implementation

#defines the colors of each sqaure type.
square_color = {'o': (229, 159, 9), 'y': (229, 218, 9),'r': (229, 9, 9),
                'b': (9, 12, 188),'g': (67, 229, 9),'w': (199, 204, 197)}

cube_queue = Queue() # a queue of cube objects that the pygame visualizer consumes and displays

#adds a cube to the cube_queue to be displayed by the pygame thread
def add_cube(cube_obj: cube.Cube):
    cube_queue.put(cube_obj)

#runs the visualizer process. Consumes the next item in the queue and displays it once every 1/30 sec. Only one pygame process can be running at a time
def pygame_process(x_size: int =300, y_size: int =300):
    assert(x_size > 12 and y_size > 9)#to be able to display the cube, must be at least this size
    pygame.init()
    surface = pygame.display.set_mode((x_size, y_size))

    pygame.time.set_timer(pygame.USEREVENT, 33)# start the timer for grabbing from the queue
    keep_window_open = True
    while keep_window_open:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                keep_window_open = False
            elif event.type == pygame.USEREVENT:
                if not cube_queue.empty():
                    display_cube(cube_queue.get(), 0, 0, x_size, y_size, surface)
                    pygame.display.flip()
    pygame.quit()

#usage example
def main():
    import threading#only import if main is executed
    displayer = threading.Thread(target=pygame_process, args=[800, 600])
    displayer.start()

    #display the cube
    cube_obj = cube.Cube().scramble()
    add_cube(cube_obj)
    
    #start a thread to get user input from the terminal
    user_in_buffer = [] #list of move strings
    user_in_thread = threading.Thread(target=get_input, args=[user_in_buffer, "Enter alg string: "], daemon=True)
    user_in_thread.start()

    #get user input algs
    while True:
        if not user_in_thread.is_alive():
            move_str = "".join(user_in_buffer)
            user_in_buffer = []#empty the buffer
            try:
                #execute the moves on the cube
                cube_obj.parseAlgString(move_str)
                add_cube(cube_obj)
            except Exception as e:
                print(e)

            #restart the thread to get new input
            user_in_thread = threading.Thread(target=get_input, args=[user_in_buffer, "Enter alg string: "], daemon=True)
            user_in_thread.start()
        if not displayer.is_alive():
            break

    displayer.join()#wait for the thread to finish
    #exit

def get_input(in_buffer: list, msg: str = ''):
    in_buffer.append(input(msg))


#displays the cube as large as possible within the given rectangular area, does not flip the surface, does not check for out of bounds x and y values yet <<<<
def display_cube(cube_obj: cube.Cube, x_start: int, y_start: int, x_max: int, y_max: int, surface: pygame.Surface):

    total_y = y_max - y_start
    total_x = x_max - x_start

    #in x we need to display 4 sides, in y, we need to display 3 sides.
    if total_y / total_x > 3.0/4.0:
        square_size = total_x // 12
    else:
        square_size = total_y // 9    

    cmap = cube_obj.getColorMap()
    side_num = 0
    square_num = 0
    serialized_color_map = cube.Cube.get_print_string(cmap)

    cur_index = 0
    for row in range(9):#9 rows of squares
        if row < 3 or row > 5:
            #print padding and only three squares
            draw_cube_slice(serialized_color_map[cur_index:cur_index+3], x_start + 3*square_size, y_start + row*square_size, square_size, surface)
            cur_index += 3
        else:
            draw_cube_slice(serialized_color_map[cur_index:cur_index+12], x_start, y_start + row*square_size, square_size, surface)
            cur_index += 12

def draw_cube_slice(slice: str, start_x: int, start_y: int, square_size: int, surface: pygame.Surface):
    for square in slice:
        color = square_color[square]
        pygame.draw.rect(surface, color, pygame.Rect(start_x, start_y, square_size, square_size))
        start_x += square_size

if __name__ == '__main__':
    main()