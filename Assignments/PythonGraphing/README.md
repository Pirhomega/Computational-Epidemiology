# Cellular Automata Program 2

## Computational Epidemiology - Summer II 2020

## Professor: Dr. Tina Johnson

## Programmer: Corbin Matamoros

## Program Description

This program demonstrates the SLIR model using graph theory, where people are represented
as nodes and personal contact with each other as edges. The weight of the edge represents
the number of times two adjacent nodes have contacted each other.

## Instructions

1. Make sure you have a compatible version of Python running (this program used version 3.8.3, 32-bit).

2. Have the latest version of [NetworkX](https://pypi.org/project/networkx/) and [Matplotlib](https://matplotlib.org/users/installing.html) installed on your computer. This program used NetworkX version 2.4 and MatPlotLib version 3.3.0

3. Modify the `params.json` file to represent your selected disease. `population` is the number people to include in the simulation, `num_contacts` is the average number of contacts each person is allowed to make, `trans_rate` is the ratio of infections per single contact, `init_infected` is the number of people in the population who begin the simulation infectious, `latent_period` and `infectious_period` are the disease's latent period and infectious period, respectively, `immune_perc` is the ratio of people who are immune to the disease per single person (e.g., in a population of 1000 and a `immune_perc` of 0.2, 200 people would be immune to the disease), and `show_graph` shows the final model in matplotlib (not recommended for large populations, e.g. > 500).

4. Place `params.json` and `GraphSLIR_Matamoros.py` in a folder and open a terminal there.

5. Enter `python GraphSLIR_Matamoros.py params.json` in the terminal and hit enter. Depending on the population, this program may take a while. If the population size is 1000 or greater, I recommend setting `show_graph` in the `params.json` file to `false`. The program will output what day it's on to prove it is running.

6. After the program has executed, it will spit out an `output.txt` file with the daily numbers (number of infections, people in the latent stage, etc.) and a list of the number of contacts each person made for the entire simulation. Dividing any person's contact count by the number of days the simulation lasted should result in the `num_contacts` value in `params.json`.

NOTES: I've tested this with a population of 104,000, and by day 28, the program had slowed to a crawl. Don't do that.
