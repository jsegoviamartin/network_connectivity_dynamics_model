# Code to create network visualizations
# as described in Figure 1 in Segovia Martin, J., Walker, B., Fay, N. & Tamariz, M. (2019)

from itertools import combinations
import matplotlib.pyplot as plt
import networkx as nx
import colored
from colour import Color
import imageio
from PIL import Image



####Network of nodes (agents) and edges(interactions)

#Low isolation
# pairs = [[("1", "2"), ("3", "4"), ("5", "6"), ("7", "8")],
#             [("1", "4"), ("3", "2"), ("5", "8"), ("7", "6")],
#             [("1", "6"), ("3", "8"), ("5", "2"), ("7", "4")],
#             [("1", "8"), ("3", "6"), ("5", "4"), ("7", "2")],
#             [("1", "3"), ("2", "4"), ("5", "7"), ("6", "8")],
#             [("1", "5"), ("2", "6"), ("3", "7"), ("4", "8")],
#             [("1", "7"), ("2", "8"), ("3", "5"), ("4", "6")]]

#Mid isolation
pairs = [[("1", "2"), ("3", "4"), ("5", "6"), ("7", "8")],
            [("1", "4"), ("2", "7"), ("3", "6"), ("5", "8")],
            [("1", "6"), ("4", "7"), ("2", "5"), ("3", "8")],
            [("1", "5"), ("3", "7"), ("2", "6"), ("4", "8")],
            [("1", "7"), ("5", "3"), ("2", "8"), ("6", "4")],
            [("1", "8"), ("3", "2"), ("7", "6"), ("5", "4")],
            [("1", "3"), ("5", "7"), ("2", "4"), ("6", "8")]]

#High isolation network
# pairs = [[("1", "2"), ("3", "4"), ("5", "6"), ("7", "8")],
#         [("1", "3"), ("2", "4"), ("5", "7"), ("6", "8")],
#         [("1", "4"), ("2", "3"), ("5", "8"), ("6", "7")],
#         [("1", "5"), ("2", "6"), ("3", "7"), ("4", "8")],
#         [("1", "6"), ("3", "8"), ("5", "2"), ("7", "4")],
#         [("1", "7"), ("2", "8"), ("3", "5"), ("4", "6")],
#         [("1", "8"), ("3", "6"), ("5", "4"), ("7", "2")]]
#
# nodes = ['1', '2', '3', '4', '5', '6', '7', '8']
# edges = combinations(nodes, 2)
# g = nx.Graph()
# g.add_nodes_from(nodes)

# g.add_edges_from(pairs[0])
# nx.draw(g)
# plt.savefig("image01.png") # save as png
# plt.show() # display
# g.add_edges_from(pairs[1])
# nx.draw(g)
# plt.savefig("image02.png") # save as png
# plt.show() # display
# g.add_edges_from(pairs[2])
# nx.draw(g)
# plt.savefig("image03.png") # save as png
# plt.show() # display
# g.add_edges_from(pairs[3])
# nx.draw(g)
# plt.savefig("image04.png") # save as png
# plt.show() # display
# g.add_edges_from(pairs[4])
# nx.draw(g)
# plt.savefig("image05.png") # save as png
# plt.show() # display
# g.add_edges_from(pairs[5])
# nx.draw(g)
# plt.savefig("image06.png") # save as png
# plt.show() # display
# g.add_edges_from(pairs[6])
# nx.draw(g)
# plt.savefig("image07.png") # save as png
# plt.show() # display


######Network of nodes (color and size)######
# # nodes = {"1": 50, "2": 50, "3": 50, "4": 50, "5": 8, "6": 8, "7": 8, "8": 8}
# # nodes = {"1": 16, "2": 8, "3": 0, "4": 16, "5": 8, "6": 8, "7": 8, "8": 0}
# # nodes = {"1": 32, "2": 0, "3": 0, "4": 24, "5": 0, "6": 0, "7": 8, "8": 0}
# # nodes = {"1": 56, "2": 0, "3": 0, "4": 8, "5": 0, "6": 0, "7": 0, "8": 0}
# # nodes = {"1": 64, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0, "8": 0}
# edges = combinations(nodes, 2)
# g = nx.Graph()
# g.add_nodes_from(nodes)
# g.add_edges_from(pairs[0])
# g.add_edges_from(pairs[1])
# node_sizes =[]
# color_map=[]
# for k in nodes:
#     if  0 <= nodes[k] <= 10:
#         color_map.append('#e0ffff')
#         node_sizes.append(100)
#     if 10 < nodes[k] <= 20:
#         color_map.append('#afeeee')
#         node_sizes.append(200)
#     if 20 < nodes[k] <= 30:
#         color_map.append('#87cefa')
#         node_sizes.append(300)
#     if 30 < nodes[k] <= 40:
#         color_map.append('#00bfff')
#         node_sizes.append(400)
#     if 40 < nodes[k] <= 50:
#         color_map.append('#1e90ff')
#         node_sizes.append(500)
#     if 50 < nodes[k] <= 60:
#         color_map.append('#0000cd')
#         node_sizes.append(600)
#     if 60 < nodes[k] <= 70:
#         color_map.append('#191970')
#         node_sizes.append(700)
# nx.draw(g, node_color=color_map, with_labels=True, node_size=node_sizes)
# plt.show()


####Spread of variants
nodes = {"1": 1, "2": 1, "3": 1, "4": 1, "5": 1, "6": 1, "7": 1, "8": 1}
edges = combinations(nodes, 2)
g = nx.Graph()
g.add_nodes_from(nodes)
g.add_edges_from(pairs[0])
g.add_edges_from(pairs[1])
g.add_edges_from(pairs[2])
g.add_edges_from(pairs[3])
g.add_edges_from(pairs[4])
g.add_edges_from(pairs[5])
# g.add_edges_from(pairs[6])
node_sizes =[]
color_map=[]
for k in nodes:
    if  0 <= nodes[k] <= 1:
        color_map.append('red')
        node_sizes.append(1000)
    if 1 < nodes[k] <= 2:
        color_map.append('blue')
        node_sizes.append(600)

nx.draw(g, node_color=color_map, with_labels=True, node_size=node_sizes)
plt.show()
