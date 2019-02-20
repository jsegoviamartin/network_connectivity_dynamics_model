#### Model to calculate convergence ####
# Includes:
# A class (Match) that contains:
# 1. Parametrized mathematical model: The model yield a probability distribution
# of variants (x) for a given history (h) of previous rounds, according to an equation
# that operates as a function of content bias, coordination bias, memory and innovarion rate.
# 2. Funtion to calculate agents' choices
# 3. Function to store produced variants in each agents' memory
# 4. Function to calculate entropy
# 5. A function (main) to set up number of agents, variants, population connectivity dynamic, memory lenght,
# level of content bias, level of coordination bias, mutation/innovation rate,
# singleton distribution (variants' quality) and number of simulations.
#
# Jose Segovia Martin (Autonomous University of Barcelona)


from __future__ import division
from random import random, sample
import random as rand
from bisect import bisect
from collections import deque
from itertools import permutations
import csv
import math

class Match():
    def __init__(self, agents, menLen, pairs, signals, s, s2, s3, cont, coord, mut):
        self.pairs = pairs
        self.signals = signals
        self.s = s
        self.s2 = s2
        self.s3 = s3
        self.cont = cont
        self.coord = coord
        self.mut = mut
        # self.agents=agents
        self.agents = {name: Match.player(menLen)
                       for pair in pairs[0]
                       for name in pair}
        self.memory = list()


    def produce_signals(self):

        def model(shown, observed, s, s2, s3, r, name):
            if name <= 8:
                if r < 7:
                    if not (shown == observed == 0):
                        result = ((0.98) * (1.0 - self.cont) * (1.0 - self.coord) * shown / r) + ((0.98) * (1.0 - self.cont) * (self.coord) * observed / r) + ((0.98) * self.cont * s) + ((self.mut / 8))
                    else:
                        result = ((0.98) * (1.0 - 0) * (1.0 - self.coord) * shown / r) + ((0.98) * (1.0 - 0) * (self.coord) * observed / r) + ((0.98) * 0 * s) + ((self.mut / 8))
                else:
                    if not (shown == observed == 0):
                        result = ((0.98) * (1.0 - self.cont) * (1.0 - self.coord) * shown / r) + ((0.98) * (1.0 - self.cont) * (self.coord) * observed / r) + ((0.98) * self.cont * s) + ((self.mut / 8))
                    else:
                        result = ((0.98) * (1.0 - 0) * (1.0 - self.coord) * shown / r) + ((0.98) * (1.0 - 0) * (self.coord) * observed / r) + ((0.98) * 0 * s) + ((self.mut / 8))

            else:
                if r < 8:
                    if not (shown == observed == 0):
                        result = ((0.98) * (1.0 - self.cont) * (1.0 - self.coord) * shown / r) + ((0.98) * (1.0 - self.cont) * (self.coord) * observed / r) + ((0.98) * self.cont * s2) + ((self.mut / 8))
                    else:
                        result = ((0.98) * (1.0 - 0) * (1.0 - self.coord) * shown / r) + ((0.98) * (1.0 - 0) * (self.coord) * observed / r) + ((0.98) * 0 * s2) + ((self.mut / 8))
                else:
                    if not (shown == observed == 0):
                        result = ((0.98) * (1.0 - self.cont) * (1.0 - self.coord) * shown / r) + ((0.98) * (1.0 - self.cont) * (self.coord) * observed / r) + ((0.98) * self.cont * s3) + ((self.mut / 8))
                    else:
                        result = ((0.98) * (1.0 - 0) * (1.0 - self.coord) * shown / r) + ((0.98) * (1.0 - 0) * (self.coord) * observed / r) + ((0.98) * 0 * s3) + ((self.mut / 8))
            return result

        def choice(options, probs):
            probAcumuladas = list()
            aux = 0
            for p in probs:
                aux += p
                probAcumuladas.append(aux)
            r = random() * probAcumuladas[-1]
            op = bisect(probAcumuladas, r)
            return options[op]

        yield dict(zip(self.agents.keys(), self.signals))


        r = 1
        while True:
            eleccs = dict.fromkeys(self.agents.keys())
            for name, inst in self.agents.items():
                probs = [model(inst.mem_shown.count(op), inst.mem_observed.count(op), self.s[indx], self.s2[indx], self.s3[indx], r, name)
                         for indx, op in enumerate(self.signals)]
                eleccs[name] = choice(self.signals, probs)
            r += 1
            yield eleccs


    def play(self):
        gen_sens =  self.produce_signals()
        for n, round in enumerate(self.pairs):
            signals = next(gen_sens)
            self.memory.append(signals)

            for agent1, agent2 in round:
                self.agents[agent1].mem_observed.append(signals[agent2])
                self.agents[agent2].mem_observed.append(signals[agent1])
                self.agents[agent1].mem_shown.append(signals[agent1])
                self.agents[agent2].mem_shown.append(signals[agent2])

    class player():
        def __init__(self, menLen):
            self.mem_shown = deque(maxlen=menLen)
            self.mem_observed = deque(maxlen=menLen)

