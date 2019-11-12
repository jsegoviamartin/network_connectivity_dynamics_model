from __future__ import division
from random import random, sample
import random as rand
from bisect import bisect
from collections import deque, Counter
from itertools import permutations
import csv
import math
from skbio.diversity.alpha import brillouin_d, margalef, simpson, simpson_e, observed_otus, shannon

## ORIGINAL VALUE SYSTEM (SIGMA): EACH AGENT HAS ITS OWN ONE (IT REMAINS THE SAME OVER ROUNDS)
s_initial = {
    1: [1, 1, 0, 0, 0, 0, 0, 0],
    2: [1, 1, 0, 0, 0, 0, 0, 0],
    3: [1, 1, 0, 0, 0, 0, 0, 0],
    4: [1, 1, 0, 0, 0, 0, 0, 0],
    5: [0, 0, 0, 0, 0, 0, 1, 1],
    6: [0, 0, 0, 0, 0, 0, 1, 1],
    7: [0, 0, 0, 0, 0, 0, 1, 1],
    8: [0, 0, 0, 0, 0, 0, 1, 1],
}

## LEVEL OF INSTITUTIONAL REINFORCEMENT
cf_pos = 1.0
cf_neg = 0.5

# CHOICE FUNCTION (CUMMULATIVE PROBABILITIES)
def choice(opciones, probs):
    probAcumuladas = list()
    aux = 0
    for p in probs:
        aux += p
        probAcumuladas.append(aux)
    r = random() * probAcumuladas[-1]
    op = bisect(probAcumuladas, r)
    return opciones[op]


class Agent:
    def __init__(self, name, signals, sigma, cont, coord, mut, menLen):
        self.name = name
        self.signals = signals
        self.mem_shown = {signal: 0 for signal in signals}
        self.mem_observed = {signal: 0 for signal in signals}
        self.__mem_shown = deque(maxlen=menLen)
        self.__mem_observed = deque(maxlen=menLen)
        self.sigma = sigma[:]  # Make a unique copy of sigma for each agent
        self.cont = cont
        self.coord = coord
        self.mut = mut

    def recall(self, v_shown, v_observed):
        self.__mem_shown.append(v_shown)
        self.__mem_observed.append(v_observed)
        v_shown = Counter(self.__mem_shown)
        v_observed = Counter(self.__mem_observed)
        self.mem_shown = { signal: v_shown.get(signal, 0) for signal in self.signals }
        self.mem_observed = { signal: v_observed.get(signal, 0) for signal in self.signals }

    def __str__(self):
        return "Agent_{}".format(self.name)

    def with_b(self, shown, observed, r, idx):
        if not (shown == observed == 0):
            result = (
                ((0.98) * (1.0 - self.cont) * (1.0 - self.coord) * shown / r)
                + ((0.98) * (1.0 - self.cont) * (self.coord) * observed / r)
                + ((0.98) * self.cont * self.sigma[idx])
                + ((self.mut / 8))
            )
        else:
            result = (
                ((0.98) * (1.0 - 0) * (1.0 - self.coord) * shown / r)
                + ((0.98) * (1.0 - 0) * (self.coord) * observed / r)
                + ((0.98) * 0 * self.sigma[idx])
                + ((self.mut / 8))
            )
        return result

    ## CHOOSE FUNCTION (VARIANT SELECTION)
    def choose(self, r):
        probs = [
            self.with_b(
                self.mem_shown[op], self.mem_observed[op], r, indx
            )
            for indx, op in enumerate(self.signals)
        ]
        elecc = choice(self.signals, probs)

        # FUNCTION TO MODIFY VALUE SYSTEM ACCORDING TO AGENT'S CHOICES  (it modifies agents' self.sigma)
        aux = [ (elecc==signali)+0 for signali in self.signals ]
        if aux == s_initial[self.name]:
            self.sigma = [x * cf_pos for x in self.sigma]
        else:
            self.sigma = [x * cf_neg for x in self.sigma]
        # E.G. HERE WE ARE CHECKING THE EVOLUTION OF THE VALUE SYSTEM (self.sigma) OF AGENT 1, ACCORDING TO ITS ACTUAL VARIANT CHOICE (aux)        if self.name == 1:
        # if self.name == 1:
        #     print(aux)
        #     print(self.sigma)
        return elecc


class Match:
    def __init__(self, agents, pairs, signals, sigmas, cont, coord, mut, menLen):
        self.pairs = pairs
        self.signals = signals
        self.agents = {
            name: Agent(name, signals, sigmas[name], cont, coord, mut, menLen)
            for name in agents
        }
        self.memory = list()
        self.entropy = float()

    def produce_signals(self):
        ## NUEVO. Función muy simplificada al extraerse al Jugador la mayor parte
        yield dict(zip(self.agents, self.signals))
        r = 1
        while True:
            eleccs = {}
            for agent in self.agents.values():
                eleccs[agent.name] = agent.choose(r)
            r += 1
            yield eleccs

    def play(self):
        gen_sens = self.produce_signals()
        for round in self.pairs:
            signals = next(gen_sens)
            self.memory.append(signals)
            for agent1, agent2 in round:
                self.agents[agent1].recall(v_observed=signals[agent2], v_shown=signals[agent1])
                self.agents[agent2].recall(v_observed=signals[agent1], v_shown=signals[agent2])

#Shannon entropy function
def entropy(lista):
    N = sum(lista)
    probs = (freq/N for freq in lista if freq>0)
    return -sum(x * math.log(x, 2) for x in probs)

#Function to randomize connectivity dynamic without repetition
def group(agents, n=7):
    todos = set()
    for caso in permutations(agents):
        gen = list(zip(*[iter(caso)] * 2))
        gen = tuple(sorted(tuple(sorted(pair)) for pair in gen))
        todos.add(gen)
    todos = list(todos)
    rand.shuffle(todos)
    return todos[:n]


