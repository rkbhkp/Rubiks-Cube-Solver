import cube
import maestro_interface
import cube_solver

def main():
    cube_str = ''
    while len(cube_str) != 54:
        cube_str = input("Please enter a valid 54 character cube string consisting of \'y\',\'o\',\'b\',\'g\',\'r\',\'w\'\n>> ")
    #get the cube object
    cube_obj = cube.Cube(list(cube_str))
    #find the solution algorithm
    sol = "".join(cube_solver.solve(cube_obj))

    #excecute the solution
    maestro_interface.excecute_alg_string(sol)

if __name__ == "__main__":
    main()