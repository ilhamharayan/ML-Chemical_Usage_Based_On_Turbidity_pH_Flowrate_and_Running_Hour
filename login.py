import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6.QtCore import Qt
import mysql.connector
from login_menu import Ui_login
from main import MainApp

class Login(QMainWindow, Ui_login):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.button_login.clicked.connect(self.handle_login)

    def handle_login(self):
        username = self.username.text()
        password = self.password.text()

        # Koneksi ke database MySQL
        try:
            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='chemical_usage'
            )
            cursor = conn.cursor()
            query = "SELECT * FROM administrator WHERE username = %s AND password = %s"
            cursor.execute(query, (username, password))
            result = cursor.fetchone()

            if result:
                QMessageBox.information(self, "Success", "Login berhasil!")
                self.open_main_app()
            else:
                QMessageBox.warning(self, "Error", "Username atau password yang Anda masukkan salah.")
            
            cursor.close()
            conn.close()

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error", f"Error: {str(err)}")

    def open_main_app(self):
        self.main_app = MainApp()
        self.main_app.show()
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Login()
    window.show()
    sys.exit(app.exec())
