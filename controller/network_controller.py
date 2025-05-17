from PyQt5.QtWidgets import QInputDialog, QMessageBox, QFileDialog
from model.network_model import NetworkModel
from view.network_view import NetworkView

class NetworkController:
    """Controller class implementing the application logic for the network simulator.
    
    Acts as mediator between the NetworkModel (data) and NetworkView (UI),
    handling user interactions and updating both components accordingly.
    
    Attributes:
        model (NetworkModel): Instance of the network data model
        view (NetworkView): Instance of the GUI view component
        current_mode (str): Current interaction mode ('view', 'add_node', 'add_edge')
        selected_node (str): Currently selected node for edge creation
    """

    def __init__(self):
        """Initialize controller with model, view, and default settings."""
        self.model = NetworkModel()
        self.view = NetworkView(self)
        self.current_mode = "view"
        self.selected_node = None
        
        # Connect mode radio buttons to update handler
        for btn in self.view.mode_group.buttons():
            btn.toggled.connect(self.update_mode)

    def update_mode(self):
        """Update current interaction mode based on selected radio button.
        
        Triggered when user changes mode selection. Updates the controller's
        current_mode attribute to match the selected UI mode.
        """
        self.current_mode = self.view.mode_group.checkedButton().mode

    def handle_canvas_click(self, event):
        """Handle canvas click events based on current interaction mode.
        
        Args:
            event (matplotlib.backend_bases.MouseEvent): Mouse click event
                containing coordinates and other click details
        """
        if not event.inaxes:  # Ignore clicks outside drawing area
            return

        x, y = event.xdata, event.ydata
        
        # Route to appropriate handler based on current mode
        if self.current_mode == "add_node":
            self.add_node(x, y)
        elif self.current_mode == "add_edge":
            self.handle_edge_creation(x, y)
        elif self.current_mode == "view":
            self.show_node_info(x, y)

    def add_node(self, x, y):
        """Add new node to the network at specified coordinates.
        
        Args:
            x (float): X-coordinate of new node position
            y (float): Y-coordinate of new node position
        """
        name, ok = QInputDialog.getText(self.view, "New Node", "Enter node name:")
        if ok and name:
            self.model.add_node(name, (x, y))
            self.view.update_visualization(self.model)

    def handle_edge_creation(self, x, y):
        """Handle multi-step edge creation process between two nodes.
        
        Args:
            x (float): X-coordinate of click location
            y (float): Y-coordinate of click location
        """
        node = self.find_nearest_node(x, y)
        if node:
            if not self.selected_node:  # First node selection
                self.selected_node = node
            else:  # Second node selection - complete edge
                weight, ok = QInputDialog.getInt(
                    self.view, "Edge Weight", "Enter weight:", 1, 1, 100
                )
                if ok:
                    self.model.add_edge(self.selected_node, node, weight)
                    self.selected_node = None
                    self.view.update_visualization(self.model)

    def show_node_info(self, x, y):
        """Display forwarding table for node nearest to click location.
        
        Args:
            x (float): X-coordinate of click location
            y (float): Y-coordinate of click location
        """
        node = self.find_nearest_node(x, y)
        if node:
            table_data = self.model.get_forwarding_table(node)
            self.view.show_forwarding_table(node, table_data)

    def find_nearest_node(self, x, y):
        """Find network node closest to specified coordinates.
        
        Args:
            x (float): X-coordinate to check
            y (float): Y-coordinate to check
            
        Returns:
            str: Name of nearest node within threshold distance, or None
        """
        min_dist = float('inf')
        nearest = None
        for node, (nx, ny) in self.model.node_positions.items():
            dist = (nx - x)**2 + (ny - y)**2
            if dist < min_dist and dist < 0.1:  # Threshold of 0.1^2 units
                min_dist = dist
                nearest = node
        return nearest

    def load_file(self):
        """Handle file loading operation with error checking."""
        path, _ = QFileDialog.getOpenFileName(
            self.view, "Open Network File", "", "Text Files (*.txt)"
        )
        if path:
            try:
                self.model.load_from_file(path)
                self.view.update_visualization(self.model)
            except Exception as e:
                self.handle_error(f"Load Error: {str(e)}")

    def save_graph(self):
        """Handle file saving operation with error checking."""
        path, _ = QFileDialog.getSaveFileName(
            self.view, "Save Network File", "", "Text Files (*.txt)"
        )
        if path:
            try:
                self.model.save_to_file(path)
            except Exception as e:
                self.handle_error(f"Save Error: {str(e)}")

    def clear_graph(self):
        """Reset application state by clearing model and updating view."""
        self.model.clear()
        self.view.update_visualization(self.model)

    def handle_error(self, message):
        """Display error messages to user in standardized format.
        
        Args:
            message (str): Descriptive error message to display
        """
        QMessageBox.critical(self.view, "Error", message)