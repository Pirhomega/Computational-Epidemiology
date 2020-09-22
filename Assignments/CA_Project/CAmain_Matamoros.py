# Cellular Automata Program 1
# Computational Epidemiology - Summer II 2020
# Dr. Johnson
# Programmer: Corbin Matamoros
# Program Description:
#       This program will use a cellular automaton to simulate disease spread in a closed population using the SLIR model.
#       Each day, a report will be generated and sent to an output file. The report will contain the locations of the
#       individuals at the end of each day, as well as the number of infectious, latent, and recovered individuals.

import random
import sys
import numpy as np
from CAhelper_Matamoros import load_params

##############################################################################################################
#                                               CONSTANTS
##############################################################################################################

# grab the parameters file from the command line
PARAMS = load_params(sys.argv[1])

# constants pertaining to the simulation, such as
#       grid dimensions
NUM_ROWS = PARAMS["num_row"]+2
NUM_COLS = PARAMS["num_col"]+2
GRID_SIZE = PARAMS["num_row"]
# variable that will keep any for-loops using it from traversing the border of a grid
ITERATOR_LIMIT = NUM_ROWS-1
# disease parameters
LATENT_PERIOD = PARAMS["latent_period"]
INFECTIOUS_PERIOD = PARAMS["infectious_period"]
CONTACT_TYPE = PARAMS["vonNeumann"]
MAX_EXPOSURE = PARAMS["max_exposure"]

# Create the two grids for the simulation
# Each index represents a location an individual can occupy
# The first 2D array / grid represents the current state of the simulation
# The second grid will represent the state of the disease spread based on the first grid
# Each element in the grid represents a location in the world as a tuple with the following schema:
    # (a, b, c, d, e) = (location state, days latent, days infectious, time exposed, individual id)
        # 'a' can be 1 (occupied by susceptible individual), 2 (occupied by latent individual), 
        #       3 (occupied by infectious individual), 4 (occupied by recovered individual).
        #       If an element is just a zero, the location is unoccupied
        # 'b' is an integer between 0 and the latent period, inclusive
        # 'c' is an integer between 0 and the infectious period, inclusive
        # 'd' is a float value that represents the time someone maintained close contact with an infectious individual
        # 'e' is a number given to an individual to identify them in the end-of-day report
        # if an element is (0,0,0,0,0), the location is unoccupied
SIM_MATRICES = np.zeros((3, NUM_ROWS, NUM_COLS), dtype=object)

# the `if __name__ == "__main__":` at the very bottom of this script calls this function
def main():
    # variables that count the number of susceptible, infectious, latent, and recovered individuals in the population
    num_susceptible = PARAMS["population"] - PARAMS["init_infected"]
    num_infectious = PARAMS["init_infected"]
    num_latent = 0
    num_recovered = 0

    # used to give each individual in the population a unique ID
    individual_counter = 1

    # if the population value is too large to fit in the simulation grid, warn the user and end program
    if PARAMS["population"] > GRID_SIZE*GRID_SIZE:
        print("The population -", PARAMS["population"], "- is too great to fit within the grid borders.\nPlease select a population less than or equal to", GRID_SIZE*GRID_SIZE)
    else:
        # initialize all grids to zeros
        for a in range(0, 3):
            for b in range(NUM_ROWS):
                for c in range(NUM_COLS):
                    SIM_MATRICES[a][b][c] = (0, 0, 0, 0, 0)
                    
        # These following two while loops will only place individuals randomly in the first grid so as to leave
        #       a border of zeros around the grid's outside. E.G.
        #       GRID A ->   |0 0 0 0 0| (the 'X' spots are usable; the '0' spots aren't)
        #                   |0 X X X 0|
        #                   |0 X X X 0|
        #                   |0 X X X 0|
        #                   |0 0 0 0 0|

        # disperse all initially infected individuals randomly throughout the first grid,
        #       but only place them in unoccupied locations
        y = num_infectious
        while y > 0:
            randx = random.randint(1, NUM_ROWS-2)
            randy = random.randint(1, NUM_COLS-2)
            if SIM_MATRICES[0][randx][randy][0] == 0:
                SIM_MATRICES[0][randx][randy] = (3, 0, 0, 0, individual_counter)
                y -= 1
                individual_counter += 1

        # disperse all susceptible individuals (which is total population minus the initial infectious individuals)
        #       randomly throughout the first grid but only place them in unoccupied locations
        x = num_susceptible
        while x > 0:
            randx = random.randint(1, NUM_ROWS-2)
            randy = random.randint(1, NUM_COLS-2)
            if SIM_MATRICES[0][randx][randy][0] == 0:
                SIM_MATRICES[0][randx][randy] = (1, 0, 0, 0, individual_counter)
                x -= 1
                individual_counter += 1

        # main simulation block
        # open a 'csv' file for outputting the daily reports, explained later
        with open("CAoutput.csv", 'w') as outfile:
            outfile.write("day,susceptible,latent,infectious,recovered\n")
            num_days = 0
            # loop until there are no individuals in the infectious nor latent stages
            while num_infectious or num_latent:
                # this variable keeps our for loops from interating over a border element.
                # Remember that our grid is surrounded by a layer of zeros so we don't get
                #       out-of-bounds errors when checking a cell's neighbors. We will only
                #       iterate over the cells within the border of zeros.
                for row in range(1, ITERATOR_LIMIT):
                    for col in range(1, ITERATOR_LIMIT):
                        # if a spot is unoccupied
                        if SIM_MATRICES[0][row][col][0] == 0 or SIM_MATRICES[0][row][col][0] == 4:
                            SIM_MATRICES[1][row][col] = SIM_MATRICES[0][row][col]
                        # if a spot is occupied by a susceptible person
                        elif SIM_MATRICES[0][row][col][0] == 1:
                            SIM_MATRICES[1][row][col], num_latent, num_susceptible = infect(SIM_MATRICES[0][row][col], (row, col), num_latent, num_susceptible)
                        # if a spot is occupied by an latent person
                        elif SIM_MATRICES[0][row][col][0] == 2:
                            SIM_MATRICES[1][row][col], num_infectious, num_latent = infectious(SIM_MATRICES[0][row][col], num_infectious, num_latent)
                        # if a spot is occupied by a infectious person
                        elif SIM_MATRICES[0][row][col][0] == 3:
                            SIM_MATRICES[1][row][col], num_infectious, num_recovered = recovered(SIM_MATRICES[0][row][col], num_infectious, num_recovered)

                # copy second grid to first grid and begin the next day of the simulation, zero-ing out grid 2
                for row in range(1, ITERATOR_LIMIT):
                    for col in range(1, ITERATOR_LIMIT):
                        SIM_MATRICES[0][row][col] = SIM_MATRICES[1][row][col]
                        SIM_MATRICES[1][row][col] = (0,0,0,0,0)
                        print(SIM_MATRICES[0][row][col][0], end='', flush=True)
                    print()
                print('---------------------------')
                # outputs the end-of-day state of the grid to csv output file
                outfile.write(str(num_days)+','+str(num_susceptible)+','+str(num_latent)+','+str(num_infectious)+','+str(num_recovered)+'\n')
                # print(num_days)
                num_days += 1

