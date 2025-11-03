"""
Custom Canvas Widget for TSP Visualization
Handles drawing cities and tour paths with PyQt5
"""

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPointF, QRectF, QTimer
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont


class TSPCanvas(QWidget):
    """Custom widget for drawing TSP cities and solution tour"""
    
    def __init__(self):
        super().__init__()
        self.setMinimumSize(600, 500)
        self.setStyleSheet("background-color: white; border: 2px solid #e0e0e0; border-radius: 8px;")
        
        # Data
        self.cities = []
        self.solution = None
        self.scaled_cities = []
        
        # Animation
        self.animation_progress = 0
        self.is_animating = False
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate_tour)
        
    def set_cities(self, cities):
        """Set the cities to display"""
        self.cities = cities
        self.solution = None
        self.animation_progress = 0
        self.is_animating = False
        self.update()  # Trigger repaint
    
    def set_solution(self, solution):
        """Set the solution path and start animation"""
        self.solution = solution
        self.animation_progress = 0
        self.is_animating = True
        self.animation_timer.start(30)  # 30ms updates (~33 FPS)
    
    def clear_solution(self):
        """Clear the solution path"""
        self.solution = None
        self.animation_progress = 0
        self.is_animating = False
        self.animation_timer.stop()
        self.update()
    
    def animate_tour(self):
        """Animate the tour drawing"""
        if self.animation_progress < 1.0:
            self.animation_progress += 0.02  # 2% per frame
            self.update()
        else:
            self.is_animating = False
            self.animation_timer.stop()
    
    def scale_coordinates(self):
        """Scale city coordinates to fit canvas"""
        if not self.cities:
            return
        
        width = self.width()
        height = self.height()
        padding = 60
        
        # Extract coordinates
        x_coords = [city[1] for city in self.cities]
        y_coords = [city[2] for city in self.cities]
        
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)
        
        x_range = x_max - x_min if x_max != x_min else 1
        y_range = y_max - y_min if y_max != y_min else 1
        
        # Scale to canvas
        self.scaled_cities = []
        for name, x, y in self.cities:
            canvas_x = padding + ((x - x_min) / x_range) * (width - 2 * padding)
            canvas_y = padding + ((y - y_min) / y_range) * (height - 2 * padding)
            self.scaled_cities.append((name, canvas_x, canvas_y))
    
    def paintEvent(self, event):
        """Draw the cities and tour"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if not self.cities:
            self.draw_empty_state(painter)
            return
        
        # Scale coordinates
        self.scale_coordinates()
        
        # Draw solution tour if exists
        if self.solution and len(self.solution) > 1:
            self.draw_tour(painter)
        
        # Draw cities on top
        self.draw_cities(painter)
    
    def draw_empty_state(self, painter):
        """Draw message when no cities added"""
        painter.setPen(QPen(QColor("#999999")))
        painter.setFont(QFont("Arial", 12))
        
        text = "No cities added yet\nAdd cities using the control panel →"
        rect = self.rect()
        painter.drawText(rect, Qt.AlignCenter, text)
    
    def draw_cities(self, painter):
        """Draw city markers and labels"""
        for i, (name, x, y) in enumerate(self.scaled_cities):
            # Highlight start city differently
            if i == 0:
                color = QColor("#4CAF50")  # Green for start
            else:
                color = QColor("#2196F3")  # Blue for others
            
            # Draw city circle
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(color.darker(120), 2))
            
            radius = 10
            painter.drawEllipse(QPointF(x, y), radius, radius)
            
            # Draw city label
            painter.setPen(QPen(Qt.black))
            painter.setFont(QFont("Arial", 9, QFont.Bold))
            
            # Position label above city
            label_rect = QRectF(x - 40, y - 28, 80, 20)
            painter.drawText(label_rect, Qt.AlignCenter, name)
            
            # Draw city index
            painter.setFont(QFont("Arial", 8))
            index_rect = QRectF(x - 5, y - 3, 10, 10)
            painter.drawText(index_rect, Qt.AlignCenter, str(i))
    
    def draw_tour(self, painter):
        """Draw the tour path with animation"""
        if not self.solution or len(self.solution) < 2:
            return
        
        # Calculate how many edges to draw based on animation progress
        total_edges = len(self.solution)
        edges_to_draw = int(total_edges * self.animation_progress)
        
        # Draw edges
        for i in range(edges_to_draw):
            city1_idx = self.solution[i]
            city2_idx = self.solution[(i + 1) % len(self.solution)]
            
            city1 = self.scaled_cities[city1_idx]
            city2 = self.scaled_cities[city2_idx]
            
            x1, y1 = city1[1], city1[2]
            x2, y2 = city2[1], city2[2]
            
            # Draw line with arrow
            painter.setPen(QPen(QColor("#F44336"), 3, Qt.SolidLine))
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
            
            # Draw arrow head
            self.draw_arrow_head(painter, x1, y1, x2, y2)
            
            # Draw distance label on edge
            if i < total_edges - 1 or self.animation_progress >= 1.0:
                self.draw_edge_distance(painter, x1, y1, x2, y2, city1_idx, city2_idx)
        
        # Draw partial edge if animating
        if self.is_animating and edges_to_draw < total_edges:
            partial_progress = (total_edges * self.animation_progress) - edges_to_draw
            
            city1_idx = self.solution[edges_to_draw]
            city2_idx = self.solution[(edges_to_draw + 1) % len(self.solution)]
            
            city1 = self.scaled_cities[city1_idx]
            city2 = self.scaled_cities[city2_idx]
            
            x1, y1 = city1[1], city1[2]
            x2, y2 = city2[1], city2[2]
            
            # Interpolate
            x_partial = x1 + (x2 - x1) * partial_progress
            y_partial = y1 + (y2 - y1) * partial_progress
            
            painter.setPen(QPen(QColor("#F44336"), 3, Qt.SolidLine))
            painter.drawLine(QPointF(x1, y1), QPointF(x_partial, y_partial))
    
    def draw_arrow_head(self, painter, x1, y1, x2, y2):
        """Draw arrow head at end of edge"""
        import math
        
        # Calculate angle
        angle = math.atan2(y2 - y1, x2 - x1)
        
        # Arrow dimensions
        arrow_size = 12
        arrow_angle = math.pi / 6  # 30 degrees
        
        # Calculate arrow points
        x_back = x2 - arrow_size * math.cos(angle)
        y_back = y2 - arrow_size * math.sin(angle)
        
        x_left = x_back - arrow_size/2 * math.cos(angle + math.pi/2)
        y_left = y_back - arrow_size/2 * math.sin(angle + math.pi/2)
        
        x_right = x_back + arrow_size/2 * math.cos(angle + math.pi/2)
        y_right = y_back + arrow_size/2 * math.sin(angle + math.pi/2)
        
        # Draw arrow head
        painter.setBrush(QBrush(QColor("#F44336")))
        painter.setPen(Qt.NoPen)
        
        points = [
            QPointF(x2, y2),
            QPointF(x_left, y_left),
            QPointF(x_right, y_right)
        ]
        
        painter.drawPolygon(*points)
    
    def draw_edge_distance(self, painter, x1, y1, x2, y2, idx1, idx2):
        """Draw distance label on edge"""
        from src.utilities import calculate_distance
        
        # Calculate actual distance
        city1 = self.cities[idx1]
        city2 = self.cities[idx2]
        distance = calculate_distance(city1[1], city1[2], city2[1], city2[2])
        
        # Midpoint of edge
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        
        # Draw background rectangle for label
        painter.setBrush(QBrush(QColor(255, 255, 255, 230)))
        painter.setPen(QPen(QColor("#666666"), 1))
        
        label_text = f"{distance:.1f}"
        label_rect = QRectF(mid_x - 20, mid_y - 10, 40, 20)
        painter.drawRoundedRect(label_rect, 3, 3)
        
        # Draw text
        painter.setPen(QPen(Qt.black))
        painter.setFont(QFont("Arial", 8))
        painter.drawText(label_rect, Qt.AlignCenter, label_text)