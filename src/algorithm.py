"""
Branch and Bound Algorithm for TSP
Implements the core solving logic using Branch and Bound approach
Now with statistics tracking for analysis
"""

import numpy as np
from queue import PriorityQueue
import sys
import time
from src.utilities import calculate_distance

class Node:
    """Represents a node in the Branch and Bound search tree"""
    
    def __init__(self, level, path, reduced_matrix, cost, visited):
        self.level = level  # Current level in the tree
        self.path = path  # Path taken so far
        self.reduced_matrix = reduced_matrix  # Reduced cost matrix
        self.cost = cost  # Lower bound cost
        self.visited = visited  # Set of visited cities
    
    def __lt__(self, other):
        """Compare nodes based on cost for priority queue"""
        return self.cost < other.cost


class BranchAndBoundTSP:
    """Branch and Bound solver for Traveling Salesman Problem with statistics"""
    
    def __init__(self, cities):
        """
        Initialize TSP solver with cities
        
        Args:
            cities: List of tuples (name, x, y)
        """
        self.cities = cities
        self.n = len(cities)
        self.distance_matrix = self.create_distance_matrix()
        self.best_cost = float('inf')
        self.best_path = []
        
        # Statistics tracking
        self.nodes_explored = 0
        self.branches_pruned = 0
        self.max_depth_reached = 0
        self.start_time = 0
        self.end_time = 0
        self.computation_time = 0
        
        # For progress tracking
        self.callback = None
    
    def set_progress_callback(self, callback):
        """Set callback function for progress updates"""
        self.callback = callback
    
    def create_distance_matrix(self):
        """Create distance matrix from city coordinates"""
        n = len(self.cities)
        matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    matrix[i][j] = calculate_distance(
                        self.cities[i][1], self.cities[i][2],
                        self.cities[j][1], self.cities[j][2]
                    )
                else:
                    matrix[i][j] = float('inf')
        
        return matrix
    
    def reduce_matrix(self, matrix):
        """
        Reduce the cost matrix by subtracting minimum values
        
        Args:
            matrix: Cost matrix to reduce
            
        Returns:
            Tuple of (reduced_matrix, reduction_cost)
        """
        reduced = matrix.copy()
        cost = 0
        
        # Row reduction
        for i in range(len(reduced)):
            row_min = np.min(reduced[i])
            if row_min != float('inf') and row_min > 0:
                reduced[i] -= row_min
                cost += row_min
        
        # Column reduction
        for j in range(len(reduced[0])):
            col_min = np.min(reduced[:, j])
            if col_min != float('inf') and col_min > 0:
                reduced[:, j] -= col_min
                cost += col_min
        
        return reduced, cost
    
    def calculate_lower_bound(self, matrix, current_cost, src, dest):
        """
        Calculate lower bound for a given edge
        
        Args:
            matrix: Current cost matrix
            current_cost: Cost accumulated so far
            src: Source city
            dest: Destination city
            
        Returns:
            Lower bound cost
        """
        # Create a copy of the matrix
        temp_matrix = matrix.copy()
        
        # Set row and column to infinity
        temp_matrix[src, :] = float('inf')
        temp_matrix[:, dest] = float('inf')
        temp_matrix[dest, 0] = float('inf')  # Prevent returning to start prematurely
        
        # Reduce the matrix and get reduction cost
        reduced, reduction_cost = self.reduce_matrix(temp_matrix)
        
        # Total cost = current + edge + reduction
        return current_cost + matrix[src][dest] + reduction_cost
    
    def update_statistics(self):
        """Update statistics and call progress callback if set"""
        if self.callback:
            stats = {
                'nodes_explored': self.nodes_explored,
                'branches_pruned': self.branches_pruned,
                'best_cost': self.best_cost if self.best_cost != float('inf') else None,
                'max_depth': self.max_depth_reached
            }
            self.callback(stats)
    
    def solve(self):
        """
        Solve TSP using Branch and Bound algorithm
        
        Returns:
            Tuple of (best_path, best_cost)
        """
        # Reset statistics
        self.nodes_explored = 0
        self.branches_pruned = 0
        self.max_depth_reached = 0
        self.best_cost = float('inf')
        self.best_path = []
        
        # Start timing
        self.start_time = time.time()
        
        # Initialize with reduced matrix
        reduced_matrix, initial_cost = self.reduce_matrix(self.distance_matrix)
        
        # Priority queue for nodes
        pq = PriorityQueue()
        
        # Create root node
        visited = {0}
        root = Node(
            level=0,
            path=[0],
            reduced_matrix=reduced_matrix,
            cost=initial_cost,
            visited=visited
        )
        
        pq.put((root.cost, id(root), root))
        
        # Branch and Bound search
        while not pq.empty():
            _, _, current = pq.get()
            
            # Update statistics
            self.nodes_explored += 1
            if current.level > self.max_depth_reached:
                self.max_depth_reached = current.level
            
            # Periodic progress update (every 100 nodes)
            if self.nodes_explored % 100 == 0:
                self.update_statistics()
            
            # If current node's cost is already worse than best, prune it
            if current.cost >= self.best_cost:
                self.branches_pruned += 1
                continue
            
            # If we've visited all cities
            if current.level == self.n - 1:
                # Complete the tour by returning to start
                last_city = current.path[-1]
                total_cost = current.cost + self.distance_matrix[last_city][0]
                
                if total_cost < self.best_cost:
                    self.best_cost = total_cost
                    self.best_path = current.path + [0]
                    self.update_statistics()
                
                continue
            
            # Explore all unvisited cities
            current_city = current.path[-1]
            
            for next_city in range(self.n):
                if next_city not in current.visited:
                    # Calculate lower bound for this branch
                    new_cost = self.calculate_lower_bound(
                        current.reduced_matrix,
                        current.cost,
                        current_city,
                        next_city
                    )
                    
                    # Pruning: only explore if promising
                    if new_cost < self.best_cost:
                        new_visited = current.visited.copy()
                        new_visited.add(next_city)
                        
                        new_matrix = current.reduced_matrix.copy()
                        new_matrix[current_city, :] = float('inf')
                        new_matrix[:, next_city] = float('inf')
                        
                        new_node = Node(
                            level=current.level + 1,
                            path=current.path + [next_city],
                            reduced_matrix=new_matrix,
                            cost=new_cost,
                            visited=new_visited
                        )
                        
                        pq.put((new_node.cost, id(new_node), new_node))
                    else:
                        # This branch was pruned
                        self.branches_pruned += 1
        
        # End timing
        self.end_time = time.time()
        self.computation_time = self.end_time - self.start_time
        
        # Final statistics update
        self.update_statistics()
        
        # Return path without the final return to start for visualization
        return self.best_path[:-1], self.best_cost
    
    def get_statistics(self):
        """
        Get solving statistics
        
        Returns:
            Dictionary with statistics
        """
        return {
            'nodes_explored': self.nodes_explored,
            'branches_pruned': self.branches_pruned,
            'max_depth_reached': self.max_depth_reached,
            'computation_time': self.computation_time,
            'best_cost': self.best_cost,
            'pruning_efficiency': (self.branches_pruned / max(self.nodes_explored, 1)) * 100
        }
    
    def get_tour_distance(self, path):
        """
        Calculate total distance for a given path
        
        Args:
            path: List of city indices
            
        Returns:
            Total distance
        """
        total = 0
        for i in range(len(path)):
            total += self.distance_matrix[path[i]][path[(i + 1) % len(path)]]
        return total