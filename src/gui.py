"""
GUI Module for TSP Branch and Bound Solver
Handles all user interface components and visualization
"""
import tkinter as tk
from tkinter import ttk, messagebox
import math
from src.algorithm import BranchAndBoundTSP
from src.utilities import calculate_distance

class TSPApplication:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TSP Branch and Bound Solver")
        self.root.geometry("1200x700")
        self.root.resizable(True, True)
        
        # Data storage
        self.cities = []  # List of (name, x, y) tuples
        self.is_running = False
        self.is_paused = False
        self.solution = None
        self.total_distance = 0
        
        # Algorithm instance
        self.tsp_solver = None
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        """Create and layout all UI components"""
        # Main container with two panels
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Controls and Input
        left_panel = tk.Frame(main_frame, width=350, relief=tk.RIDGE, borderwidth=2)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 5))
        left_panel.pack_propagate(False)
        
        # Right panel - Visualization
        right_panel = tk.Frame(main_frame, relief=tk.RIDGE, borderwidth=2)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Setup left panel components
        self.setup_control_panel(left_panel)
        
        # Setup right panel components
        self.setup_canvas(right_panel)
        
    def setup_control_panel(self, parent):
        """Setup the control panel with inputs and buttons"""
        # Title
        title_label = tk.Label(parent, text="TSP Branch & Bound", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # City Input Section
        input_frame = tk.LabelFrame(parent, text="Add City", padx=10, pady=10)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(input_frame, text="City Name:").grid(row=0, column=0, sticky=tk.W)
        self.city_name_entry = tk.Entry(input_frame, width=20)
        self.city_name_entry.grid(row=0, column=1, pady=2)
        
        tk.Label(input_frame, text="X Coordinate:").grid(row=1, column=0, sticky=tk.W)
        self.x_coord_entry = tk.Entry(input_frame, width=20)
        self.x_coord_entry.grid(row=1, column=1, pady=2)
        
        tk.Label(input_frame, text="Y Coordinate:").grid(row=2, column=0, sticky=tk.W)
        self.y_coord_entry = tk.Entry(input_frame, width=20)
        self.y_coord_entry.grid(row=2, column=1, pady=2)
        
        tk.Button(input_frame, text="Add City", command=self.add_city,
                 bg="#4CAF50", fg="white").grid(row=3, column=0, columnspan=2, pady=5)
        
        # Cities List
        list_frame = tk.LabelFrame(parent, text="Cities Added", padx=10, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.cities_listbox = tk.Listbox(list_frame, height=10)
        self.cities_listbox.pack(fill=tk.BOTH, expand=True)
        
        tk.Button(list_frame, text="Remove Selected", 
                 command=self.remove_city).pack(pady=5)
        
        # Control Buttons
        button_frame = tk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.start_button = tk.Button(button_frame, text="Start", 
                                      command=self.start_solve,
                                      bg="#2196F3", fg="white", height=2)
        self.start_button.pack(fill=tk.X, pady=2)
        
        self.pause_button = tk.Button(button_frame, text="Pause", 
                                      command=self.pause_solve,
                                      bg="#FF9800", fg="white", height=2,
                                      state=tk.DISABLED)
        self.pause_button.pack(fill=tk.X, pady=2)
        
        self.reset_button = tk.Button(button_frame, text="Reset", 
                                      command=self.reset_solve,
                                      bg="#F44336", fg="white", height=2)
        self.reset_button.pack(fill=tk.X, pady=2)
        
        # Results Display
        results_frame = tk.LabelFrame(parent, text="Results", padx=10, pady=10)
        results_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.distance_label = tk.Label(results_frame, 
                                       text="Total Distance: N/A",
                                       font=("Arial", 12, "bold"))
        self.distance_label.pack()
        
        self.status_label = tk.Label(results_frame, 
                                     text="Status: Ready",
                                     font=("Arial", 10))
        self.status_label.pack()
        
    def setup_canvas(self, parent):
        """Setup the visualization canvas"""
        canvas_label = tk.Label(parent, text="Tour Visualization", 
                               font=("Arial", 14, "bold"))
        canvas_label.pack(pady=5)
        
        self.canvas = tk.Canvas(parent, bg="white", highlightthickness=1,
                               highlightbackground="gray")
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Instructions
        instructions = tk.Label(parent, 
                               text="Add at least 4 cities to start solving TSP",
                               font=("Arial", 9), fg="gray")
        instructions.pack(pady=5)
        
    def add_city(self):
        """Add a city to the list"""
        try:
            name = self.city_name_entry.get().strip()
            x = float(self.x_coord_entry.get())
            y = float(self.y_coord_entry.get())
            
            if not name:
                messagebox.showwarning("Invalid Input", "Please enter a city name")
                return
            
            # Check if city already exists
            if any(city[0] == name for city in self.cities):
                messagebox.showwarning("Duplicate", f"City '{name}' already exists")
                return
            
            self.cities.append((name, x, y))
            self.cities_listbox.insert(tk.END, f"{name} ({x}, {y})")
            
            # Clear entries
            self.city_name_entry.delete(0, tk.END)
            self.x_coord_entry.delete(0, tk.END)
            self.y_coord_entry.delete(0, tk.END)
            
            # Draw city on canvas
            self.draw_cities()
            
            self.status_label.config(text=f"Status: {len(self.cities)} cities added")
            
        except ValueError:
            messagebox.showerror("Invalid Input", 
                                "Please enter valid numeric coordinates")
    
    def remove_city(self):
        """Remove selected city from the list"""
        selection = self.cities_listbox.curselection()
        if selection:
            index = selection[0]
            self.cities.pop(index)
            self.cities_listbox.delete(index)
            self.draw_cities()
            self.status_label.config(text=f"Status: {len(self.cities)} cities added")
    
    def draw_cities(self):
        """Draw all cities on the canvas"""
        self.canvas.delete("all")
        
        if not self.cities:
            return
        
        # Get canvas dimensions
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width <= 1 or height <= 1:
            width = 600
            height = 500
        
        # Find min/max coordinates for scaling
        if len(self.cities) > 0:
            x_coords = [city[1] for city in self.cities]
            y_coords = [city[2] for city in self.cities]
            
            x_min, x_max = min(x_coords), max(x_coords)
            y_min, y_max = min(y_coords), max(y_coords)
            
            # Add padding
            padding = 50
            x_range = x_max - x_min if x_max != x_min else 1
            y_range = y_max - y_min if y_max != y_min else 1
            
            # Draw cities
            for name, x, y in self.cities:
                # Scale coordinates
                canvas_x = padding + ((x - x_min) / x_range) * (width - 2 * padding)
                canvas_y = padding + ((y - y_min) / y_range) * (height - 2 * padding)
                
                # Draw city as circle
                r = 8
                self.canvas.create_oval(canvas_x - r, canvas_y - r,
                                       canvas_x + r, canvas_y + r,
                                       fill="blue", outline="darkblue", width=2)
                
                # Draw city name
                self.canvas.create_text(canvas_x, canvas_y - 15,
                                       text=name, font=("Arial", 9, "bold"))
    
    def start_solve(self):
        """Start solving TSP using Branch and Bound"""
        if len(self.cities) < 4:
            messagebox.showwarning("Insufficient Cities", 
                                  "Please add at least 4 cities to solve TSP")
            return
        
        self.is_running = True
        self.is_paused = False
        self.start_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        self.status_label.config(text="Status: Solving...")
        
        # Create solver instance
        self.tsp_solver = BranchAndBoundTSP(self.cities)
        
        # Solve (this is placeholder - will be implemented in algorithm.py)
        try:
            self.solution, self.total_distance = self.tsp_solver.solve()
            self.draw_solution()
            self.distance_label.config(text=f"Total Distance: {self.total_distance:.2f}")
            self.status_label.config(text="Status: Solution Found!")
        except Exception as e:
            messagebox.showerror("Error", f"Error solving TSP: {str(e)}")
            self.status_label.config(text="Status: Error occurred")
        finally:
            self.is_running = False
            self.start_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.DISABLED)
    
    def pause_solve(self):
        """Pause the solving process"""
        if self.is_running and not self.is_paused:
            self.is_paused = True
            self.pause_button.config(text="Resume")
            self.status_label.config(text="Status: Paused")
        elif self.is_paused:
            self.is_paused = False
            self.pause_button.config(text="Pause")
            self.status_label.config(text="Status: Solving...")
    
    def reset_solve(self):
        """Reset the solver and clear visualization"""
        self.is_running = False
        self.is_paused = False
        self.solution = None
        self.total_distance = 0
        self.tsp_solver = None
        
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED, text="Pause")
        self.distance_label.config(text="Total Distance: N/A")
        self.status_label.config(text="Status: Reset")
        
        self.draw_cities()
    
    def draw_solution(self):
        """Draw the solution tour on canvas"""
        self.draw_cities()
        
        if not self.solution or len(self.solution) < 2:
            return
        
        # Get canvas dimensions
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width <= 1 or height <= 1:
            width = 600
            height = 500
        
        # Get coordinates for scaling
        x_coords = [city[1] for city in self.cities]
        y_coords = [city[2] for city in self.cities]
        
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)
        
        padding = 50
        x_range = x_max - x_min if x_max != x_min else 1
        y_range = y_max - y_min if y_max != y_min else 1
        
        # Draw tour lines
        for i in range(len(self.solution)):
            city1_idx = self.solution[i]
            city2_idx = self.solution[(i + 1) % len(self.solution)]
            
            city1 = self.cities[city1_idx]
            city2 = self.cities[city2_idx]
            
            # Scale coordinates
            x1 = padding + ((city1[1] - x_min) / x_range) * (width - 2 * padding)
            y1 = padding + ((city1[2] - y_min) / y_range) * (height - 2 * padding)
            x2 = padding + ((city2[1] - x_min) / x_range) * (width - 2 * padding)
            y2 = padding + ((city2[2] - y_min) / y_range) * (height - 2 * padding)
            
            # Draw line
            self.canvas.create_line(x1, y1, x2, y2, fill="red", width=2,
                                   arrow=tk.LAST)
    
    def run(self):
        """Start the application main loop"""
        self.root.mainloop()