from pathlib import Path
from queue import Queue
import timeit

class FlowEdge:
    def __init__(self, v, w, capacity): # Create an edge v->w with a double capacity
        assert isinstance(v, int) and isinstance(w, int), f"v({v}) and/or w({w}) are not integers"
        assert v>=0 and w>=0, f"Vertices {v} and/or {w} have negative IDs"
        assert isinstance(capacity, int) or isinstance(capacity, float), f"Capacity {capacity} is neither an integer nor a floating-point number"
        assert capacity>=0, f"Edge capacity {capacity} must be >= 0"
        self.v, self.w, self.capacity = v, w, capacity
        self.flow = 0.0 # Initialize flow to 0
    
    def __lt__(self, other): # < operator, used to sort elements (e.g., in a PriorityQueue, sorted() function)
        self.validateInstance(other)
        return self.capacity < other.capacity

    def __gt__(self, other): # > operator, used to sort elements
        self.validateInstance(other)
        return self.capacity > other.capacity

    def __eq__(self, other): # == operator, used to compare edges for grading
        if other == None: return False
        self.validateInstance(other)
        return self.v == other.v and self.w == other.w and self.capacity == other.capacity

    def __str__(self): # Called when an Edge instance is printed (e.g., print(e))
        return f"{self.v}->{self.w} ({self.flow}/{self.capacity})"

    def __repr__(self): # Called when an Edge instance is printed as an element of a list
        return self.__str__()

    def other(self, vertex): # Return the vertex on the Edge other than vertex        
        if vertex == self.v: return self.w
        elif vertex == self.w: return self.v
        else: self.invalidIndex(vertex)

    def remainingCapacityTo(self, vertex): # Remaining capacity toward vertex
        if vertex == self.v: return self.flow
        elif vertex == self.w: return self.capacity - self.flow
        else: self.invalidIndex(vertex)
    
    def addRemainingFlowTo(self, vertex, delta): # Add delta flow toward vertex     
        assert isinstance(delta, int) or isinstance(delta, float), f"Delta {delta} is neither an integer nor a floating-point number"
        assert delta <= self.remainingCapacityTo(vertex), f"Delta {delta} is greater than the remaining capacity {self.remainingCapacity(v)}"        
        if vertex == self.v: self.flow -= delta
        elif vertex == self.w: self.flow += delta
        else: self.invalidIndex(vertex)

    def invalidIndex(self, i):
        assert False, f"Illegal endpoint {i}, which is neither of the two end points {self.v} and {self.w}"

    @staticmethod
    def validateInstance(e):
        assert isinstance(e, FlowEdge), f"e={e} is not an instance of FlowEdge"


