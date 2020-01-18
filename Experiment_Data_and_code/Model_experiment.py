
from __future__ import division
from random import random, sample
import random as rand
from bisect import bisect
from collections import deque
from itertools import permutations
import csv
import math

class Match():
    def __init__(self, agents, menLen, pairs, signals, s, s2, cont, coord, mut):
        self.pairs = pairs
        self.signals = signals
        self.s = s
        self.s2 = s2
        self.cont = cont
        self.coord = coord
        self.mut = mut
        # self.agents=agents
        self.agents = {name: Match.player(menLen)
                       for pair in pairs[0]
                       for name in pair}
        self.memory = list()


    def produce_signals(self):

        def model(shown, observed, s, s2, r, name):
            if name <= 8:
                if r < 5:
                    if not (shown == observed == 0):
                        result = ((0.98) * (1.0 - self.cont) * (1.0 - self.coord) * shown / r) + ((0.98) * (1.0 - self.cont) * (self.coord) * observed / r) + ((0.98) * self.cont * s) + ((self.mut / 8))
                    else:
                        result = ((0.98) * (1.0 - 0) * (1.0 - self.coord) * shown / r) + ((0.98) * (1.0 - 0) * (self.coord) * observed / r) + ((0.98) * 0 * s) + ((self.mut / 8))
                else:
                    if not (shown == observed == 0):
                        result = ((0.98) * (1.0 - self.cont) * (1.0 - self.coord) * shown / r) + ((0.98) * (1.0 - self.cont) * (self.coord) * observed / r) + ((0.98) * self.cont * s2) + ((self.mut / 8))
                    else:
                        result = ((0.98) * (1.0 - 0) * (1.0 - self.coord) * shown / r) + ((0.98) * (1.0 - 0) * (self.coord) * observed / r) + ((0.98) * 0 * s2) + ((self.mut / 8))

            else:
                if r < 5:
                    if not (shown == observed == 0):
                        result = ((0.98) * (1.0 - self.cont) * (1.0 - self.coord) * shown / r) + ((0.98) * (1.0 - self.cont) * (self.coord) * observed / r) + ((0.98) * self.cont * s) + ((self.mut / 8))
                    else:
                        result = ((0.98) * (1.0 - 0) * (1.0 - self.coord) * shown / r) + ((0.98) * (1.0 - 0) * (self.coord) * observed / r) + ((0.98) * 0 * s) + ((self.mut / 8))
                else:
                    if not (shown == observed == 0):
                        result = ((0.98) * (1.0 - self.cont) * (1.0 - self.coord) * shown / r) + ((0.98) * (1.0 - self.cont) * (self.coord) * observed / r) + ((0.98) * self.cont * s2) + ((self.mut / 8))
                    else:
                        result = ((0.98) * (1.0 - 0) * (1.0 - self.coord) * shown / r) + ((0.98) * (1.0 - 0) * (self.coord) * observed / r) + ((0.98) * 0 * s2) + ((self.mut / 8))
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
                probs = [model(inst.mem_shown.count(op), inst.mem_observed.count(op), self.s[indx], self.s2[indx], r, name)
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
    agents = [1, 2, 3, 4]
    #Variants
    signals = ['S1', 'S2', 'S3', 'S4']
    #Pair composition
    # pairs = [[(1, 2), (3, 4)],
    #          [(1, 2), (3, 4)],
    #          [(1 , 4), (2,3)],
    #          [(1, 3),(2,4)],
    #          [(1, 2),(3,4)]]
    pairs = [[(1, 2), (3, 4)],
             [(1, 4), (2, 3)],
             [(1 , 3), (2,4)],
             [(1, 2),(3,4)],
             [(1, 2),(3,4)]]
    # Randomize pair composition (only use the following two lines of code if you want to randomize pair composition):
    # network = group(agents)
    # pairs = [list(elem) for elem in network]
    # Memory length
    menLen = 3
    #Connectivity dynamic
    connectivity= 'Sim_Early'
    #Singleton distribution (variant quality distribution or variants' selctive value)
    s = [1, 0, 0, 0]
    s2 = [1, 0, 0, 0]


    # Content bias ('cont'): no content bias=0.0, fully content biased population=1.0
    # Coordination bias ('coord'): fully egocentric=0.0, fully allocentric=1.0, neutral=0.5
    # mutation rate ('mut')
    #Setup for one parameter combination:
    # samples = [{'cont': 0.2, 'coord': 0.5, 'mut': 0.02} for _ in range(100)]
    #Setup for all parameter combinations (content bias and coordination bias):
    samples = [
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
               {'cont': 0.0, 'coord': 0.5, 'mut': 0.02},
               {'cont': 0.1, 'coord': 0.5, 'mut': 0.02},
               {'cont': 0.2, 'coord': 0.5, 'mut': 0.02},
               {'cont': 0.3, 'coord': 0.5, 'mut': 0.02},
               {'cont': 0.4, 'coord': 0.5, 'mut': 0.02},
               {'cont': 0.5, 'coord': 0.5, 'mut': 0.02},
               {'cont': 0.6, 'coord': 0.5, 'mut': 0.02},
               {'cont': 0.7, 'coord': 0.5, 'mut': 0.02},
               {'cont': 0.8, 'coord': 0.5, 'mut': 0.02},
               {'cont': 0.9, 'coord': 0.5, 'mut': 0.02},
               {'cont': 1.0, 'coord': 0.5, 'mut': 0.02}]
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
               #{'cont': 0.7, 'coord': 1.0, 'mut': 0.02}],
               # {'cont': 0.8, 'coord': 1.0, 'mut': 0.02},
               # {'cont': 0.9, 'coord': 1.0, 'mut': 0.02},
               # {'cont': 1.0, 'coord': 1.0, 'mut': 0.02}]
    samples = [d for d in samples for _ in range(1)]

    simulations = 100

    statistics = {
        sim: {
            agent: {
                sample: {
                    signal: [0 for round in range(1, len(pairs) + 1)]
                    for signal in signals
                }
                for sample in range(len(samples))
            }
            for agent in agents
        }
        for sim in range(simulations)
    }

    for sim in range(simulations):
            for mu in range(len(samples)):
                    game = Match(agents, menLen, pairs, signals, s, s2, samples[mu]['cont'], samples[mu]['coord'], samples[mu]['mut'])
                    game.play()
                    for n, round in enumerate(game.memory):
                        for agent, signal in round.items():
                            statistics[sim][agent][mu][signal][n] += 1

    with open('Sim_Early.csv', 'wb') as csvfile:
            writer =csv.writer(csvfile, delimiter=',',
                        quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(['Simulation','Sample', 'Agent', 'Memory', 'Generation', 'Connectivity', 'Content bias', 'Coordination bias', 'Mutation rate'] + signals +
                            ['Population signals'] + ['Entropy_population'])

            for agent in agents:
                for sim in range(simulations):
                    for mu in range(len(samples)):
                        for round in range(1, len(pairs) + 1):
                            aux = [statistics[sim][agent][mu][signal][round - 1] for signal in signals]
                            aux1 = [statistics[sim][1][mu][signal][round - 1] for signal in signals]
                            aux2 = [statistics[sim][2][mu][signal][round - 1] for signal in signals]
                            aux3 = [statistics[sim][3][mu][signal][round - 1] for signal in signals]
                            aux4 = [statistics[sim][4][mu][signal][round - 1] for signal in signals]

                            summation_pop = []

                            summation_subpop_1=[]
                            summation_subpop_2=[]


                            for i in range(len(aux1)):
                                summation_pop.append(aux1[i] + aux2[i] + aux3[i] + aux4[i])


                            writer.writerow([sim+1,mu + 1, agent, menLen, round, connectivity, samples[mu]['cont'], samples[mu]['coord'],
                                         samples[mu]['mut']] + aux + [summation_pop] + [entropy(summation_pop)])

if __name__ == '__main__':
    main()
