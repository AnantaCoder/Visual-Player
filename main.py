import sys
from PyQt5 import QtWidgets
from gui.main_window import MainWindow  # Import the MainWindow class from gui/main.py

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()  # Instantiate your main window (the neon guitar player)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
