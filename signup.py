import sys
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QRadioButton,
    QButtonGroup,
    QMessageBox,
    QGroupBox,
)

from firebase import addUser
from login import LoginWindow

ASSET_FILES = ["avatar1.png", "avatar2.png", "avatar3.png"]

class SignupWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.login_window = None
        self.setWindowTitle("Signup")
        self.resize(700, 350)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(100, 100)
        self.avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.avatar_label.setStyleSheet("border: 1px solid #bbb; border-radius: 8px;")

        self.avatar_group = QButtonGroup()
        self.avatar_buttons = []
        avatar_box = QGroupBox("Choose avatar")
        avatar_layout = QHBoxLayout()

        script_dir = Path(__file__).parent
        self.avatar_pixmaps = []
        for i, fname in enumerate(ASSET_FILES):
            path = script_dir / fname
            rb = QRadioButton()
            rb.setObjectName(f"avatar_rb_{i}")
            rb.clicked.connect(self.on_avatar_selected)

            if path.exists():
                pix = QPixmap(str(path)).scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.avatar_pixmaps.append(pix)
                icon_label = QLabel()
                icon_label.setPixmap(pix)
                icon_label.setFixedSize(64, 64)
                icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                container = QVBoxLayout()
                container.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
                container.addWidget(rb, alignment=Qt.AlignmentFlag.AlignCenter)
                widget = QWidget()
                widget.setLayout(container)
                avatar_layout.addWidget(widget)
            else:
                emoji = QLabel("😀" if i == 0 else "😎" if i == 1 else "🦊")
                emoji.setFixedSize(64, 64)
                emoji.setAlignment(Qt.AlignmentFlag.AlignCenter)
                container = QVBoxLayout()
                container.addWidget(emoji, alignment=Qt.AlignmentFlag.AlignCenter)
                container.addWidget(rb, alignment=Qt.AlignmentFlag.AlignCenter)
                widget = QWidget()
                widget.setLayout(container)
                avatar_layout.addWidget(widget)
                self.avatar_pixmaps.append(None)

            self.avatar_group.addButton(rb, i)
            self.avatar_buttons.append(rb)

        avatar_box.setLayout(avatar_layout)

        if self.avatar_buttons:
            self.avatar_buttons[0].setChecked(True)
            self.update_avatar_preview(0)

        signup_btn = QPushButton("Signup")
        signup_btn.clicked.connect(self.on_signup)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.close)

        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Username"))
        left_layout.addWidget(self.username_input)
        left_layout.addWidget(QLabel("Password"))
        left_layout.addWidget(self.password_input)
        left_layout.addStretch()
        left_layout.addWidget(signup_btn)

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.avatar_label)
        right_layout.addWidget(avatar_box)
        right_layout.addStretch()
        right_layout.addWidget(cancel_btn)

        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout, stretch=3)
        main_layout.addLayout(right_layout, stretch=3)

        self.setLayout(main_layout)

    def on_avatar_selected(self):
        idx = self.avatar_group.checkedId()
        if idx >= 0:
            self.update_avatar_preview(idx)

    def update_avatar_preview(self, idx: int):
        pix = self.avatar_pixmaps[idx]
        if pix:
            self.avatar_label.setPixmap(pix.scaled(self.avatar_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            self.avatar_label.setText("")
        else:
            emoji = "😀" if idx == 0 else "😎" if idx == 1 else "🦊"
            self.avatar_label.setPixmap(QPixmap())
            self.avatar_label.setText(emoji)
            self.avatar_label.setStyleSheet("font-size: 40px; border: 1px solid #bbb; border-radius: 8px;")

    def on_signup(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        avatar_id = self.avatar_group.checkedId()

        if not username or not password:
            QMessageBox.warning(self, "Missing", "Please enter both username and password.")
            return

        addUser(username, password, avatar_id)

        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()


def main():
    app = QApplication(sys.argv)
    win = SignupWindow() 
    win.show()
    sys.exit(app.exec())
if __name__ == "__main__":
    main()