from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QDialog, QTableWidget, QFrame, QAction,
                             QTableWidgetItem, QButtonGroup, QRadioButton, QTextEdit)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import networkx as nx

class NetworkView(QMainWindow):
    """Main application window handling UI components and visualization.
    
    Implements the View component in MVC architecture. Manages user interface
    elements and graph visualization updates.
    
    Attributes:
        controller (NetworkController): Reference to associated controller
        figure (matplotlib.figure.Figure): Main figure for graph visualization
        canvas (FigureCanvas): Canvas for rendering matplotlib figure
    """

    def __init__(self, controller):
        """Initialize view components and set up UI layout.
        
        Args:
            controller (NetworkController): Controller instance to handle interactions
        """
        super().__init__()
        self.controller = controller
        self.init_ui()
        self.create_menu()

    def init_ui(self):
        """Set up main window properties and layout components."""
        self.setWindowTitle("Network Simulator")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget and main layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)

        # Add control panel and visualization components
        control_panel = self.create_control_panel()
        layout.addWidget(control_panel, stretch=1)

        self.figure, self.canvas = self.create_canvas()
        layout.addWidget(self.canvas, stretch=4)

    def create_menu(self):
        """Create and configure the application menu bar with file operations."""
        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')

        # Open Action
        open_action = QAction('&Open', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.controller.load_file)
        file_menu.addAction(open_action)

        # Save Action
        save_action = QAction('&Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.controller.save_graph)
        file_menu.addAction(save_action)

        # New Action
        clear_action = QAction('&New', self)
        clear_action.setShortcut('Ctrl+N')
        clear_action.triggered.connect(self.controller.clear_graph)
        file_menu.addAction(clear_action)

    def create_control_panel(self):
        """Create and configure the control panel with interaction modes and file operations.
        
        Returns:
            QWidget: Configured control panel widget
        """
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Configure layout spacing and margins
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)  # Left, Top, Right, Bottom

        # Initialize mode selection radio buttons
        self.mode_group = QButtonGroup()
        modes = [
            ("Add Node", "add_node"),
            ("Add Edge", "add_edge"),
            ("View Mode", "view")
        ]
        
        # Create mode selection buttons
        for text, mode in modes:
            btn = QRadioButton(text)
            btn.mode = mode
            self.mode_group.addButton(btn)
            layout.addWidget(btn, alignment=Qt.AlignTop)

        # Add visual separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setLineWidth(1)
        separator.setStyleSheet("color: #cccccc;")
        layout.addWidget(separator)

        # Create file operation buttons
        file_buttons = [
            ("Open File", self.controller.load_file),
            ("Save Graph", self.controller.save_graph),
            ("Clear All", self.controller.clear_graph),
            ("Help", self.show_help_dialog)
        ]
        
        for btn_text, handler in file_buttons:
            print(f"Creating button: {btn_text}")
            btn = QPushButton(btn_text)
            btn.clicked.connect(handler)
            btn.setFixedHeight(30)
            layout.addWidget(btn)

        # Add spacer to keep elements at top
        layout.addStretch()

        # Set default mode to "View"
        self.mode_group.buttons()[2].setChecked(True)
        
        return panel

    def create_canvas(self):
        """Initialize matplotlib figure and canvas for graph visualization.
        
        Returns:
            tuple: (figure, canvas) tuple for matplotlib visualization
        """
        figure = plt.figure()
        canvas = FigureCanvas(figure)
        ax = figure.add_subplot(111)
        
        # Configure initial empty canvas properties
        ax.set_xlim(-1, 1)
        ax.set_ylim(-1, 1)
        ax.grid(False)
        ax.set_facecolor('white')

        # Connect canvas click events to controller handler
        canvas.mpl_connect('button_press_event', self.controller.handle_canvas_click)
        return figure, canvas

    def update_visualization(self, model):
        """Update graph visualization based on current model state.
        
        Args:
            model (NetworkModel): Data model containing graph structure
        """
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        if model.G.nodes:
            pos = model.node_positions
            # Draw network nodes and edges
            nx.draw(
                model.G, pos, 
                ax=ax, 
                with_labels=True, 
                node_color='skyblue', 
                node_size=800
            )
            # Add edge weight labels
            edge_labels = nx.get_edge_attributes(model.G, 'weight')
            nx.draw_networkx_edge_labels(model.G, pos, edge_labels=edge_labels, ax=ax)
            
            # Adjust viewport to contain all nodes
            x_vals = [x for x, y in pos.values()]
            y_vals = [y for x, y in pos.values()]
            ax.set_xlim(min(x_vals)-1, max(x_vals)+1)
            ax.set_ylim(min(y_vals)-1, max(y_vals)+1)
        else:
            # Maintain default viewport for empty graph
            ax.set_xlim(-1, 1)
            ax.set_ylim(-1, 1)
        
        self.canvas.draw()

    def show_forwarding_table(self, node, table_data):
        """Display forwarding table for a node in dialog window.
        
        Args:
            node (str): Node identifier for table header
            table_data (dict): Forwarding table data {destination: next_hop}
        """
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Forwarding Table - {node}")
        dialog.resize(400, 500)
        
        layout = QVBoxLayout(dialog)
        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Destination", "Next Hop"])
        table.setRowCount(len(table_data))
        
        # Populate table with forwarding data
        for row, (dest, hop) in enumerate(table_data.items()):
            table.setItem(row, 0, QTableWidgetItem(dest))
            table.setItem(row, 1, QTableWidgetItem(hop))
        
        layout.addWidget(table)
        dialog.exec_()

    def show_help_dialog(self):
        """Display help documentation in a scrollable window."""
        help_text =  """Network Simulator Help

                        Keyboard Shortcuts:
                        N - Enter Node Creation Mode
                        E - Enter Edge Creation Mode
                        C - Delete Node under cursor
                        D - Delete Edge near cursor
                        Ctrl+O - Open Network File
                        Ctrl+S - Save Network File
                        Ctrl+N - Clear Current Network

                        Mouse Actions:
                        Left Click (Add Node Mode) - Place new node
                        Left Click (Add Edge Mode) - Select nodes to connect
                        Left Click (View Mode) - Show node forwarding table
                        Right Click - Pan view
                        Scroll - Zoom in/out

                        Menu Operations:
                        File -> Open - Load network from file
                        File -> Save - Save current network
                        File -> New - Clear current network"""

        dialog = QDialog(self)
        dialog.setWindowTitle("Help Documentation")
        dialog.resize(500, 400)
        
        layout = QVBoxLayout(dialog)
        text_edit = QTextEdit()
        text_edit.setPlainText(help_text)
        text_edit.setReadOnly(True)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        
        layout.addWidget(text_edit)
        layout.addWidget(close_btn)
        dialog.exec_()

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts for deletion operations."""
        key = event.key()
        
        if key == Qt.Key_N:
            self.controller.set_mode('add_node')
        elif key == Qt.Key_E:
            self.controller.set_mode('add_edge')
        elif key == Qt.Key_C:
            self._handle_delete_node()
        elif key == Qt.Key_D:
            self._handle_delete_edge()
        elif key == Qt.Key_Escape:
            self.controller.set_mode('view')
        else:
            super().keyPressEvent(event)

    def _handle_delete_node(self):
        """Delete node under cursor position."""
        pos = self.canvas.mapFromGlobal(QCursor.pos())
        x, y = self._convert_pos_to_data(pos)
        self.controller.delete_node_at(x, y)

    def _handle_delete_edge(self):
        """Delete edge nearest to cursor position."""
        pos = self.canvas.mapFromGlobal(QCursor.pos())
        x, y = self._convert_pos_to_data(pos)
        self.controller.delete_edge_near(x, y)

    def _convert_pos_to_data(self, pos):
        """Convert widget position to data coordinates."""
        ax = self.figure.gca()
        x_widget = pos.x()
        y_widget = pos.y()
        return ax.transData.inverted().transform((x_widget, y_widget))