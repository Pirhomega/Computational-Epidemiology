# Cellular Automata Program 2
# Computational Epidemiology - Summer II 2020
# Dr. Johnson
# Programmer: Corbin Matamoros
# Program Description:
#       This program demonstrates the SLIR model using graph theory, where people are represented
#       as nodes and personal contact with each other as edges. The weight of the edge represents
#       the number of times two adjacent nodes have contacted each other.

import networkx as nx
import json
import sys
import random
import matplotlib.pyplot as plt

# loads the .json file into a dictionary
def load_json(infile):
    with open(infile,'r') as f:
        data = f.read()
        dictionary_json = json.loads(data)
    return dictionary_json

# randomly selects two distinct individuals by their ID's 
def rando_persons(population_size):
    person1 = random.randint(0,population_size)
    person2 = random.randint(0,population_size)
    if person1 != person2:
        return person1, person2
    # if the two people are the same (we don't want that), run this function again
    return rando_persons(population_size)

# if a random number between 0.0 and 1.0 is larger than the transmission rate (TR),
#       return True. An individual is getting infected.
def attempt_infection(transmission_rate):
    if random.random() > transmission_rate:
        return True
    else:
        return False

def main():
    # grab the user's parameters from `PARAMS.json` and apply them to the project
    PARAMS = load_json(sys.argv[1])

    # safe-guards
    # If there are: E.G. 110 initially infected people when the population is 100
    if PARAMS["init_infected"] > PARAMS["population"]:
        print("The number of initially infected people is greater than the population size. Lower it, and restart the program.")
    # If there are: E.G. 50 initially infected people in a population of 100 people, where 60 people are already immune
    elif (PARAMS["immune_perc"]*PARAMS["population"])+PARAMS["init_infected"] > PARAMS["population"]:
        print("The sum of initially infected and immune people is larger than the population. Lower one or the other, and restart the program.")
    else:
        # population size
        N = PARAMS["population"]
        # average number of contacts per person, per day;
        C = PARAMS["num_contacts"]
        # number of contacts allowed in entire population per day 
        CP = C * N
        # transmission rate
        TR = PARAMS["trans_rate"]
        # number of initially infected people
        II = PARAMS["init_infected"]
        # days latent
        DL = PARAMS["latent_period"]
        # days infectious
        DI = PARAMS["infectious_period"]
        # percent and number of immune people, respectively - these people may have natural immunity or may have been vaccinated
        PI = PARAMS["immune_perc"]
        NI = int(PI * N)
        # shows a graph of the final state of the model (number of remaining susceptibles, removed, and immune people)
        GRAPH = PARAMS["show_graph"]

        # Graph of the disease spread
        SimGraph = nx.Graph()

        # number used to give people a unique identifier
        iden = 0

        # current number of susceptible people
        current_susceptible = N - II - NI

        # current number of infectious people
        current_infectious = II

        # current number people in the latent stage
        current_latent = 0

        # current number of recovered people
        current_recovered = 0

        # number of people infected on any day
        daily_infections = 0
        # simulation day
        day = 0

        # populate the graph with enough nodes to represent the population
        # Add the initially infected people first
        for _ in range(II):
            SimGraph.add_node(iden,attributes={"immune":False,"susceptible":False,"latent":False,"infectious":True,"recovered":False,"days_in_state":0,"num_contacts":0})
            iden += 1

        # Add the number of immune
        for _ in range(NI):
            SimGraph.add_node(iden,attributes={"immune":True,"susceptible":False,"latent":False,"infectious":False,"recovered":False,"days_in_state":0,"num_contacts":0})
            iden += 1

        # Add the rest of the population as susceptible
        for x in range(iden,N):
            SimGraph.add_node(x,attributes={"immune":False,"susceptible":True,"latent":False,"infectious":False,"recovered":False,"days_in_state":0,"num_contacts":0})
        
        # open the output file to which we will write the daily numbers and contact count of each
        #       person at the end of the simulation
        with open("output.txt",'w') as w:
            # main simulation loop, where we continue the simulation until there are no more infectious
            #       nor latent people
            while current_infectious or current_latent:
                # this loops until we hit the total number of contacts allowed per day
                # We loop 2 contacts at a time because whenever, say, person1 has contact with
                # person2, person2 has contacted person1. A net count of two contacts. Make sense? Cool.
                for _ in range(0,CP,2):
                    # pick two random people to have close contact
                    person1, person2 = rando_persons(N - 1)
                    # increment each person's contact count by one
                    SimGraph.nodes[person1]["attributes"]["num_contacts"] += 1
                    SimGraph.nodes[person2]["attributes"]["num_contacts"] += 1

                    # create an edge between them if it doesn't exist
                    if not SimGraph.has_edge(person1,person2):
                        SimGraph.add_weighted_edges_from([(person1,person2,1)])
                    # if the edge already exists, increase its weight by one
                    else:
                        SimGraph.edges[person1,person2]["weight"] += 1

                    # INFECTING SECTION
                    # if person1 is infectious while person2 isn't
                    if SimGraph.nodes[person1]["attributes"]["infectious"] and SimGraph.nodes[person2]["attributes"]["susceptible"]:
                        # if the individual is getting infected, we update their node;
                        #       if they don't get infected, leave everything as is
                        if attempt_infection(TR):
                            SimGraph.nodes[person2]["attributes"]["latent"] = True
                            SimGraph.nodes[person2]["attributes"]["susceptible"] = False
                            current_latent += 1
                            current_susceptible -= 1
                            daily_infections += 1
                    # if person 2 is infectious while person 1 isn't
                    elif SimGraph.nodes[person2]["attributes"]["infectious"] and SimGraph.nodes[person1]["attributes"]["susceptible"]:
                        # if the individual is getting infected, we update their node;
                        #       if they don't get infected, leave everything as is
                        if attempt_infection(TR):
                            SimGraph.nodes[person1]["attributes"]["latent"] = True
                            SimGraph.nodes[person1]["attributes"]["susceptible"] = False
                            current_latent += 1
                            current_susceptible -= 1

                # loop through the entire population and handle each person's state
                #       increasing days latent or infectious by one if they haven't
                #       been in that state for the entire latent or infectious period.
                #       Also, we move people who have stayed the duration of each period
                #       to the next state.
                for node in range(N):
                    # ADJUSTING PEOPLE'S TIME IN LATENT STAGE
                    # if person is in the latent stage
                    if SimGraph.nodes[node]["attributes"]["latent"]:
                        # if they've been in the latent stage for less than the disease's latent period
                        if SimGraph.nodes[node]["attributes"]["days_in_state"] < DL:
                            SimGraph.nodes[node]["attributes"]["days_in_state"] += 1
                        # if they have, progress them to the next stage
                        else:
                            SimGraph.nodes[node]["attributes"]["latent"] = False
                            SimGraph.nodes[node]["attributes"]["infectious"] = True
                            current_infectious += 1
                            current_latent -= 1
                            SimGraph.nodes[node]["attributes"]["days_in_state"] = 0
                    
                    # ADJUSTING PEOPLE'S TIME IN INFECTIOUS STAGE
                    # if person is in the infectious stage
                    elif SimGraph.nodes[node]["attributes"]["infectious"]:
                        # if they've been in the infectious stage for less than the disease's infectious period
                        if SimGraph.nodes[node]["attributes"]["days_in_state"] < DI:
                            SimGraph.nodes[node]["attributes"]["days_in_state"] += 1
                        # if they have, progress them to the next stage
                        else:
                            SimGraph.nodes[node]["attributes"]["infectious"] = False
                            SimGraph.nodes[node]["attributes"]["recovered"] = True
                            current_recovered += 1
                            current_infectious -= 1
                            # we don't reset SimGraph.nodes[node]["attributes"]["days_in_state"] since recovered people
                            #       aren't processed in the simulation anymore.

                # print off the number of people in each state at the end of the day
                w.write("Day "+str(day)+'\n')
                w.write("Num infections: "+str(daily_infections)+'\n')
                w.write("Num immune: "+str(NI)+'\n')
                w.write("Num susceptible: "+str(current_susceptible)+'\n')
                w.write("Num latent: "+str(current_latent)+'\n')
                w.write("Num infectious: "+str(current_infectious)+'\n')
                w.write("Num recovered: "+str(current_recovered)+'\n')
                w.write('-------------------------------\n')
                # print the day to the terminal to prove the program is still executing
                print("Day:",day)
                # move on to the next day
                day += 1
                daily_infections = 0
            
            # loop through all nodes in the graph and print each person's ID and their contact count
            for (u, d) in SimGraph.nodes(data=True):
                w.write("Person "+str(u)+" was contacted "+str(d["attributes"]["num_contacts"])+" times.\n")

        # if the user wants to see the final model's state, draw to Matplotlib
        if GRAPH:
            # here we add the nodes of people who are either susceptible, recovered, and immune to their own list.
            #       That way, we can apply a color to each node type.
            susceptible = []
            recovered = []
            immune = []
            for (_, d) in SimGraph.nodes(data=True):
                if d["attributes"]["susceptible"]:
                    susceptible.append(u)
                elif d["attributes"]["recovered"]:
                    recovered.append(u)
                else:
                    immune.append(u)

            # Draw the graph
            pos = nx.circles_layout(SimGraph)
            nx.draw_networkx_nodes(SimGraph, pos, nodelist=susceptible, node_color='#14de4a')
            nx.draw_networkx_nodes(SimGraph, pos, nodelist=recovered, node_color='#0000ff')
            nx.draw_networkx_nodes(SimGraph, pos, nodelist=immune, node_color='#ba8722')
            nx.draw_networkx_labels(SimGraph, pos)
            nx.draw_networkx_edges(SimGraph, pos, width=0.25, arrowsize=1)
            # nx.draw_networkx_edge_labels(SimGraph, pos, font_size=4) # this slows the program down a LOT for large populations
            plt.title("SLIR simulation over "+str(day)+" days")
            plt.show()

if __name__ == "__main__":
    main()
