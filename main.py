
# ------------------------------------------------------ imports ------------------------------------------------------ #

import pygame
import math
import rich

pygame.font.init()
font = pygame.font.SysFont("comicsans", 15)

# ------------------------------------------------------ constants ---------------------------------------------------- #

width = 500
height = 500
MAX_WEIGHT = 100

display = pygame.display.set_mode((width, height))
pygame.display.set_caption("Dijkstra's algorithm")

# ------------------------------------------------------ COLOR ------------------------------------------------------- #

class Color:
    bg = (46, 52, 64)
    light = (216, 222, 233)
    dark = (94, 129, 172)

# --------------------------------------------------- UTILS FUNCS ---------------------------------------------------- #

def mapn(value, act_lower, act_upper, to_lower, to_upper):
    return to_lower + (to_upper - to_lower) * ((value - act_lower) / (act_upper - act_lower))

def render_text(txt: str, win: pygame.display, x: int, y: int):
    render_text = font.render(str(txt), True, Color.light)
    win.blit(render_text, (x, y))

# ------------------------------------------------------ VERTEX ------------------------------------------------------ #

class Vertex:
    vertex_index = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.coords = (self.x, self.y)
        self.visited = False
        self.index = Vertex.vertex_index
        self.edges = []

        # increment the class variable "vertex_index"
        Vertex.vertex_index += 1

    def draw(self, win):
        pygame.draw.circle(win, Color.dark, (self.x, self.y), 5)
        render_text = font.render(str(self.index), True, Color.light)
        win.blit(render_text, (self.x, self.y))

# ------------------------------------------------------ EDGE ------------------------------------------------------ #

class Edge:
    def __init__(self, vert_A: Vertex, vert_B: Vertex, weight: int = None):
        self.vertA = vert_A
        self.vertB = vert_B
        self.weight = weight

    def includes(self, vert: Vertex):
        if self.vertA == vert or self.vertB == vert:
            return True
        return False

    def other(self, vert):
        if vert == self.vertA:
            return self.vertB
        elif vert == self.vertB:
            return self.vertA
        else:
            return None

    def draw(self, win):
        weighted_Color = (int(mapn(self.weight, 1, MAX_WEIGHT, 0, 255)), int(mapn(self.weight, 1, MAX_WEIGHT, 0, 255))) + (255, )
        pygame.draw.line(win, weighted_Color, (self.vertA.x, self.vertA.y), (self.vertB.x, self.vertB.y), 5)
        
        if self.weight != None:
            render_text(str(self.weight), win, (self.vertA.x + self.vertB.x) // 2, (self.vertA.y + self.vertB.y) // 2)

# ---------------------------------------------------- dijkstra ---------------------------------------------------- #

def dijkstra(vertices, edges, start_ind, lookup = [], past_distance = 0, path = []):
    if lookup == []:
        for vertex in vertices:
            if vertex.index == start_ind:
                value = 0
            else:
                value = math.inf

            lookup.append(value)

    if path == []:
        for vertex in vertices:
            path.append([])

    try:
        current_vertex: Vertex = [v for v in vertices if v.index == start_ind][0]
        current_vertex.visited = True
    except IndexError:
        rich.print(f"[bold red]ERROR[/bold red]: [bold blue]Unresolved logic error[/bold blue]")
        return

    current_vertex_neighbors: list[Vertex] = []
    for edge in edges:
        if edge.includes(current_vertex):
            if not edge.other(current_vertex).visited:
                current_vertex_neighbors.append((edge.other(current_vertex), edge.weight))

    # BASE CONDITION
    if len(current_vertex_neighbors) == 0:
        if all([ew != math.inf for ew in lookup]):
            print()
            for ind, packed in enumerate(zip(path, lookup)):
                route, distance = packed
                route.append(ind)
                rich.print(f"0 [i]to[/i] {ind} : {' ' * (3 - len(str(distance)))}{distance} : {' -> '.join([str(i) for i in route])}")

            return
        else:
            rich.print(f"[bold red]ERROR[/bold red]: [bold blue]Unresolved logic error[/bold blue]")

    # RECURSIVE CONDITION
    else:
        nearest_vertex_distance = math.inf
        nearest_vertex_index = None
        for vertex, edge_weight in current_vertex_neighbors:

            # updating the shortest distance to a vertex
            if lookup[vertex.index] > edge_weight + past_distance:
                lookup[vertex.index] = edge_weight + past_distance 
                path[vertex.index].append(current_vertex.index)

            # finding the nearest vertex for the next round
            if lookup[vertex.index] < nearest_vertex_distance:
                nearest_vertex_index = vertex.index
                nearest_vertex_distance = lookup[vertex.index]

        return dijkstra(vertices, edges, nearest_vertex_index, lookup, nearest_vertex_distance, path)

# ----------------------------------------------------- main func ---------------------------------------------------- #

def main():
    run = True
    verts: list[Vertex] = []
    edges: list[Edge] = []
    selected: list[Vertex] = []
    user_weight = ''
    prompted = False

    while run:
        display.fill(Color.bg)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:                                                       # left mouse button          
                    if not prompted:    
                        # vertx creation
                        x, y = pygame.mouse.get_pos()
                        new_vertex = Vertex(x, y)
                        verts.append(new_vertex)
                    else:
                        print("Enter a valid input")

                elif event.button == 3:                                                     # right mouse button
                    if len(verts) >= 2:
                        pos = pygame.mouse.get_pos()
                        short_dist = math.inf
                        nearest_vert = None
                        for vert in verts:
                            point_dist = math.dist(vert.coords, pos)
                            if point_dist < short_dist:
                                short_dist = point_dist
                                nearest_vert = vert

                        selected.append(nearest_vert)

                        if len(selected) >= 2:
                            new_edge = Edge(selected[0], selected[1], MAX_WEIGHT)           # edge creation
                            edges.append(new_edge)
                            selected = []
                            prompted = True                                                 # prompt the user for edge weight after edge creation

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    print([e.weight for e in edges])

                if event.key == pygame.K_RETURN:
                    try:
                        edges[-1].weight = int(user_weight)
                    except:
                        user_weight = ''
                        break

                    user_weight = ''
                    prompted = False
                else:
                    # If user is prompted, only then we add the keystrokes to the user_weight variable
                    if prompted:
                        user_weight += pygame.key.name(event.key)

                if event.key == pygame.K_d:
                    if len(verts) != 0:
                        start_ind = int(input("Enter the starting index: "))
                        dijkstra(verts, edges, start_ind)
                    else:
                        rich.print("[bold red]ERROR[/bold red] : [bold blue]No graph found[/bold blue]")


                if event.key == pygame.K_BACKSPACE:
                    user_weight = ''

                if event.key == pygame.K_DELETE:
                    if len(verts) > 0:
                        last_vert = verts[-1]
                        for edge in edges:
                            if edge.includes(last_vert):
                                edges.remove(edge)  
                        verts = verts[:-1]
                        Vertex.vertex_index -= 1
                    else:
                        rich.print("[bold red]ERROR[/bold red] : [bold blue]No vertices to delete[/bold blue]")

        if prompted:
            render_text("Weight: ", display, 0, 10)
            render_text(user_weight, display, 60, 10)

        for edge in edges:
            edge.draw(display)
                
        for vert in verts:
            vert.draw(display)

        for vert in selected:
            pygame.draw.circle(display, Color.light, vert.coords, 7, 1)

        pygame.display.flip()


# --------------------------------------------- calling the main func ------------------------------------------------- #

if __name__ == "__main__":
    main()

# --------------------------------------------------------------------------------------------------------------------- #

