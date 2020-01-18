import math
import csv


# Shannon entropy function
def entropy(lista):
    N = sum(lista)
    probs = (freq / N for freq in lista if freq > 0)
    return -sum(x * math.log(x, 2) for x in probs)

#Open experiment data and obtaining summation_pop(list of signal frequency produced by the community by round)
with open('experiment_data_late_r.csv', 'r', encoding='utf8', errors='ignore') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    community = []
    condition = []
    order = []
    category = []
    concept = []
    rounds = []
    summation_pop = []
    header = next(reader)
    rows = [header] + [[row[0], row[1], row[2], row[3], row[4], int(row[5]), int(row[6]), int(row[7]), int(row[8]), int(row[9]), int(row[10])] for row in reader]
    # for row in rows:
    #     print (row)
    for row in rows:
        if row != ['Community','Condition', 'Order', 'Category','Concept','Round', 'S1', 'S2', 'S3', 'S4', 'S5']:
            summation_pop.append(row)
            community.append(row[0])
            condition.append(row[1])
            order.append(row[2])
            category.append(row[3])
            concept.append(row[4])
            rounds.append(row[5])
    print(summation_pop)
    for list in summation_pop:
        del list[0:6]

    print (summation_pop)

#Computing Shannon entropy
bits=[]
for i in summation_pop:
    bits.append(entropy(i))

#Writing csv file ready for R analisys
rows = zip(community, condition, order, category, concept, rounds,summation_pop,bits)
with open('experiment_entropy_late.csv', 'w', newline='') as csvfile:
                writer =csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(['Community','Condition', 'Order', 'Category','Concept','Round','Population signals','Entropy_population'])
                for row in rows:
                    writer.writerow(row)

