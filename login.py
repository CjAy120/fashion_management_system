from PyQt6.QtCore import pyqtSignal, Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtWidgets import QDialog, QMessageBox, QLabel, QGraphicsOpacityEffect
from databaseconn import register_user, verify_user
from manager import managerDashboard
from PyQt6.uic import loadUi

class Login(QDialog):
    def __init__(self):
        super().__init__()
        loadUi('login.ui', self)

        self.loginBtn.clicked.connect(self.handle_login)
        self.registerBtn.clicked.connect(self.handle_registration)
        self.login_link.clicked.connect(lambda: self.pop_page(1))
        self.createUser_link.clicked.connect(lambda: self.pop_page(0))

    def handle_registration(self):
        fullname = self.fullnameFld.text().strip()
        email = self.emailFld.text().strip()
        password = self.passFld.text().strip()
        confirm  = self.confpassFld.text().strip()

        if not fullname or not email or not password or not confirm:
            QMessageBox.warning(self, 'Registration error', 'Fill all the fields')
            return

        if password != confirm:
            QMessageBox.warning(self, 'Registration error', 'Passwords do not match')
            return

        try:
            success = register_user(fullname, email, password)
            if success:
                QMessageBox.information(self, 'Registration success', 'You are now registered')
                self.pop_page(1)
            else:
                QMessageBox.warning(self, 'Registration error', 'Something went wrong')
        except Exception as e:
            QMessageBox.warning(self, 'Registration error', str(e))

    def handle_login(self):
        userid =  self.loginEmailFld.text().strip()
        password = self.logPassFld.text().strip()

        if not userid or not password:
            QMessageBox.warning(self, 'Login error', 'Please fill all the fields')
            return

        try:
            user = verify_user(userid, password)
            if user:
                self.manager_window = managerDashboard(None, user['fullname'])
                self.manager_window.show()
                self.close()
            else:
                QMessageBox.warning(self, 'Login error', 'Something went wrong')
        except Exception as e:
            QMessageBox.warning(self, 'Login error', str(e))

    def pop_page(self, index):
        new_page = self.stackedWidget.widget(index)
        self.stackedWidget.setCurrentIndex(index)

        new_page.setGraphicsEffect(None)
        effect = QGraphicsOpacityEffect(new_page)
        new_page.setGraphicsEffect(effect)

        fade_anim = QPropertyAnimation(effect, b"opacity")
        fade_anim.setDuration(700)
        fade_anim.setStartValue(0.0)
        fade_anim.setEndValue(1.0)
        fade_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)

        self.page_anim = fade_anim
        fade_anim.start()


class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()