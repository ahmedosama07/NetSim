import networkx as nx
import heapq
import math

class NetworkModel:
    """Data model class representing the network graph and associated properties.
    
    Manages the network topology using NetworkX graph structure, node positions,
    and edge information. Implements file I/O operations and path calculation logic.
    
    Attributes:
        G (nx.Graph): Undirected graph representing network topology
        node_positions (dict): Mapping of node names to (x, y) coordinates
        _edges (list): Internal storage of edge tuples for persistence
    """

    def __init__(self):
        """Initialize empty network model with clean data structures."""
        self.G = nx.Graph()
        self.node_positions = {}
        self._edges = []

    def add_node(self, name, pos):
        """Add a node to the network model.
        
        Args:
            name (str): Unique identifier for the node
            pos (tuple): (x, y) coordinates for node visualization
        """
        self.G.add_node(name)
        self.node_positions[name] = pos

    def add_edge(self, src, dest, weight):
        """Add an edge between two nodes with specified weight.
        
        Args:
            src (str): Source node identifier
            dest (str): Destination node identifier
            weight (int): Edge weight/cost for path calculations
        """
        self.G.add_edge(src, dest, weight=weight)
        self._edges.append((src, dest, weight))

    def clear(self):
        """Reset model to initial empty state."""
        self.G.clear()
        self.node_positions.clear()
        self._edges.clear()

    def get_forwarding_table(self, node):
        """Calculate shortest path forwarding table using custom Dijkstra's implementation.
        
        Args:
            node (str): Source node for forwarding table calculation
            
        Returns:
            dict: Mapping of destination nodes to next-hop nodes.
                Empty if node doesn't exist or no paths found.
        """
        # Validate source node exists in graph
        if node not in self.G.nodes:
            return {}

        # Initialize data structures
        distances = {n: float('inf') for n in self.G.nodes}     # Shortest distance from source
        previous = {n: None for n in self.G.nodes}              # Previous node in shortest path
        next_hop = {n: None for n in self.G.nodes}              # First hop in shortest path
        distances[node] = 0                                     # Distance to self is zero

        # Priority queue using heap structure (distance, node)
        heap = []
        heapq.heappush(heap, (0, node))

        visited = set()

        # Main Dijkstra's algorithm loop
        while heap:
            current_dist, current = heapq.heappop(heap)

            if current in visited:
                continue
            visited.add(current)

            # Explore all neighbors of current node
            for neighbor in self.G.neighbors(current):
                if neighbor in visited:
                    continue

                # Calculate tentative distance through current node
                edge_weight = self.G[current][neighbor]['weight']
                tentative_dist = current_dist + edge_weight

                # Update if found shorter path
                if tentative_dist < distances[neighbor]:
                    distances[neighbor] = tentative_dist
                    previous[neighbor] = current

                    # Determine next hop using path inheritance:
                    # - Direct neighbors get neighbor as next hop
                    # - Indirect paths inherit next hop from predecessor
                    next_hop[neighbor] = neighbor if current == node else next_hop[current]

                    # Update priority queue
                    heapq.heappush(heap, (tentative_dist, neighbor))

        # Build forwarding table excluding source and unreachable nodes
        return {
            dest: hop 
            for dest, hop in next_hop.items() 
            if dest != node and hop is not None
        }

    def load_from_file(self, file_path):
        """Load network topology from formatted text file.
        
        Args:
            file_path (str): Path to input file
            
        File Format:
            First line: <number_of_nodes>,<number_of_edges>
            Subsequent lines: <src_node>,<dest_node>,<weight>
            
        Raises:
            ValueError: If file format is invalid or data is inconsistent
        """
        # Clear existing network data
        self.clear()

        # Read and process file
        with open(file_path, 'r') as f:
            lines = f.read().strip().split('\n')

            # Parse header line (nodes_count, edges_count)
            # Note: nodes_count is read but not used - determined implicitly from edges
            _, m = map(int, lines[0].split(','))
            # Extract edge definitions (first m lines after header)
            edges = [tuple(line.strip().split(',')) for line in lines[1:m+1]]
            
            for u, v, w in edges:
                self.add_edge(u.strip(), v.strip(), int(w.strip()))
            
            if self.G.nodes:
                self.node_positions.update(nx.spring_layout(self.G))

    def save_to_file(self, file_path):
        """Save current network topology to formatted text file.
        
        Args:
            file_path (str): Destination path for output file
            
        File Format:
            First line: <number_of_nodes>,<number_of_edges>
            Subsequent lines: <src_node>,<dest_node>,<weight>
        
        Raises:
            IOError: If there is an issue writing to the file
        """
        try:
            with open(file_path, 'w') as f:
                # Write the number of nodes and edges
                f.write(f"{len(self.G.nodes)},{len(self._edges)}\n")
                
                # Write each edge in the format <src_node>,<dest_node>,<weight>
                for u, v, w in self._edges:
                    f.write(f"{u},{v},{w}\n")
        except IOError as e:
            raise IOError(f"Failed to save file: {e}")


    def delete_node(self, node):
        """Remove node and all connected edges."""
        if node in self.G:
            # Remove from graph
            self.G.remove_node(node)
            
            # Remove from positions
            del self.node_positions[node]
            
            # Remove related edges
            self._edges = [
                (u, v, w) for u, v, w in self._edges 
                if u != node and v != node
            ]

    def delete_edge(self, edge):
        """Remove specific edge from the network."""
        u, v = edge
        if self.G.has_edge(u, v):
            self.G.remove_edge(u, v)
            self._edges = [
                (src, dest, w) for src, dest, w in self._edges
                if not ((src == u and dest == v) or (src == v and dest == u))
            ]

    def find_nearest_edge(self, x, y, threshold=1.0):
        """Find edge closest to coordinates using line segment distance."""
        min_distance = float('inf')
        nearest_edge = None
        
        for u, v in self.G.edges():
            ux, uy = self.node_positions[u]
            vx, vy = self.node_positions[v]
            distance = self._distance_to_segment((x, y), (ux, uy), (vx, vy))
            
            if distance < min_distance and distance < threshold:
                min_distance = distance
                nearest_edge = (u, v)
                
        return nearest_edge

    def _distance_to_segment(self, p, a, b):
        """Calculate distance from point to line segment."""
        # Vector math implementation
        ax, ay = a
        bx, by = b
        px, py = p
        
        if ax == bx and ay == by:
            return math.hypot(px - ax, py - ay)
        
        seg_length_sq = (bx - ax)**2 + (by - ay)**2
        t = ((px - ax)*(bx - ax) + (py - ay)*(by - ay)) / seg_length_sq
        t = max(0, min(1, t))
        proj_x = ax + t*(bx - ax)
        proj_y = ay + t*(by - ay)
        
        return math.hypot(px - proj_x, py - proj_y)