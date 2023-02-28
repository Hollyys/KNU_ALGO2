import math

angle_flag = []

# Merge a[lo ~ mid] with a[mid+1 ~ hi], using the extra space aux[]
def merge(a, b, aux1, aux2, lo, mid, hi):
    # Copy elements in a[] to the auxiliary array aux[]
    for k in range(lo, hi + 1):
        aux1[k] = a[k]
        aux2[k] = b[k]

    i, j = lo, mid + 1
    for k in range(lo, hi + 1):
        if i > mid:
            a[k] = aux1[j]
            b[k], j = aux2[j], j + 1
        elif j > hi:
            a[k] = aux1[i]
            b[k], i = aux2[i], i + 1
        elif aux1[i] <= aux1[j]:
            a[k] = aux1[i]
            b[k], i = aux2[i], i + 1
        else:
            a[k] = aux1[j]
            b[k], j = aux2[j], j + 1

    return a

# Halve a[lo ~ hi], sort each of the halves, and merge them, using the extra space aux[]
def divideNMerge(a, b, aux1, aux2, lo, hi):
    if (hi <= lo): return a
    mid = (lo + hi) // 2
    divideNMerge(a, b, aux1, aux2, lo, mid)
    divideNMerge(a, b, aux1, aux2, mid + 1, hi)
    merge(a, b, aux1, aux2, lo, mid, hi)
    return a

def mergeSort(a, b):
    # Create the auxiliary array once and re-use for all subsequent merges
    aux1 = [None] * len(a)
    aux2 = [None] * len(a)

    divideNMerge(a, b, aux1, aux2, 0, len(a) - 1)
    return a, b

def anglecheck(x1, y1, x2, y2):
    return math.atan2(y2 - y1, x2 - x1) * 180 / math.pi

def collinearpoints(point):
    cnt_max = []
    point_max = []
    angle_max = []
    def linereturn(start, x):
        print(start)
        angle = []
        output = []
        aux_point = point.copy()

        for i in range(0, len(point)):
            angle.append(anglecheck(start[0], start[1], point[i][0], point[i][1]))
        # p와 이루는 모든 각도 구함

        mergeSort(angle, aux_point)

        angle_logger = []
        point_logger = []
        cnt_logger = []
        # angle_logger[n] : 각도
        # cnt_logger[n] : 해당 각도의 선에 해당하는 점의 개수

        for i in range(x, len(angle)):
            flag2 = angle[i] in angle_logger
            if flag2 == False:# 해당 각도가 해당 시작점에서 탐색된 적이 없으면 logger에 데이터 생성
                angle_logger.append(angle[i])
                point_logger.append(aux_point[i])
                cnt_logger.append(1)
            else:  # 해당 각도가 이미 탐색된 적이 있으면 logger에 데이터 업데이트
                cnt_logger[angle_logger.index(angle[i])] = cnt_logger[angle_logger.index(angle[i])] + 1
                point_logger[angle_logger.index(angle[i])] = aux_point[i]

        # 시작점에서 모든점 다돌았고 이제 중앙 data에 업로드 해야함

        for i in range(0, len(cnt_logger)):
            if(cnt_logger[i] >= 3):
                insert = start + point_logger[i]
                output.append(insert)
                #print(output)

        return output

    collinearpoint = []
    """
    for i in range(0, len(point)):
        out = []
        out.extend(linereturn(point[i], i))
        if len(out) != 0:
            collinearpoint.extend(out)"""

    for i in range(0, len(point)):
        #print(linereturn(point[i], i))

        print(linereturn(point[9], 9))


    return collinearpoint

if __name__ == "__main__":
    print(__name__)
    input = [(0,0), (1,1), (3,3), (4,4), (6,6), (7,7), (2,0), (3,0), (4,0), (5,0), (5,1), (5,2), (5,3)]

    #print(collinearpoints(input))
    collinearpoints(input)