##############################################################################################################
#                                              FUNCTIONS
##############################################################################################################

# An individuals is infected if the sum of infectious neighbors equals or surpasses the "exposure points" limit
#       set in `PARAMS.json`
def infect(individual, location, latent_count, susecptible_count):
    # sum up the number of exposure points the susceptible individual has accumulated
    total_exposure = individual[3] + checkNeighbors(location)
    # if the individual has less than the number of exposure points necessary to get infected
    #       return the sum of their current exposure point count and the new ones from this
    #       function call
    if total_exposure < MAX_EXPOSURE:
        return (1,0,0,total_exposure,individual[4]), latent_count, susecptible_count
    else:
        return (2,0,0,0,individual[4]), (latent_count+1), (susecptible_count-1)

# count how many infectious neighbors an individual has
def checkNeighbors(location):
    count = 0
    # if using the von Neumann method, just check the north, south, east, and west neighbors
    if SIM_MATRICES[0][location[0]][location[1]+1][0] == 3:
        count += 1
    if SIM_MATRICES[0][location[0]-1][location[1]][0] == 3:
        count += 1
    if SIM_MATRICES[0][location[0]][location[1]-1][0] == 3:
        count += 1
    if SIM_MATRICES[0][location[0]+1][location[1]][0] == 3:
        count += 1
    # if using the Moore method, consider the corner neighbors
    if not CONTACT_TYPE:
        if SIM_MATRICES[0][location[0]-1][location[1]+1][0] == 3:
            count += 1
        if SIM_MATRICES[0][location[0]-1][location[1]-1][0] == 3:
            count += 1
        if SIM_MATRICES[0][location[0]+1][location[1]-1][0] == 3:
            count += 1
        if SIM_MATRICES[0][location[0]+1][location[1]+1][0] == 3:
            count += 1
    return count

# determine if a latent individual jumps to the infectious stage
def infectious(individual, infectious_count, latent_count):
    # if the individual has not been in the latent stage for the latent period,
    #       increment the 'b' index in the individual's tuple
    if individual[1] < LATENT_PERIOD:
        return (2,individual[1]+1,0,0,individual[4]), (infectious_count), (latent_count)
    # if the individual has been in the latent stage for the latent period,
    #       increment the 'a' index of the individual's tuple
    else:
        return (3,0,0,0,individual[4]), (infectious_count+1), (latent_count-1)

# determine if an infectious individual jumps to the recovered stage
def recovered(individual, infectious_count, recovered_count):
    # if the individual has not been in the infectious stage for the infectious period,
    #       increment the 'c' index in the individual's tuple
    if individual[2] < INFECTIOUS_PERIOD:
        return (3,0,individual[2]+1,0,individual[4]), infectious_count, recovered_count
    # if the individual has been in the infectious stage for the infectious period,
    #       increment the 'a' index of the individual's tuple
    else:
        return (4,0,0,0,individual[4]), infectious_count-1, recovered_count+1

# the `int main()` of the program
if __name__ == "__main__":
    main()