def main():
    # Agents
    agents = [1, 2, 3, 4, 5, 6, 7, 8]
    # Variants
    signals = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8']
    # Pair composition
    # Randomize pair composition:
    network = group(agents)
    pairs = [list(elem) for elem in network]
    # Memory length
    menLen = 3
    # Condition
    condition = "Heterogeneity C W"

    #### STRUCTURE OF VALUE SYSTEMS IN THE MICRO-SOCIETY (each value system (s1, s2, etc...) is assigned an agent):
    #### class Match, in the initialization, creates "agents" and passes the parameters to each agent,
    #### (including their sigmas). For this reason, a dictionary containig keys (agents' names ("name") and
    #### values (sigmas), is required
    s1 = [1, 1, 0, 0, 0, 0, 0, 0]
    s2 = [0, 0, 0, 0, 0, 0, 1, 1]
    sigmas = {1: s1, 2: s1, 3: s1, 4: s1, 5: s2, 6: s2, 7: s2, 8: s2}

    # Content bias ('cont'): no content bias=0.0, fully content biased population=1.0
    # Coordination bias ('coord'): fully egocentric=0.0, fully allocentric=1.0, neutral=0.5
    # mutation rate ('mut')
    # Setup for one parameter combination:
    #samples = [{'cont': 0.2, 'coord': 0.5, 'mut': 0.02} for _ in range(100)]
    # Setup for all parameter combinations (content bias and coordination bias):
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
        # {'cont': 1.0, 'coord': 0.0, 'mut': 0.02}]
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
        # {'cont': 0.7, 'coord': 1.0, 'mut': 0.02},
        # {'cont': 0.8, 'coord': 1.0, 'mut': 0.02},
        # {'cont': 0.9, 'coord': 1.0, 'mut': 0.02},
        # {'cont': 1.0, 'coord': 1.0, 'mut': 0.02}]
    samples = [d for d in samples for _ in range(1)]

    # Number of runs (simulations)
    simulations = 250

    # Generating statistics
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

    # Running The Game (game.play)
    for sim in range(simulations):
        network = group(agents)
        pairs = [list(elem) for elem in network]
        for mu in range(len(samples)):
            game = Match(
                agents,
                pairs,
                signals,
                sigmas,
                samples[mu]["cont"],
                samples[mu]["coord"],
                samples[mu]["mut"],
                menLen
            )
            game.play()
            for n, round in enumerate(game.memory):
                for agent, signal in round.items():
                    statistics[sim][agent][mu][signal][n] += 1

    # Writing data
    with open('heterogeneity_C_W.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=';',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(['Simulation', 'Sample', 'Agent', 'Memory', 'Generation', 'Condition', 'Content bias',
                             'Coordination bias', 'Mutation rate'] + signals +
                            ['Population signals'] + ['Entropy_population'] + ['Entropy_subpopulation_1'] + [
                                'Entropy_subpopulation_2'] + ['Subpopulation_1 signals'] + ['Subpopulation_2 signals']
                            + ['Brillouin_population'] + ['Margalef_population'] + ['Simpson_population'] + [
                                'Simpson_e_population'] + ['Richness'])

            # Creating lists that contain signals' production
            for agent in agents:
                for sim in range(simulations):
                    for mu in range(len(samples)):
                        for round in range(1, len(pairs) + 1):
                            aux = [statistics[sim][agent][mu][signal][round - 1] for signal in signals]
                            aux1 = [statistics[sim][1][mu][signal][round - 1] for signal in signals]
                            aux2 = [statistics[sim][2][mu][signal][round - 1] for signal in signals]
                            aux3 = [statistics[sim][3][mu][signal][round - 1] for signal in signals]
                            aux4 = [statistics[sim][4][mu][signal][round - 1] for signal in signals]
                            aux5 = [statistics[sim][5][mu][signal][round - 1] for signal in signals]
                            aux6 = [statistics[sim][6][mu][signal][round - 1] for signal in signals]
                            aux7 = [statistics[sim][7][mu][signal][round - 1] for signal in signals]
                            aux8 = [statistics[sim][8][mu][signal][round - 1] for signal in signals]

                            # List that contains the sum of produced variants in the population for each simulation and round
                            summation_pop = []
                            # List that contains the sum of produced vatiants in each population for each simulation and round
                            summation_subpop_1 = []
                            summation_subpop_2 = []

                            # Summing variants
                            for i in range(len(aux1)):
                                # In teh population
                                summation_pop.append(
                                    aux1[i] + aux2[i] + aux3[i] + aux4[i] + aux5[i] + aux6[i] + aux7[i] + aux8[i])
                                # In each subpopulation
                            for i in range(len(aux1)):
                                summation_subpop_1.append(aux1[i] + aux2[i] + aux3[i] + aux4[i])
                                summation_subpop_2.append(aux5[i] + aux6[i] + aux7[i] + aux8[i])

                            writer.writerow([sim + 1, mu + 1, agent, menLen, round, condition, samples[mu]['cont'],
                                             samples[mu]['coord'],
                                             samples[mu]['mut']] + aux + [summation_pop] + [entropy(summation_pop)] + [
                                                entropy(summation_subpop_1)] + [entropy(summation_subpop_2)] + [
                                                summation_subpop_1] + [summation_subpop_2]
                                            + [brillouin_d(summation_pop)] + [margalef(summation_pop)] + [
                                                simpson(summation_pop)] + [simpson_e(summation_pop)] + [
                                                observed_otus(summation_pop) / 8])
if __name__ == '__main__':
    main()