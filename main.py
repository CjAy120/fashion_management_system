from PyQt6.QtWidgets import QApplication
from login import Login
import sys

app = QApplication([])

app.setStyleSheet("""
    QWidget {
        color: black;
    }
""")

window = Login()
window.show()
sys.exit(app.exec())