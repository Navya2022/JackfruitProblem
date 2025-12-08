from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout,QMessageBox
)
from PyQt6.QtCore import Qt
import sys
from firebase import checkUser

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Login")
        self.resize(400, 250)

        # --- Username ---
        user_label = QLabel("Username:")
        self.user_input = QLineEdit()

        # --- Password ---
        pass_label = QLabel("Password:")
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)

        # --- Login Button ---
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.login)

        # Layouts
        layout = QVBoxLayout()
        layout.addWidget(user_label)
        layout.addWidget(self.user_input)
        layout.addWidget(pass_label)
        layout.addWidget(self.pass_input)

        layout.addSpacing(15)
        layout.addWidget(login_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def login(self):
        username = self.user_input.text()
        password = self.pass_input.text()
        status = checkUser(username, password)
        if status == "Success":
            QMessageBox.information(self, "Login Successful", "You have logged in successfully!")
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password.")



def main():
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