#Shannon entropy function
def entropy(lista):
    N = sum(lista)
    probs = (freq/N for freq in lista if freq>0)
    return -sum(x * math.log(x, 2) for x in probs)

#Function to randomize connectivity dynamic without repetition
def group(agents, n=7):
    all = set()
    for caso in permutations(agents):
        gen = zip(*[iter(caso)] * 2)
        gen = tuple(sorted(tuple(sorted(pair)) for pair in gen))
        all.add(gen)
    all = list(all)
    rand.shuffle(all)
    return all[:n]

def main():
    #Agents
    agents = [1, 2, 3, 4, 5, 6, 7, 8]
    #Variants
    signals = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8']
    #Pair composition
    pairs = [[(1, 2), (3, 4), (5, 6), (7, 8)],
             [(1, 3), (2, 4), (5, 7), (6, 8)],
             [(1, 4), (2, 3), (5, 8), (6, 7)],
             [(1, 5), (2, 6), (3, 7), (4, 8)],
             [(1, 6), (3, 8), (5, 2), (7, 4)],
             [(1, 7), (2, 8), (3, 5), (4, 6)],
             [(1, 8), (3, 6), (5, 4), (7, 2)]]
    # Randomize pair composition (only use the following two lines of code if you want to randomize pair composition):
    # network = group(agents)
    # pairs = [list(elem) for elem in network]
    # Memory length
    menLen = 3
    #Connectivity dynamic
    connectivity= 'Late connectivity'
    #Singleton distribution (variant quality distribution or variants' selctive value)
    s = [1, 0, 0, 0, 0, 0, 0, 0]
    # s = [0.9, 1, 1, 0.8, 0, 0.3, 0.3, 0]
    s2 = [1, 0, 0, 0, 0, 0, 0, 0]
    s3 = [1, 0, 0, 0, 0, 0, 0, 0]

    # Content bias ('cont'): no content bias=0.0, fully content biased population=1.0
    # Coordination bias ('coord'): fully egocentric=0.0, fully allocentric=1.0, neutral=0.5
    # mutation rate ('mut')
    #Setup for one parameter combination:
    samples = [{'cont': 0.2, 'coord': 0.5, 'mut': 0.02} for _ in range(1000)]
    #Setup for all parameter combinations (content bias and coordination bias):
    #samples = [
               # {'cont': 0.0, 'coord': 0.0, 'mut': 0.02},
               # {'cont': 0.1, 'coord': 0.0, 'mut': 0.02},
               # {'cont': 0.2, 'coord': 0.0, 'mut': 0.02},
               # {'cont': 0.3, 'coord': 0.0, 'mut': 0.02},
               # {'cont': 0.4, 'coord': 0.0, 'mut': 0.02},
               # {'cont': 0.5, 'coord': 0.0, 'mut': 0.02},
               # {'cont': 0.6, 'coord': 0.0, 'mut': 0.02},
               # {'cont': 0.7, 'coord': 0.0, 'mut': 0.02},
               # {'cont': 0.8, 'coord': 0.0, 'mut': 0.02},
               # {'cont': 0.9, 'coord': 0.0, 'mut': 0.02},
               # {'cont': 1.0, 'coord': 0.0, 'mut': 0.02},
               # {'cont': 0.0, 'coord': 0.1, 'mut': 0.02},
               # {'cont': 0.1, 'coord': 0.1, 'mut': 0.02},
               # {'cont': 0.2, 'coord': 0.1, 'mut': 0.02},
               # {'cont': 0.3, 'coord': 0.1, 'mut': 0.02},
               # {'cont': 0.4, 'coord': 0.1, 'mut': 0.02},
               # {'cont': 0.5, 'coord': 0.1, 'mut': 0.02},
               # {'cont': 0.6, 'coord': 0.1, 'mut': 0.02},
               # {'cont': 0.7, 'coord': 0.1, 'mut': 0.02},
               # {'cont': 0.8, 'coord': 0.1, 'mut': 0.02},
               # {'cont': 0.9, 'coord': 0.1, 'mut': 0.02},
               # {'cont': 1.0, 'coord': 0.1, 'mut': 0.02},
               # {'cont': 0.0, 'coord': 0.2, 'mut': 0.02},
               # {'cont': 0.1, 'coord': 0.2, 'mut': 0.02},
               # {'cont': 0.2, 'coord': 0.2, 'mut': 0.02},
               # {'cont': 0.3, 'coord': 0.2, 'mut': 0.02},
               # {'cont': 0.4, 'coord': 0.2, 'mut': 0.02},
               # {'cont': 0.5, 'coord': 0.2, 'mut': 0.02},
               # {'cont': 0.6, 'coord': 0.2, 'mut': 0.02},
               # {'cont': 0.7, 'coord': 0.2, 'mut': 0.02},
               # {'cont': 0.8, 'coord': 0.2, 'mut': 0.02},
               # {'cont': 0.9, 'coord': 0.2, 'mut': 0.02},
               # {'cont': 1.0, 'coord': 0.2, 'mut': 0.02},
               # {'cont': 0.0, 'coord': 0.3, 'mut': 0.02},
               # {'cont': 0.1, 'coord': 0.3, 'mut': 0.02},
               # {'cont': 0.2, 'coord': 0.3, 'mut': 0.02},
               # {'cont': 0.3, 'coord': 0.3, 'mut': 0.02},
               # {'cont': 0.4, 'coord': 0.3, 'mut': 0.02},
               # {'cont': 0.5, 'coord': 0.3, 'mut': 0.02},
               # {'cont': 0.6, 'coord': 0.3, 'mut': 0.02},
               # {'cont': 0.7, 'coord': 0.3, 'mut': 0.02},
               # {'cont': 0.8, 'coord': 0.3, 'mut': 0.02},
               # {'cont': 0.9, 'coord': 0.3, 'mut': 0.02},
               # {'cont': 1.0, 'coord': 0.3, 'mut': 0.02},
               # {'cont': 0.0, 'coord': 0.4, 'mut': 0.02},
               # {'cont': 0.1, 'coord': 0.4, 'mut': 0.02},
               # {'cont': 0.2, 'coord': 0.4, 'mut': 0.02},
               # {'cont': 0.3, 'coord': 0.4, 'mut': 0.02},
               # {'cont': 0.4, 'coord': 0.4, 'mut': 0.02},
               # {'cont': 0.5, 'coord': 0.4, 'mut': 0.02},
               # {'cont': 0.6, 'coord': 0.4, 'mut': 0.02},
               # {'cont': 0.7, 'coord': 0.4, 'mut': 0.02},
               # {'cont': 0.8, 'coord': 0.4, 'mut': 0.02},
               # {'cont': 0.9, 'coord': 0.4, 'mut': 0.02},
               # {'cont': 1.0, 'coord': 0.4, 'mut': 0.02},
               # {'cont': 0.0, 'coord': 0.5, 'mut': 0.02},
               # {'cont': 0.1, 'coord': 0.5, 'mut': 0.02},
               # {'cont': 0.2, 'coord': 0.5, 'mut': 0.02},
               # {'cont': 0.3, 'coord': 0.5, 'mut': 0.02},
               # {'cont': 0.4, 'coord': 0.5, 'mut': 0.02},
               # {'cont': 0.5, 'coord': 0.5, 'mut': 0.02},
               # {'cont': 0.6, 'coord': 0.5, 'mut': 0.02},
               # {'cont': 0.7, 'coord': 0.5, 'mut': 0.02},
               # {'cont': 0.8, 'coord': 0.5, 'mut': 0.02},
               # {'cont': 0.9, 'coord': 0.5, 'mut': 0.02},
               # {'cont': 1.0, 'coord': 0.5, 'mut': 0.02},
               # {'cont': 0.0, 'coord': 0.6, 'mut': 0.02},
               # {'cont': 0.1, 'coord': 0.6, 'mut': 0.02},
               # {'cont': 0.2, 'coord': 0.6, 'mut': 0.02},
               # {'cont': 0.3, 'coord': 0.6, 'mut': 0.02},
               # {'cont': 0.4, 'coord': 0.6, 'mut': 0.02},
               # {'cont': 0.5, 'coord': 0.6, 'mut': 0.02},
               # {'cont': 0.6, 'coord': 0.6, 'mut': 0.02},
               # {'cont': 0.7, 'coord': 0.6, 'mut': 0.02},
               # {'cont': 0.8, 'coord': 0.6, 'mut': 0.02},
               # {'cont': 0.9, 'coord': 0.6, 'mut': 0.02},
               # {'cont': 1.0, 'coord': 0.6, 'mut': 0.02},
               # {'cont': 0.0, 'coord': 0.7, 'mut': 0.02},
               # {'cont': 0.1, 'coord': 0.7, 'mut': 0.02},
               # {'cont': 0.2, 'coord': 0.7, 'mut': 0.02},
               # {'cont': 0.3, 'coord': 0.7, 'mut': 0.02},
               # {'cont': 0.4, 'coord': 0.7, 'mut': 0.02},
               # {'cont': 0.5, 'coord': 0.7, 'mut': 0.02},
               # {'cont': 0.6, 'coord': 0.7, 'mut': 0.02},
               # {'cont': 0.7, 'coord': 0.7, 'mut': 0.02},
               # {'cont': 0.8, 'coord': 0.7, 'mut': 0.02},
               # {'cont': 0.9, 'coord': 0.7, 'mut': 0.02},
               # {'cont': 1.0, 'coord': 0.7, 'mut': 0.02},
               # {'cont': 0.0, 'coord': 0.8, 'mut': 0.02},
               # {'cont': 0.1, 'coord': 0.8, 'mut': 0.02},
               # {'cont': 0.2, 'coord': 0.8, 'mut': 0.02},
               # {'cont': 0.3, 'coord': 0.8, 'mut': 0.02},
               # {'cont': 0.4, 'coord': 0.8, 'mut': 0.02},
               # {'cont': 0.5, 'coord': 0.8, 'mut': 0.02},
               # {'cont': 0.6, 'coord': 0.8, 'mut': 0.02},
               # {'cont': 0.7, 'coord': 0.8, 'mut': 0.02},
               # {'cont': 0.8, 'coord': 0.8, 'mut': 0.02},
               # {'cont': 0.9, 'coord': 0.8, 'mut': 0.02},
               # {'cont': 1.0, 'coord': 0.8, 'mut': 0.02},
               # {'cont': 0.0, 'coord': 0.9, 'mut': 0.02},
               # {'cont': 0.1, 'coord': 0.9, 'mut': 0.02},
               # {'cont': 0.2, 'coord': 0.9, 'mut': 0.02},
               # {'cont': 0.3, 'coord': 0.9, 'mut': 0.02},
               # {'cont': 0.4, 'coord': 0.9, 'mut': 0.02},
               # {'cont': 0.5, 'coord': 0.9, 'mut': 0.02},
               # {'cont': 0.6, 'coord': 0.9, 'mut': 0.02},
               # {'cont': 0.7, 'coord': 0.9, 'mut': 0.02},
               # {'cont': 0.8, 'coord': 0.9, 'mut': 0.02},
               # {'cont': 0.9, 'coord': 0.9, 'mut': 0.02},
               # {'cont': 1.0, 'coord': 0.9, 'mut': 0.02},
               # {'cont': 0.0, 'coord': 1.0, 'mut': 0.02},
               # {'cont': 0.1, 'coord': 1.0, 'mut': 0.02},
               # {'cont': 0.2, 'coord': 1.0, 'mut': 0.02},
               # {'cont': 0.3, 'coord': 1.0, 'mut': 0.02},
               # {'cont': 0.4, 'coord': 1.0, 'mut': 0.02},
               # {'cont': 0.5, 'coord': 1.0, 'mut': 0.02},
               # {'cont': 0.6, 'coord': 1.0, 'mut': 0.02},
               # {'cont': 0.7, 'coord': 1.0, 'mut': 0.02},
               # {'cont': 0.8, 'coord': 1.0, 'mut': 0.02},
               # {'cont': 0.9, 'coord': 1.0, 'mut': 0.02},
               # {'cont': 1.0, 'coord': 1.0, 'mut': 0.02}]
    #samples = [d for d in samples for _ in range(1000)]

    simulations = 1

    statistics = {agent:{sample:{signal:[0 for round in range(1, len(pairs) + 1)]
                                 for signal in signals}
                         for sample in range(len(samples))}
                  for agent in agents}

    for sample in range(len(samples)):
        # Use the following two lines of code to randomize the pair composition
        # network = group(agents)
        # pairs = [list(elem) for elem in network]
        for mu in range(len(samples)):
            for _ in range(simulations):
                game = Match(agents, menLen, pairs, signals, s, s2, s3, samples[mu]['cont'], samples[mu]['coord'], samples[mu]['mut'])
                game.play()
                for n, round in enumerate(game.memory):
                    for agent, signal in round.items():
                        statistics[agent][mu][signal][n] += 1

    with open('test.csv', 'wb') as csvfile:
            writer =csv.writer(csvfile, delimiter=';',
                        quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(['Sample', 'Agent', 'Memory', 'Generation', 'Connectivity', 'Content bias', 'Coordination bias', 'Mutation rate'] + signals +
                            ['Population signals'] + ['Entropy_population'] + ['Entropy_subpopulation_1'] + ['Entropy_subpopulation_2'] + ['Subpopulation_1 signals'] + ['Subpopulation_2 signals'])

            for agent in agents:
                for mu in range(len(samples)):
                    for round in range(1, len(pairs) + 1):
                        aux = [statistics[agent][mu][signal][round - 1] for signal in signals]
                        aux1 = [statistics[1][mu][signal][round - 1] for signal in signals]
                        aux2 = [statistics[2][mu][signal][round - 1] for signal in signals]
                        aux3 = [statistics[3][mu][signal][round - 1] for signal in signals]
                        aux4 = [statistics[4][mu][signal][round - 1] for signal in signals]
                        aux5 = [statistics[5][mu][signal][round - 1] for signal in signals]
                        aux6 = [statistics[6][mu][signal][round - 1] for signal in signals]
                        aux7 = [statistics[7][mu][signal][round - 1] for signal in signals]
                        aux8 = [statistics[8][mu][signal][round - 1] for signal in signals]

                        summation_pop = []

                        summation_subpop_1=[]
                        summation_subpop_2=[]


                        for i in range(len(aux1)):
                            summation_pop.append(aux1[i] + aux2[i] + aux3[i] + aux4[i] + aux5[i] + aux6[i] + aux7[i] + aux8[i])

                        for i in range(len(aux1)):
                            summation_subpop_1.append(aux1[i] + aux2[i] + aux3[i] + aux4[i])
                            summation_subpop_2.append(aux5[i] + aux6[i] + aux7[i] + aux8[i])

                        writer.writerow([mu + 1, agent, menLen, round, connectivity, samples[mu]['cont'], samples[mu]['coord'],
                                         samples[mu]['mut']] + aux + [summation_pop] + [entropy(summation_pop)] + [entropy(summation_subpop_1)] + [entropy(summation_subpop_2)] + [summation_subpop_1] + [summation_subpop_2])

if __name__ == '__main__':
    main()

#Pair composition:
#Early connectyvity
 #   pairs = [[(1, 2), (3, 4), (5, 6), (7, 8)],
 #           [(1, 4), (3, 2), (5, 8), (7, 6)],
 #           [(1, 6), (3, 8), (5, 2), (7, 4)],
 #           [(1, 8), (3, 6), (5, 4), (7, 2)],
 #           [(1, 3), (2, 4), (5, 7), (6, 8)],
 #           [(1, 5), (2, 6), (3, 7), (4, 8)],
 #           [(1, 7), (2, 8), (3, 5), (4, 6)]]
#Mid connectivity
 #   pairs = [[(1, 2), (3, 4), (5, 6), (7, 8)],
 #           [(1, 4), (2, 7), (3, 6), (5, 8)],
 #           [(1, 6), (4, 7), (2, 5), (3, 8)],
 #           [(1, 5), (3, 7), (2, 6), (4, 8)],
 #           [(1, 7), (5, 3), (2, 8), (6, 4)],
 #           [(1, 8), (3, 2), (7, 6), (5, 4)],
 #           [(1, 3), (5, 7), (2, 4), (6, 8)]]