'''
Class that represents Digraphs with Flow/Capacity
'''
class FlowNetwork:
    def __init__(self, V): # Constructor
        assert isinstance(V, int) and V >= 0, f"V({V}) is not an integer >= 0"
        self.V = V # Number of vertices
        self.E = 0 # Number of edges
        self.adj = [[] for _ in range(V)]   # adj[v] is a list of vertices adjacent to v
        self.edges = []

    def addEdge(self, e): # Add edge v-w. Self-loops and parallel edges are allowed
        FlowEdge.validateInstance(e)
        assert 0<=e.v and e.v<self.V and 0<=e.w and e.w<self.V, f"Edge endpoints ({e.v},{e.w}) are out of the range 0 to {self.V-1}"
        self.adj[e.v].append(e) # Add forward edge
        self.adj[e.w].append(e) # Add backward edge
        self.edges.append(e)
        self.E += 1

    def __str__(self):
        rtList = [f"{self.V} vertices and {self.E} edges\n"]
        for v in range(self.V):
            for e in self.adj[v]: 
                if e.v == v: rtList.append(f"{e}\n") # Show only forward edges to not show the same edge twice
        return "".join(rtList)

    def copy(self):
        fn = FlowNetwork(self.V)
        for e in self.edges: fn.addEdge(FlowEdge(e.v, e.w, e.capacity))
        return fn

    '''
    Create an FlowNetwork from a file
        fileName: Name of the file that contains graph information as follows:
            (1) the number of vertices, followed by
            (2) one edge in each line, where an edge v->w with capacity is represented by "v w capacity"
            e.g., the following file represents a digraph with 3 vertices and 2 edges
            3
            0 1 0.12
            2 0 0.26
        The file needs to be in the same directory as the current .py file
    '''
    @staticmethod
    def fromFile(fileName):
        filePath = Path(__file__).with_name(fileName)   # Use the location of the current .py file   
        with filePath.open('r') as f:
            phase = 0
            line = f.readline().strip() # Read a line, while removing preceding and trailing whitespaces
            while line:                                
                if len(line) > 0:
                    if phase == 0: # Read V, the number of vertices
                        g = FlowNetwork(int(line))
                        phase = 1
                    elif phase == 1: # Read edges
                        edge = line.split()
                        assert len(edge) == 3, f"Invalid edge format found in {line}"
                        if edge[2] == 'inf': g.addEdge(FlowEdge(int(edge[0]), int(edge[1]), float('inf')))                        
                        else: g.addEdge(FlowEdge(int(edge[0]), int(edge[1]), float(edge[2])))                        
                line = f.readline().strip()
        return g

    @staticmethod
    def validateInstance(g):
        assert isinstance(g, FlowNetwork), f"g={g} is not an instance of FlowNetwork"


def findAugmentingPathBFS(g, s):
    FlowNetwork.validateInstance(g)
    edgeTo = [None for _ in range(g.V)]
    visited = [False for _ in range(g.V)]
        
    q = Queue()
    q.put(s)
    visited[s] = True
    while not q.empty():
        v = q.get()
        for e in g.adj[v]:
            w = e.other(v)
            if e.remainingCapacityTo(w) > 0 and not visited[w]:
                edgeTo[w] = e
                visited[w] = True
                q.put(w)

    return edgeTo, visited


'''
Class that performs FordFulkerson algorithm to identify maxflow and mincut
    and that stores the results
'''
class FordFulkerson:
    def __init__(self, g, s, t):        
        FlowNetwork.validateInstance(g)
        assert s>=0 and s<g.V, f"s({s}) is not within 0 ~ {g.V-1}"
        assert t>=0 and t<g.V, f"t({t}) is not within 0 ~ {g.V-1}"
        assert s != t, f"s({s}) and t({t}) must be different"

        self.g = g.copy() # Make a copy to not mutate original graph
        self.s, self.t = s, t

        self.flow = 0.0
        while self.hasAugmentingPath():
            # Compute bottleneck capacity along the augmenting path
            minflow = float('inf')
            v = t
            while v != s: 
                minflow = min(minflow, self.edgeTo[v].remainingCapacityTo(v))
                v = self.edgeTo[v].other(v)
            
            # Add bottlenack capacity to the augmenting path
            v = t
            while v != s:
                self.edgeTo[v].addRemainingFlowTo(v, minflow)
                v = self.edgeTo[v].other(v)
        
            # Increase the amoung of flow
            self.flow += minflow

    # Perform BFS to find vertices reachable from s along with shortest paths to them
    def hasAugmentingPath(self):
        self.edgeTo = [None for _ in range(self.g.V)]
        self.visited = [False for _ in range(self.g.V)]
        
        q = Queue()
        q.put(self.s)
        self.visited[self.s] = True
        while not q.empty():
            v = q.get()
            for e in self.g.adj[v]:
                w = e.other(v)
                if e.remainingCapacityTo(w) > 0 and not self.visited[w]:
                    self.edgeTo[w] = e
                    self.visited[w] = True
                    q.put(w)

        return self.visited[self.t] # Is t reachable from s with current flow assignment?

    def inCut(self, vertex): # Is vertex reachable from s with current flow assignment?
        assert vertex>=0 and vertex<self.g.V, f"vertex({vertex}) is not within 0 ~ {self.g.V-1}"
        return self.visited[vertex]


