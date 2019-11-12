from __future__ import division
from random import random, sample
import random as rand
from bisect import bisect
from collections import deque, Counter
from itertools import permutations
import csv
import math
from skbio.diversity.alpha import brillouin_d, margalef, simpson, simpson_e, observed_otus, shannon

si_1 = rand.sample([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0], 8)

s_initial = {
    1: si_1,
    2: si_1,
    3: si_1,
    4: si_1,
    5: si_1,
    6: si_1,
    7: si_1,
    8: si_1,
}

cf_pos = 1.0
cf_neg = 0.5

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
        self.sigma = sigma[:]  # Hacer copia para que cada jugador tenga la suya
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

    ## ESTA FUNCION ES NUEVA COMPLETAMENTE,
    def choose(self, r):
        # Esta parte del código se extrajo de Partida.generar_senales()
        # y se ha adaptado
        probs = [
            self.with_b(
                self.mem_shown[op], self.mem_observed[op], r, indx
            )
            for indx, op in enumerate(self.signals)
        ]
        elecc = choice(self.signals, probs)

        # Esta parte es la que modifica el sigma. Se puede quitar por
        # completo y el código debería ser equivalente funcionalmente
        # al que teníamos antes (y al originalmente suministrado por el usuario)
        aux = [ (elecc==signali)+0 for signali in self.signals ]
        if aux == s_initial[self.name]:
            self.sigma = [x * cf_pos for x in self.sigma]
        else:
            self.sigma = [x * cf_neg for x in self.sigma]
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

def group(agents, n=7):
    todos = set()
    for caso in permutations(agents):
        gen = list(zip(*[iter(caso)] * 2))
        gen = tuple(sorted(tuple(sorted(pair)) for pair in gen))
        todos.add(gen)
    todos = list(todos)
    rand.shuffle(todos)
    return todos[:n]

# El resto no se ha tocado
def main():
    agents = [1, 2, 3, 4, 5, 6, 7, 8]
    signals = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8']

    network = group(agents)
    pairs = [list(elem) for elem in network]

    menLen = 3
    condition = "Homogeneity PR W"

    ####SIGMAS####
    s1 = rand.sample([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0], 8)
    s2 = s1
    sigmas = {1: s1, 2: s1, 3: s1, 4: s1, 5: s2, 6: s2, 7: s2, 8: s2}

    #samples = [{"b": 1.0, "x": 0.5, "m": 0.02}]

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

    simulations = 250

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
        network = group(agents)
        pairs = [list(elem) for elem in network]
        s1 = rand.sample([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0], 8)
        s2 = s1
        sigmas = {1: s1, 2: s1, 3: s1, 4: s1, 5: s2, 6: s2, 7: s2, 8: s2}
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

    with open('homogeneity_PR_W.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=';',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(['Simulation', 'Sample', 'Agent', 'Memory', 'Generation', 'Condition', 'Content bias',
                             'Coordination bias', 'Mutation rate'] + signals +
                            ['Population signals'] + ['Entropy_population'] + ['Entropy_subpopulation_1'] + [
                                'Entropy_subpopulation_2'] + ['Subpopulation_1 signals'] + ['Subpopulation_2 signals']
                            + ['Brillouin_population'] + ['Margalef_population'] + ['Simpson_population'] + [
                                'Simpson_e_population'] + ['Richness'])

            # Creando listas que contienen la produccion de cada senal: para toda la poblacion (aux) y para cada jugador (auxn)
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

                            # Lista que contiene los sumatorios de cada tipo de senales producidas a nivel de la poblacion global en cada muestra y ronda
                            summation_pop = []
                            # Lista que contiene los sumatorios de cada tipo de senales producidas a nivel de subpoblacion en cada muestra y ronda
                            summation_subpop_1 = []
                            summation_subpop_2 = []

                            # Sumando las senales de cada tipo
                            for i in range(len(aux1)):
                                # A nivel de la poblacion
                                summation_pop.append(
                                    aux1[i] + aux2[i] + aux3[i] + aux4[i] + aux5[i] + aux6[i] + aux7[i] + aux8[i])
                                # A nivel de las subpoblaciones
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