import math

def push(stack, data):
    stack.append(data)
    return data

def pop(stack):
    return stack.pop()

def grahamScan(point):
    cursor = 0
    def monitoring():
        print("-----monitoring-----")
        print(count)
        print(convex_hull)
        print(len(point))
        print(point)
        print(sorted(angle))

        return

    def ccw(p1, p2, p3):
        return (p1[0]*p2[1] + p2[0]*p3[1] + p3[0]*p1[1]) - (p2[0]*p1[1] + p3[0]*p2[1] + p1[0]*p3[1])

    def scan(count): # 현재 point가 hull에 포함될수 있는 점인지
        count1 = count + 1
        for i in range(count1, len(point) + 1):
            push(convex_hull, point[angle.index(sorted(angle)[count1])])
            if (i == len(point)): # 마지막까지 전부 오목인 경우
                pop(convex_hull)
                return False # 이 point는 convex_hull에 포함 될 수 없음

            if(ccw(convex_hull[-1], convex_hull[-2], convex_hull[-3]) >= 0): #그 다음 라인에서 볼록인게 있음
                if (scan(count1) == True):
                    return True
                else:
                    pop(convex_hull)

    angle = []
    convex_hull = []
    p = point[0]
    for i in range(0, len(point)):
        if (point[i][1] < p[1]):
            p = point[i]
        elif (point[i][1] == p[1]):
            if (point[i][0] > p[0]):
                p = point[i]
    # p 구함
    push(convex_hull, p)

    for i in range(0, len(point)):
        angle.append(math.atan2(point[i][1]-p[1], point[i][0]-p[0]) * 180 / math.pi)
    # p와 이루는 모든 각도 구함

    for i in range(0, len(point)):
        if(sorted(angle)[i] != 0):
            next_point = point[angle.index(sorted(angle)[i])]
            count = i # 현재 포인트위치 저장
            push(convex_hull, next_point)
            break;
    #두번째 point까지 구함 (p를 제외하면 첫번쨰)
    monitoring()

    while True:
        if(ccw(point[angle.index(sorted(angle)[len(point)-1])], convex_hull[-1], convex_hull[-2]) >= 0):
            push(convex_hull, point[angle.index(sorted(angle)[len(point)-1])])
            break
        # 마지막 point와 -1, -2번째가 볼록하다면 종료

        # scan: 현재 포인트 point(count)를 push해도 되는지?
        # check해볼 point(count + n)과 볼록하다면 push가능
        if(scan(count) == False):
            pop(convex_hull) # 넣으면 안되는 point

        break

    print(point[angle.index(sorted(angle)[len(point)-1])])
    return convex_hull

if __name__ == "__main__":
    print(__name__)
    input = [(4,2),(3,-1),(2,-2),(1,0),(0,2),(0,-2),(-1,1),(-2,-1),(-2,-3),(- 3,3),(-6,0),(-4,-2),(-4,-4)]

    grahamScan(input)
