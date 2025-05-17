import sys
from PyQt5.QtWidgets import QApplication
from controller.network_controller import NetworkController


if __name__ == '__main__':
    app = QApplication(sys.argv)
    controller = NetworkController()
    controller.view.show()
    sys.exit(app.exec_())