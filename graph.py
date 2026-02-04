import random
from collections import deque
from map import GRID_WIDTH, GRID_HEIGHT

class Graph:
    """Adjacency-list Graph (our own non-linear DS)."""
    def __init__(self):
        self.adj = {}  # node -> list of neighbors

    def add_node(self, node):
        if node not in self.adj:
            self.adj[node] = []

    def add_edge(self, u, v):
        self.add_node(u)
        self.add_node(v)
        self.adj[u].append(v)

    def neighbors(self, node):
        return self.adj.get(node, [])

    def bfs_path(self, start, goal):
        """BFS traversal that returns one shortest path (list of tiles)."""
        q = deque([start])
        parent = {start: None}

        while q:
            cur = q.popleft()
            if cur == goal:
                break

            for nxt in self.neighbors(cur):
                if nxt not in parent:
                    parent[nxt] = cur
                    q.append(nxt)

        if goal not in parent:
            return None

        # reconstruct
        path = []
        cur = goal
        while cur is not None:
            path.append(cur)
            cur = parent[cur]
        path.reverse()
        return path


def build_grid_graph(blocked_tiles):
    """Build a grid graph excluding blocked tiles (tower tiles)."""
    g = Graph()
    dirs = [(1,0), (-1,0), (0,1), (0,-1)]

    for x in range(GRID_WIDTH):
        for y in range(1, GRID_HEIGHT-1):
            u = (x, y)
            if u in blocked_tiles:
                continue

            dirs_shuffled = dirs[:]       # make paths vary
            random.shuffle(dirs_shuffled)

            for dx, dy in dirs_shuffled:
                v = (x + dx, y + dy)
                if 0 <= v[0] < GRID_WIDTH and 1 <= v[1] < GRID_HEIGHT - 1 and v not in blocked_tiles:
                    g.add_edge(u, v)

    return g


def generate_path(blocked_tiles = None):
    if blocked_tiles is None:
        blocked_tiles = set()
    # Random start/end anywhere on first/last column
    start_y = random.randint(1, GRID_HEIGHT - 2)
    end_y   = random.randint(1, GRID_HEIGHT - 2)
    start = (0, start_y)
    end   = (GRID_WIDTH - 1, end_y)

    if start in blocked_tiles or end in blocked_tiles:
        return None

    g = build_grid_graph(blocked_tiles)

    # Choose 1 or 2 random waypoints to force a more winding path
    waypoint_count = random.choice([1, 2])

    waypoints = []
    tries = 0

    # Waypoints must move forward in x to avoid loopbacks/tails
    min_x = 1
    max_x = GRID_WIDTH - 4  # keep away from the end to prevent ugly tails

    while len(waypoints) < waypoint_count and tries < 60:
        tries += 1
        wx = random.randint(min_x, max_x)
        wy = random.randint(1, GRID_HEIGHT - 2)
        w = (wx, wy)

        if w in blocked_tiles:
            continue
        if any(wx == px for (px, py) in waypoints):
            continue

        waypoints.append(w)

    # Sort waypoints left-to-right so path overall always progresses forward
    waypoints.sort(key=lambda t: t[0])

    points = [start] + waypoints + [end]

    full = []
    for i in range(len(points) - 1):
        seg = g.bfs_path(points[i], points[i+1])
        if not seg:
            return None

        # join segments without duplicating connecting node
        if i > 0:
            seg = seg[1:]
        full.extend(seg)

    return full



def path_to_pixels(path, tile_size):
    if not path:
        return []
    pixel_path = []
    for i in range(len(path)-1):
        x1, y1 = path[i]
        x2, y2 = path[i+1]
        steps = max(abs(x2 - x1), abs(y2 - y1)) * tile_size
        if steps == 0:
            steps = 1
        for s in range(int(steps)):
            px = x1 * tile_size + tile_size // 2 + (x2 - x1) * tile_size * s / steps
            py = y1 * tile_size + tile_size // 2 + (y2 - y1) * tile_size * s / steps
            pixel_path.append((px, py))
    lx, ly = path[-1]
    pixel_path.append((lx * tile_size + tile_size // 2, ly * tile_size + tile_size // 2))
    return pixel_path
