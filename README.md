# TSP Branch and Bound Solver

A Python-based GUI application that solves the Traveling Salesman Problem (TSP) using the Branch and Bound algorithm.

## Project Information

**Course:** BSC - CS & IT Department  
**Module:** Comprehension (351 CP 81)  
**Algorithm:** Branch and Bound  
**Language:** Python  
**Author:** Wisdom Mellow Mlambia  
**Date:** October 2025

## Description

This application implements the Branch and Bound algorithm to find the optimal solution for the Traveling Salesman Problem. The GUI allows users to:
- Add cities with coordinates
- Visualize cities on a canvas
- Solve TSP and view the optimal tour
- See the total tour distance

## Features

- ✅ Interactive GUI built with Tkinter
- ✅ Add/remove cities dynamically
- ✅ Visual representation of cities and tour
- ✅ Branch and Bound algorithm implementation
- ✅ Real-time distance calculation
- ✅ Start/Pause/Reset functionality

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone <your-repo-url>
cd tsp-branch-bound
```

2. Create virtual environment:
```bash
python -m venv venv
```

3. Activate virtual environment:
```bash
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python main.py
```

### How to Use:
1. **Add Cities:** Enter city name and coordinates (x, y) and click "Add City"
2. **Add Multiple Cities:** Add at least 4 cities to solve TSP
3. **Start Solving:** Click the "Start" button to find the optimal tour
4. **View Results:** See the tour visualization and total distance
5. **Reset:** Click "Reset" to clear and start over

## Project Structure

```
tsp-branch-bound/
│
├── src/
│   ├── __init__.py
│   ├── algorithm.py          # Branch & Bound implementation
│   ├── gui.py                # GUI components
│   └── utils.py              # Helper functions
│
├── data/
│   └── (test data files)
│
├── docs/
│   └── (documentation)
│
├── main.py                   # Entry point
├── requirements.txt          # Dependencies
├── README.md                 # This file
└── .gitignore
```

## Algorithm: Branch and Bound

Branch and Bound is an exact algorithm that guarantees finding the optimal solution for TSP. It works by:

1. **Branching:** Exploring different possible tours
2. **Bounding:** Calculating lower bounds to prune unpromising branches
3. **Pruning:** Eliminating branches that cannot lead to better solutions

### Why Branch and Bound?
- ✅ Finds **optimal solution** (not just approximate)
- ✅ More efficient than brute force (O(n!))
- ✅ Uses intelligent pruning to reduce search space
- ✅ Good for small to medium-sized problems (up to 20-25 cities)

## Development Timeline

- **Week 1 (Oct 21-27):** Project setup, basic GUI, data structures
- **Week 2 (Oct 28-Nov 3):** Algorithm implementation, basic visualization
- **Week 3 (Nov 4-10):** Complete features, testing, refinement

## Dependencies

- numpy: Numerical computations and matrix operations
- matplotlib: (Optional) Additional visualization
- tkinter: GUI framework (built-in with Python)

## Testing

To test the application with sample cities:
1. Run the application
2. Add cities manually or use the sample data
3. Click "Start" to solve

## Known Limitations

- Performance decreases significantly for cities > 15 (exponential complexity)
- GUI responsiveness may be affected during computation
- Currently supports Euclidean distance only

## Future Enhancements

- [ ] Animation of the solving process
- [ ] Step-by-step visualization
- [ ] Import/export city data from CSV
