# Network Simulator

A Python-based GUI application for simulating computer networks using graph theory concepts. Implements link-state routing with Dijkstra's algorithm and provides visual network topology management.

## Features

- **Interactive GUI**
  - Add/remove nodes and edges through intuitive interface
  - Visualize network topology with automatic layout
  - View forwarding tables for any node
- **File I/O Support**
  - Save/load network configurations in standardized format
  - Import/export network topologies
- **Routing Features**
  - Custom Dijkstra's algorithm implementation
  - Automatic forwarding table generation
  - Path cost calculations
- **Error Handling**
  - Comprehensive input validation
  - Clear error messages for invalid operations
- **Modular Architecture**
  - MVC design pattern implementation
  - Separate model-view-controller components
  - Extensible codebase

## Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Dependencies
```bash
pip install PyQt5 matplotlib networkx
```

## Usage

### Basic Operations
1. **Adding Nodes**
    - Select "Add Node" mode
    - Click on canvas to place node
    - Enter node name in dialog
2. **Creating Edges**
    - Select "Add Edge" mode
    - Click source node, then destination node
    - Enter edge weight in dialog
3. **Viewing Forwarding Tables**
    - Select "View Mode"
    - Click any node to see its forwarding table

### File Operations
- Load Network: File → Open (Ctrl+O)
- Save Network: File → Save (Ctrl+S)
- Clear Network: File → New (Ctrl+N)

### File Format
Network configurations are stored in `.txt` files with format:
```
nodes_count,edges_count
src_node,dest_node,weight
src_node,dest_node,weight
...
```
#### Example:
```
6,10
u,v,2
u,w,5
u,x,1
x,v,2
v,w,3
x,w,3
w,y,1
x,y,1
w,z,5
y,z,2
```

## Implementation Details

### Architecture
- **Model**: network_model.py
    * Manages graph data structure
    * Handles file I/O operations
    * Implements custom Dijkstra's algorithm

- **View**: network_view.py
    * Handles GUI presentation
    * Manages user interactions
    * Implements visualization using Matplotlib

- **Controller**: network_controller.py
    * Mediates between Model and View
    * Handles application logic
    * Manages event handling

### Algorithm 
- Custom Dijkstra's implementation features:
    * Priority queue optimization
    * O((E+V) log V) time complexity
    * Path reconstruction with next-hop tracking
    * Disconnected node handling