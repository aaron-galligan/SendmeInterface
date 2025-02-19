import sys
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, 
    QLabel, QHBoxLayout, QStackedWidget, QFrame
)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Modern PyQt6 UI")
        self.setGeometry(100, 100, 900, 600)
        #self.setStyleSheet("background-color: #121212; color: white;")  # Dark mode

        # Main Layout
        main_widget = QWidget(self)
        main_layout = QHBoxLayout(main_widget)

        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(200)
        #self.sidebar.setStyleSheet("background-color: #1E1E1E; border-radius: 10px;")

        sidebar_layout = QVBoxLayout(self.sidebar)
        
        self.btn_home = QPushButton("Home")
        self.btn_settings = QPushButton("Settings")
        self.btn_about = QPushButton("About")
        
        #stacks all the buttons in the sidebar layout
        for btn in (self.btn_home, self.btn_settings, self.btn_about):
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()

        # Content Area
        self.stack = QStackedWidget()
        
        self.page_home = QWidget()
        self.page_settings = QWidget()
        self.page_about = QWidget()

        # Add pages
        self.stack.addWidget(self.page_home)
        self.stack.addWidget(self.page_settings)
        self.stack.addWidget(self.page_about)

        # Set home page layout
        home_layout = QVBoxLayout(self.page_home)
        home_layout.addWidget(QLabel("🏠 Home Page", alignment=Qt.AlignmentFlag.AlignCenter))
        
        # Set settings page layout
        settings_layout = QVBoxLayout(self.page_settings)
        settings_layout.addWidget(QLabel("⚙️ Settings Page", alignment=Qt.AlignmentFlag.AlignCenter))

        # Set about page layout
        about_layout = QVBoxLayout(self.page_about)
        about_layout.addWidget(QLabel("ℹ️ About Page", alignment=Qt.AlignmentFlag.AlignCenter))

        # Sidebar Navigation Click Events
        self.btn_home.clicked.connect(lambda: self.stack.setCurrentWidget(self.page_home))
        self.btn_settings.clicked.connect(lambda: self.stack.setCurrentWidget(self.page_settings))
        self.btn_about.clicked.connect(lambda: self.stack.setCurrentWidget(self.page_about))

        # Add widgets to main layout (main_layout is a QHBoxLayout)
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.stack)

        self.setCentralWidget(main_widget)

        


def load_stylesheet( filename):
    with open(filename, "r") as file:
        return file.read()

app = QApplication(sys.argv)
window = MainWindow()

#stylesheet = load_stylesheet("test.qss")
stylesheet = load_stylesheet("C:/Users/aaron/OneDrive/Documents/Programming/Rust/SendmeInterface/py_app/ui/test.qss")
app.setStyleSheet(stylesheet)

window.show()
app.exec()
