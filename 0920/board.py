def grahamScan(point):
    def ccw(p1, p2, p3):
        return (p1[0]*p2[1] + p2[0]*p3[1] + p3[0]*p1[1]) - (p2[0]*p1[1] + p3[0]*p2[1] + p1[0]*p3[1])

    flag = []
    angle = []
    convex_hull = []
    p = point[0]
    for i in range(0, len(point)):
        if(point[i][1] < p[1]):
            p = point[i]
        elif(point[i][1] == p[1]):
            if(point[i][0] > p[0]):
                p = point[i]
    #p 구함
    print(p)
    print(p[0])
    print(p[1])

if __name__ == "__main__":
    print(__name__)
    input = [(0,0),(-2,-1),(-1,1),(1,-1),(3,-1),(-3,-1)]

    grahamScan(input)