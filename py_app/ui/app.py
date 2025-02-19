import sys

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QAction, QCursor
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QWidget, QVBoxLayout, QLineEdit, QMenu


# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.button_is_checked = True

        self.setWindowTitle("File Flow")

        layout = QVBoxLayout()


        self.label = QLabel("<h1>This is a QLabel object<h1>")
        self.mouse_label = QLabel("What's the mouse doing?")
        self.button = QPushButton("Click Here")

        self.input = QLineEdit()
        self.input.textChanged.connect(self.change_label)
        
        

        #self.button.setCheckable(True) #acts a bit like a switch or toggle rather than a button
        self.button.clicked.connect(self.clickedbutton)
        self.windowTitleChanged.connect(self.the_window_title_changed)

        layout.addWidget(self.label)
        layout.addWidget(self.mouse_label)
        layout.addWidget(self.input)
        layout.addWidget(self.button)


        window = QWidget()
        window.setLayout(layout)

        #self.setMinimumSize(QSize(400, 300))

        # Set the central widget of the Window.
        self.setCentralWidget(window)
    
    def change_label(self, text):
        self.label.setText(f"<h1>{text}<h1>")

    def clickedbutton(self):
        self.button_is_checked = self.button.isChecked()
        print("clicked button, is the button checked:", self.button_is_checked)
        self.setWindowTitle("File Flow but better")
        self.label.setText("<h1>This QLabel object was clicked<h1>")

    def the_window_title_changed(self, window_title):
        print("The new window title is: ",  window_title)


    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            # handle the left-button press in here
            self.mouse_label.setText("mousePressEvent LEFT")

        elif e.button() == Qt.MouseButton.MiddleButton:
            # handle the middle-button press in here.
            self.mouse_label.setText("mousePressEvent MIDDLE")

        elif e.button() == Qt.MouseButton.RightButton:
            # handle the right-button press in here.
            self.mouse_label.setText("mousePressEvent RIGHT")
            self.on_context_menu()

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.mouse_label.setText("mouseReleaseEvent LEFT")

        elif e.button() == Qt.MouseButton.MiddleButton:
            self.mouse_label.setText("mouseReleaseEvent MIDDLE")

        elif e.button() == Qt.MouseButton.RightButton:
            self.mouse_label.setText("mouseReleaseEvent RIGHT")

    def mouseDoubleClickEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.mouse_label.setText("mouseDoubleClickEvent LEFT")

        elif e.button() == Qt.MouseButton.MiddleButton:
            self.mouse_label.setText("mouseDoubleClickEvent MIDDLE")

        elif e.button() == Qt.MouseButton.RightButton:
            self.mouse_label.setText("mouseDoubleClickEvent RIGHT")

    def on_context_menu(self):
        context = QMenu(self)
        context.addAction(QAction("test 1", self))
        context.addAction(QAction("test 2", self))
        context.addAction(QAction("test 3", self))
        context.exec(QCursor.pos())




app = QApplication(sys.argv)

window = MainWindow()
#window.setWindowTitle("File Flow")
#window.setGeometry(50, 50, 800, 300)

window.show()

app.exec()