class BaseballElimination:
    # Read from fileName the scores for each team and store them in member variables
    def __init__(self, fileName):
        filePath = Path(__file__).with_name(fileName)   # Use the location of the current .py file   
        with filePath.open('r') as f:
            self.teams = [] # teams[i]: name for team i
            self.team2id = {} # symbol table for team name -> index            
            self.wins = [] # Number of wins/losses/remaining games for team i
            self.losses = []
            self.remaining = [] 
            self.against = [] # against[i][j]: Number of remaining game between teams i and j            

            teamId = -1
            line = f.readline().strip() # Read a line, while removing preceding and trailing whitespaces
            while line:                                
                if len(line) > 0:
                    if teamId == -1: # Read the number of teams
                        tokens = line.split()
                        assert len(tokens) == 1, f"First non-empty line must contain a single token, but it does not ({line})"
                        assert tokens[0].isnumeric(), f"First non-empty line must contain an integer, but it does not ({tokens[0]})"
                        self.numberOfTeams = int(tokens[0])
                        teamId = 0                        
                    elif teamId >= 0: # Read team name and scores
                        tokens = line.split()
                        assert len(tokens) == 4 + self.numberOfTeams, f"Invalid team format found in {line}"
                        self.teams.append(tokens[0])
                        self.team2id[tokens[0]] = teamId
                        self.wins.append(int(tokens[1]))
                        self.losses.append(int(tokens[2]))
                        self.remaining.append(int(tokens[3]))
                        self.against.append([])
                        for i in range(4, 4 + self.numberOfTeams): self.against[teamId].append(int(tokens[i]))                        
                        teamId += 1
                line = f.readline().strip()

    def __str__(self):
        rtList = [f"{self.numberOfTeams} teams\n"]        
        for teamId in range(self.numberOfTeams):            
            rtList.append(f"{self.teams[teamId]}({self.team2id[self.teams[teamId]]}) {self.wins[teamId]} {self.losses[teamId]} {self.remaining[teamId]}")
            for i in range(self.numberOfTeams):
                rtList.append(f" {self.against[teamId][i]}")
            rtList.append("\n")        
        return "".join(rtList)

    def printResult(self):
        for team in self.teams:
            result = self.isEliminated(team)
            assert result != None and len(result)==2, f"isEliminated() must return a 2-tuple"
            eliminate, teamsResponsible = result
            if eliminate: print(f"{team} is eliminated by the subset {teamsResponsible}")
            else: print(f"{team} is not eliminated")
        print()

    # Find out whether teamName must be eliminated
    # Return (True, a list of team names responsible for the elimination), if teamName must be eliminated
    # Return (False, []), if teamName is NOT eliminated yet
    def isEliminated(self, teamName):
        def sum(number):
            if number <= 1:
                return number
            else:
                return number + sum(number-1)
        result = []

        for i in self.teams:
            if i != teamName:
                if self.wins[self.team2id[teamName]] + self.remaining[self.team2id[teamName]] < self.wins[self.team2id[i]]:
                    result.append(i)

        if len(result) > 0:
            return True, result

        gw = FlowNetwork(sum(self.numberOfTeams-1) + self.numberOfTeams + 2)
        #print(sum(self.numberOfTeams-1) + self.numberOfTeams + 2)

        # set game vertex
        firstTeamVertex = 1
        for i in range(0, self.numberOfTeams):
            for j in range(i+1, self.numberOfTeams):
                if i != j and self.teams[i] != teamName and self.teams[j] != teamName:
                    gw.addEdge(FlowEdge(0, firstTeamVertex, self.against[i][j]))
                    #print(firstTeamVertex, self.teams[i], self.teams[j])
                firstTeamVertex += 1

        # set team vertex
        for i in range(0, self.numberOfTeams):
            if self.teams[i] != teamName:
                gw.addEdge(FlowEdge(firstTeamVertex + i, sum(self.numberOfTeams-2) + self.numberOfTeams + 1,
                                self.wins[self.team2id[teamName]] + self.remaining[self.team2id[teamName]] - self.wins[i]))

        ff = FordFulkerson(gw, 0, gw.V - 1)
        #print(firstTeamVertex)

        for v in range(gw.V):
            if ff.inCut(v) and v != 0 and v != sum(self.numberOfTeams-2) + self.numberOfTeams + 1:
                print(v, firstTeamVertex)
                if v >= firstTeamVertex:
                    result.append(self.teams[v-firstTeamVertex])


        if len(result) > 0:
            return True, result
        else:
            return False, []


