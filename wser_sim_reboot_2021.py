from collections import Counter
import numpy as np
import statistics as stats

years = np.arange(1,9)
tickets = [2**(n-1) for n in np.arange(1,9)]
counts = [3319,1063,721,515,328,186,59,18]
spots = 220
sims_count = 10**5

entries = [l for s in [[years[a] for x in range(counts[a])] 
                for a in range(len(years))] for l in s]

probs = [l for s in [[tickets[a]/sum([a * b for a, b in zip(tickets, counts)]) 
            for x in range(counts[a])] for a in range(len(years))] for l in s]

summary = [Counter(np.random.choice(a = entries, size = spots, 
           replace = False, p = probs)) for x in range(sims_count)]

lol = [[x.get(i) for x in summary] for i in range(1,9)]
tc = sum([(x*y) for x, y in zip(tickets, counts)])

print('2022 Western States lottery simulator')
print('# of sims:   ',f"{sims_count:,}")
print('spots available: ',f"{spots}")
print('ticket count: ',f"{tc:,}")
print('')
print('years','\t','n','\t','min','\t','max','\t','avg','\t','prob')
for x in range(len(lol)):
    print(x+1,'\t',counts[x],'\t',int(round(min(lol[x]),0)),'\t', int(round(max(lol[x]),0)),'\t',
            int(round(stats.mean(lol[x]),0)),'\t', str(round(round(stats.mean(lol[x])/counts[x],3)*100,3))+'%')
