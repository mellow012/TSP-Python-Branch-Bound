"""
Utility functions for TSP solver
Contains helper functions for distance calculations and data processing
"""

import math

def calculate_distance(x1, y1, x2, y2):
    """
    Calculate Euclidean distance between two points
    
    Args:
        x1, y1: Coordinates of first point
        x2, y2: Coordinates of second point
        
    Returns:
        Euclidean distance
    """
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def generate_sample_cities(n=5):
    """
    Generate sample cities for testing
    
    Args:
        n: Number of cities to generate
        
    Returns:
        List of tuples (name, x, y)
    """
    import random
    cities = []
    for i in range(n):
        name = f"City{i+1}"
        x = random.uniform(0, 100)
        y = random.uniform(0, 100)
        cities.append((name, x, y))
    return cities


def validate_coordinates(x, y):
    """
    Validate if coordinates are valid numbers
    
    Args:
        x, y: Coordinates to validate
        
    Returns:
        Boolean indicating if coordinates are valid
    """
    try:
        float(x)
        float(y)
        return True
    except (ValueError, TypeError):
        return False


def format_distance(distance):
    """
    Format distance for display
    
    Args:
        distance: Distance value
        
    Returns:
        Formatted string
    """
    return f"{distance:.2f} units"


def get_path_string(path, cities):
    """
    Convert path indices to city names string
    
    Args:
        path: List of city indices
        cities: List of city tuples
        
    Returns:
        String representation of path
    """
    city_names = [cities[i][0] for i in path]
    return " → ".join(city_names)