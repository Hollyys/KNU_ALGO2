import random
import statistics
import math
from random import randrange

def simulate(n, t):
    N = n*n+2
    output = []

    for rot in range(0,t):
        data = []
        flag = [False for i in range(0, n * n)]  # 전부 닫힌상태

        for i in range(0, n * n):
            data.append(i)
        random.shuffle(data)

        ids = []
        size = []  # size[i]: size of tree rooted at i
        for idx in range(N):
            ids.append(idx)
            size.append(1)

        def root(i):
            while i != ids[i]:
                i = ids[i]
            return i

        def connected(p, q):
            return root(p) == root(q)

        def union(p, q):
            id1, id2 = root(p), root(q)
            if id1 == id2: return
            if size[id1] <= size[id2]:
                ids[id1] = id2
                size[id2] += size[id1]
            else:
                ids[id2] = id1
                size[id1] += size[id2]

        for i in range(0, n):
            union(i, n * n)
            union(n * (n - 1) + i, n * n + 1)

        count1 = 0

        while True:
            if (connected(n * n, n * n + 1) == True):
                count1 += 1
                ratio = count1 / (n * n)
                output.append(ratio)
                break

            flag[data[count1]] = True  # 열린상태 전환
            if data[count1] == 0: #구석1
                if flag[1] == True:
                    union(1, data[count1])
                if flag[n] == True:
                    union(n, data[count1])
            elif data[count1] == n - 1: #구석2
                if flag[n - 2] == True:
                    union(n - 2, data[count1])
                if flag[data[count1] + n] == True:
                    union(data[count1] + n, data[count1])
            elif data[count1] == n * (n - 1): #구석3
                if flag[data[count1] + 1] == True:
                    union(data[count1] + 1, data[count1])
                if flag[data[count1] - n] == True:
                    union(data[count1] - n, data[count1])
            elif data[count1] == n * n - 1: #구석4
                if flag[data[count1] - 1] == True:
                    union(data[count1] - 1, data[count1])
                if flag[data[count1] - n] == True:
                    union(data[count1] - n, data[count1])  # 구석 네군데
            elif data[count1] % n == 0 and data[count1] < n*(n-1):  # 첫번째 행
                if flag[data[count1] + 1] == True:
                    union(data[count1] + 1, data[count1])
                if flag[data[count1] - n] == True:
                    union(data[count1] - n, data[count1])
                if flag[data[count1] + n] == True:
                    union(data[count1] + n, data[count1])
            elif data[count1] % n == (n - 1) and data[count1] < n*(n-1):  # 마지막 행
                if flag[data[count1] - 1] == True:
                    union(data[count1] - 1, data[count1])
                if flag[data[count1] - n] == True:
                    union(data[count1] - n, data[count1])
                if flag[data[count1] + n] == True:
                    union(data[count1] + n, data[count1])
            elif data[count1] < n:  # 첫번째 열 가운데
                if flag[data[count1] + n] == True:
                    union(data[count1] + n, data[count1])
                if flag[data[count1] - 1] == True:
                    union(data[count1] - 1, data[count1])
                if flag[data[count1] + 1] == True:
                    union(data[count1] + 1, data[count1])
            elif data[count1] > n * (n - 1) and data[count1] < n * n:  # 마지막 열 가운데
                if flag[data[count1] - n] == True:
                    union(data[count1] - n, data[count1])
                if flag[data[count1] - 1] == True:
                    union(data[count1] - 1, data[count1])
                if flag[data[count1] + 1] == True:
                    union(data[count1] + 1, data[count1])
            else:  # 가운데 원소
                if flag[data[count1] - n] == True:
                    union(data[count1] - n, data[count1])
                if flag[data[count1] + n] == True:
                    union(data[count1] + n, data[count1])
                if flag[data[count1] - 1] == True:
                    union(data[count1] - 1, data[count1])
                if flag[data[count1] + 1] == True:
                    union(data[count1] + 1, data[count1])
            count1 += 1

    mean = statistics.mean(output)
    stdev = statistics.stdev(output)
    ci1 = mean - 1.96 * stdev / math.sqrt(t)
    ci2 = mean + 1.96 * stdev / math.sqrt(t)
    print('mean                    = %f' % mean)
    print('stdev                   = %f' % stdev)
    print('95% confidence interval = [{}, {}]'.format(ci1, ci2))

    return mean, stdev
