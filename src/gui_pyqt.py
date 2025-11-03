"""
PyQt5 GUI Module for TSP Branch and Bound Solver
Modern, professional interface with enhanced visualization
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QLineEdit, QListWidget, 
                             QGroupBox, QGridLayout, QMessageBox, QProgressBar,
                             QSplitter, QFrame)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor
import sys

from src.algorithm import BranchAndBoundTSP
from src.canvas_widget import TSPCanvas


class SolverThread(QThread):
    """Background thread for running the TSP solver without freezing GUI"""
    
    # Signals for communication with main thread
    progress_update = pyqtSignal(dict)
    solution_found = pyqtSignal(list, float)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, cities):
        super().__init__()
        self.cities = cities
        self.solver = None
        self.is_paused = False
        self.should_stop = False
        
    def run(self):
        """Execute the solving in background"""
        try:
            self.solver = BranchAndBoundTSP(self.cities)
            self.solver.set_progress_callback(self.on_progress)
            
            # Solve the TSP
            path, distance = self.solver.solve()
            
            if not self.should_stop:
                self.solution_found.emit(path, distance)
                
        except Exception as e:
            self.error_occurred.emit(str(e))
    
    def on_progress(self, stats):
        """Handle progress updates from solver"""
        if not self.should_stop:
            self.progress_update.emit(stats)
    
    def stop(self):
        """Stop the solver"""
        self.should_stop = True


class TSPMainWindow(QMainWindow):
    """Main application window for TSP solver"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TSP Branch & Bound Solver - Advanced Edition")
        self.setGeometry(100, 100, 1400, 800)
        
        # Data
        self.cities = []
        self.solution = None
        self.total_distance = 0
        self.solver_thread = None
        
        # Setup UI
        self.init_ui()
        self.apply_styles()
        
    def init_ui(self):
        """Initialize the user interface"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout - horizontal splitter
        main_layout = QHBoxLayout(central_widget)
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - Controls
        left_panel = self.create_control_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Visualization
        right_panel = self.create_visualization_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter sizes (30% left, 70% right)
        splitter.setSizes([400, 1000])
        
    def create_control_panel(self):
        """Create the left control panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("🌍 TSP Solver Control Panel")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # City Input Section
        input_group = QGroupBox("Add New City")
        input_layout = QGridLayout()
        
        input_layout.addWidget(QLabel("City Name:"), 0, 0)
        self.city_name_input = QLineEdit()
        self.city_name_input.setPlaceholderText("e.g., London")
        input_layout.addWidget(self.city_name_input, 0, 1)
        
        input_layout.addWidget(QLabel("X Coordinate:"), 1, 0)
        self.x_coord_input = QLineEdit()
        self.x_coord_input.setPlaceholderText("e.g., 100.5")
        input_layout.addWidget(self.x_coord_input, 1, 1)
        
        input_layout.addWidget(QLabel("Y Coordinate:"), 2, 0)
        self.y_coord_input = QLineEdit()
        self.y_coord_input.setPlaceholderText("e.g., 250.3")
        input_layout.addWidget(self.y_coord_input, 2, 1)
        
        self.add_city_btn = QPushButton("➕ Add City")
        self.add_city_btn.clicked.connect(self.add_city)
        input_layout.addWidget(self.add_city_btn, 3, 0, 1, 2)
        
        self.load_sample_btn = QPushButton("📋 Load Sample Cities")
        self.load_sample_btn.clicked.connect(self.load_sample_cities)
        input_layout.addWidget(self.load_sample_btn, 4, 0, 1, 2)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # Cities List
        list_group = QGroupBox("Cities Added")
        list_layout = QVBoxLayout()
        
        self.cities_list = QListWidget()
        self.cities_list.setMaximumHeight(150)
        list_layout.addWidget(self.cities_list)
        
        self.remove_city_btn = QPushButton("🗑️ Remove Selected")
        self.remove_city_btn.clicked.connect(self.remove_city)
        list_layout.addWidget(self.remove_city_btn)
        
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)
        
        # Control Buttons
        control_group = QGroupBox("Solver Controls")
        control_layout = QVBoxLayout()
        
        self.start_btn = QPushButton("▶️ Start Solving")
        self.start_btn.clicked.connect(self.start_solving)
        self.start_btn.setMinimumHeight(45)
        control_layout.addWidget(self.start_btn)
        
        self.pause_btn = QPushButton("⏸️ Pause")
        self.pause_btn.clicked.connect(self.pause_solving)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setMinimumHeight(45)
        control_layout.addWidget(self.pause_btn)
        
        self.reset_btn = QPushButton("🔄 Reset")
        self.reset_btn.clicked.connect(self.reset_all)
        self.reset_btn.setMinimumHeight(45)
        control_layout.addWidget(self.reset_btn)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # Statistics Display
        stats_group = QGroupBox("Algorithm Statistics")
        stats_layout = QVBoxLayout()
        
        self.nodes_explored_label = QLabel("Nodes Explored: 0")
        self.branches_pruned_label = QLabel("Branches Pruned: 0")
        self.max_depth_label = QLabel("Max Depth Reached: 0")
        self.computation_time_label = QLabel("Computation Time: 0.000s")
        self.efficiency_label = QLabel("Pruning Efficiency: 0.0%")
        
        for label in [self.nodes_explored_label, self.branches_pruned_label,
                     self.max_depth_label, self.computation_time_label,
                     self.efficiency_label]:
            label.setFont(QFont("Consolas", 9))
            stats_layout.addWidget(label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.setVisible(False)
        stats_layout.addWidget(self.progress_bar)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Results Display
        results_group = QGroupBox("Results")
        results_layout = QVBoxLayout()
        
        self.distance_label = QLabel("Total Distance: N/A")
        self.distance_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.distance_label.setStyleSheet("color: #2E7D32;")
        results_layout.addWidget(self.distance_label)
        
        self.status_label = QLabel("Status: Ready")
        self.status_label.setFont(QFont("Arial", 10))
        results_layout.addWidget(self.status_label)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        # Add stretch to push everything up
        layout.addStretch()
        
        return panel
    
    def create_visualization_panel(self):
        """Create the right visualization panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Title
        title = QLabel("Tour Visualization")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Canvas for drawing
        self.canvas = TSPCanvas()
        layout.addWidget(self.canvas)
        
        # Instructions
        instructions = QLabel("💡 Add at least 4 cities and click 'Start Solving' to find the optimal tour")
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(instructions)
        
        return panel
    
    def apply_styles(self):
        """Apply modern styling to the application"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
            QLineEdit {
                border: 2px solid #e0e0e0;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
            }
            QListWidget {
                border: 2px solid #e0e0e0;
                border-radius: 5px;
                background-color: white;
            }
            QProgressBar {
                border: 2px solid #e0e0e0;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
        """)
    
    def add_city(self):
        """Add a new city to the list"""
        try:
            name = self.city_name_input.text().strip()
            x = float(self.x_coord_input.text())
            y = float(self.y_coord_input.text())
            
            if not name:
                QMessageBox.warning(self, "Invalid Input", "Please enter a city name")
                return
            
            # Check for duplicates
            if any(city[0] == name for city in self.cities):
                QMessageBox.warning(self, "Duplicate", f"City '{name}' already exists")
                return
            
            # Add city
            self.cities.append((name, x, y))
            self.cities_list.addItem(f"{name} ({x:.1f}, {y:.1f})")
            
            # Clear inputs
            self.city_name_input.clear()
            self.x_coord_input.clear()
            self.y_coord_input.clear()
            self.city_name_input.setFocus()
            
            # Update canvas
            self.canvas.set_cities(self.cities)
            self.status_label.setText(f"Status: {len(self.cities)} cities added")
            
        except ValueError:
            QMessageBox.critical(self, "Invalid Input", 
                               "Please enter valid numeric coordinates")
    
    def remove_city(self):
        """Remove selected city"""
        current_row = self.cities_list.currentRow()
        if current_row >= 0:
            self.cities.pop(current_row)
            self.cities_list.takeItem(current_row)
            self.canvas.set_cities(self.cities)
            self.status_label.setText(f"Status: {len(self.cities)} cities added")
    
    def load_sample_cities(self):
        """Load sample cities for testing"""
        sample_cities = [
            ("New York", 50, 200),
            ("Los Angeles", 300, 350),
            ("Chicago", 150, 100),
            ("Houston", 250, 400),
            ("Phoenix", 400, 300),
            ("Philadelphia", 100, 150),
            ("San Antonio", 350, 450),
            ("San Diego", 450, 400)
        ]
        
        self.cities = sample_cities
        self.cities_list.clear()
        for name, x, y in sample_cities:
            self.cities_list.addItem(f"{name} ({x:.1f}, {y:.1f})")
        
        self.canvas.set_cities(self.cities)
        self.status_label.setText(f"Status: {len(self.cities)} sample cities loaded")
    
    def start_solving(self):
        """Start the TSP solving process"""
        if len(self.cities) < 4:
            QMessageBox.warning(self, "Insufficient Cities",
                              "Please add at least 4 cities to solve TSP")
            return
        
        # Disable controls
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.add_city_btn.setEnabled(False)
        self.load_sample_btn.setEnabled(False)
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.status_label.setText("Status: Solving... Please wait")
        
        # Start solver in background thread
        self.solver_thread = SolverThread(self.cities)
        self.solver_thread.progress_update.connect(self.on_progress_update)
        self.solver_thread.solution_found.connect(self.on_solution_found)
        self.solver_thread.error_occurred.connect(self.on_error)
        self.solver_thread.start()
    
    def on_progress_update(self, stats):
        """Handle progress updates from solver"""
        self.nodes_explored_label.setText(f"Nodes Explored: {stats['nodes_explored']}")
        self.branches_pruned_label.setText(f"Branches Pruned: {stats['branches_pruned']}")
        self.max_depth_label.setText(f"Max Depth Reached: {stats['max_depth']}")
        
        if stats.get('best_cost'):
            self.distance_label.setText(f"Current Best: {stats['best_cost']:.2f}")
    
    def on_solution_found(self, path, distance):
        """Handle solution found"""
        self.solution = path
        self.total_distance = distance
        
        # Update UI
        self.distance_label.setText(f"Total Distance: {distance:.2f}")
        self.status_label.setText("Status: ✅ Solution Found!")
        self.progress_bar.setVisible(False)
        
        # Get final statistics
        if self.solver_thread and self.solver_thread.solver:
            stats = self.solver_thread.solver.get_statistics()
            self.nodes_explored_label.setText(f"Nodes Explored: {stats['nodes_explored']}")
            self.branches_pruned_label.setText(f"Branches Pruned: {stats['branches_pruned']}")
            self.max_depth_label.setText(f"Max Depth Reached: {stats['max_depth_reached']}")
            self.computation_time_label.setText(f"Computation Time: {stats['computation_time']:.3f}s")
            self.efficiency_label.setText(f"Pruning Efficiency: {stats['pruning_efficiency']:.1f}%")
        
        # Draw solution
        self.canvas.set_solution(self.solution)
        
        # Re-enable controls
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.add_city_btn.setEnabled(True)
        self.load_sample_btn.setEnabled(True)
    
    def on_error(self, error_msg):
        """Handle error during solving"""
        QMessageBox.critical(self, "Error", f"An error occurred: {error_msg}")
        self.reset_all()
    
    def pause_solving(self):
        """Pause/Resume solving (placeholder for now)"""
        # This would require more complex threading logic
        QMessageBox.information(self, "Feature", 
                              "Pause/Resume will be fully implemented in next version.\n"
                              "For now, use Reset to stop.")
    
    def reset_all(self):
        """Reset everything"""
        # Stop solver thread if running
        if self.solver_thread and self.solver_thread.isRunning():
            self.solver_thread.stop()
            self.solver_thread.wait()
        
        # Reset data
        self.solution = None
        self.total_distance = 0
        
        # Reset UI
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.add_city_btn.setEnabled(True)
        self.load_sample_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        self.distance_label.setText("Total Distance: N/A")
        self.status_label.setText("Status: Reset - Ready")
        
        self.nodes_explored_label.setText("Nodes Explored: 0")
        self.branches_pruned_label.setText("Branches Pruned: 0")
        self.max_depth_label.setText("Max Depth Reached: 0")
        self.computation_time_label.setText("Computation Time: 0.000s")
        self.efficiency_label.setText("Pruning Efficiency: 0.0%")
        
        # Clear solution from canvas
        self.canvas.clear_solution()