if __name__ == "__main__":

    # Unit test for BaseballElimination
    be4 = BaseballElimination("teams4.txt")
    print(be4)
    be4.printResult()    
    if be4.isEliminated("Giants") == (False, []): print("P ",end='')
    else: print("F ",end='')    
    if be4.isEliminated("Lions") == (True, ['Giants', 'Dinos']): print("P ",end='')
    else: print("F ",end='')    
    if be4.isEliminated("Dinos") == (False, []): print("P ",end='')
    else: print("F ",end='')    
    if be4.isEliminated("Eagles") == (True, ['Giants']): print("P ",end='')
    else: print("F ",end='')
    print()
    print()
    '''
    be5 = BaseballElimination("teams5.txt")
    print(be5)
    be5.printResult()    
    if be5.isEliminated("Dinos") == (False, []): print("P ",end='')
    else: print("F ",end='')    
    if be5.isEliminated("Landers") == (False, []): print("P ",end='')
    else: print("F ",end='')    
    if be5.isEliminated("Bears") == (False, []): print("P ",end='')
    else: print("F ",end='')    
    if be5.isEliminated("Twins") == (False, []): print("P ",end='')
    else: print("F ",end='')    
    if be5.isEliminated("Heros") == (True, ['Dinos', 'Landers', 'Bears', 'Twins']): print("P ",end='')
    else: print("F ",end='')
    print()
    print()

    be12 = BaseballElimination("teams12.txt")
    print(be12)
    be12.printResult()
    if be12.isEliminated("Poland") == (False, []): print("P ",end='')
    else: print("F ",end='')
    if be12.isEliminated("USA") == (False, []): print("P ",end='')
    else: print("F ",end='')
    if be12.isEliminated("Brazil") == (False, []): print("P ",end='')
    else: print("F ",end='')
    if be12.isEliminated("Iran") == (False, []): print("P ",end='')
    else: print("F ",end='')
    if be12.isEliminated("Italy") == (False, []): print("P ",end='')
    else: print("F ",end='')
    if be12.isEliminated("Cuba") == (False, []): print("P ",end='')
    else: print("F ",end='')
    if be12.isEliminated("Argentina") == (False, []): print("P ",end='')
    else: print("F ",end='')
    if be12.isEliminated("Korea") == (False, []): print("P ",end='')
    else: print("F ",end='')    
    if be12.isEliminated("Japan") == (True, ['Poland', 'USA', 'Brazil', 'Iran']): print("P ",end='')
    else: print("F ",end='')    
    if be12.isEliminated("Serbia") == (True, ['Poland', 'USA', 'Brazil', 'Iran']): print("P ",end='')
    else: print("F ",end='')    
    if be12.isEliminated("Egypt") == (True, ['Poland']): print("P ",end='')
    else: print("F ",end='')    
    if be12.isEliminated("Chile") == (True, ['Poland', 'USA', 'Brazil', 'Iran']): print("P ",end='')
    else: print("F ",end='')
    print()
    print()
    '''