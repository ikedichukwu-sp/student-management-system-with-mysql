import sys
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QLabel, QWidget, QGridLayout, QLineEdit, QPushButton, \
    QMainWindow, QTableWidget, QTableWidgetItem, QDialog, QComboBox, QMessageBox, QToolBar, QStatusBar
from PyQt6.QtGui import QAction, QIcon
import sqlite3
import mysql.connector
from PyQt6.QtCore import Qt


class DataBaseConnection:
    def __init__(self, host="localhost", user="root", password="Visual000366@", database="school"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def connect(self):
        connection = mysql.connector.connect(host=self.host, user=self.user, password=self.password,
                                             database=self.database)
        return connection


class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.db = db
        self.setMinimumSize(800, 600)

        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        edit_menu_item = self.menuBar().addMenu("&Edit")

        add_student_action = QAction(QIcon("icons/add.png"), "Add Student", self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        search_action = QAction(QIcon("icons/search.png"), "Search", self)
        search_action.triggered.connect(self.open_search_dialog)
        edit_menu_item.addAction(search_action)

        # create toolbar and add toolbar element
        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        about_action.triggered.connect(self.about)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("ID", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)
        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)

        # create a status bar and add status bar element
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # detect a cell click when any of the student data is clicked on
        self.table.cellClicked.connect(self.cell_clicked)

        self.load_data()

    def cell_clicked(self):
        edith_button = QPushButton("Edit Records")
        edith_button.clicked.connect(self.edith)

        delete_button = QPushButton("Delete Records")
        delete_button.clicked.connect(self.delete)

        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)

        self.statusbar.addWidget(edith_button)
        self.statusbar.addWidget(delete_button)

    def edith(self):
        QDialog = EdithDialog(self)
        QDialog.exec()

    def delete(self):
        QDialog = DeleteDialog(self)
        QDialog.exec()

    def about(self):
        dialog = AboutDialog()
        dialog.exec()

    def load_data(self):
        data = self.db.get_all_students()
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(data):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    def open_search_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Search Student")
        dialog.setFixedSize(300, 150)

        layout = QVBoxLayout()

        search_input = QLineEdit()
        search_input.setPlaceholderText("Enter student name")
        layout.addWidget(search_input)

        search_button = QPushButton("Search")
        layout.addWidget(search_button)

        result_label = QLabel()
        layout.addWidget(result_label)

        dialog.setLayout(layout)

        def handle_search():
            name = search_input.text()
            if name.strip():
                results = self.db.search(name)
                if results:
                    result_label.setText(f"Found: {results}")
                else:
                    result_label.setText("No results found.")
            else:
                result_label.setText("Please enter a name.")

        search_button.clicked.connect(handle_search)
        dialog.exec()

    def insert(self):
        dialog = InsertDialog(self)
        dialog.exec()


class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content = """
        This app was created during the course "the python mega course".
        Feel free to modify and reuse this app.
        """
        self.setText(content)
        self.setIcon(QMessageBox.Information)
        self.setStandardButtons(QMessageBox.Ok)


class InsertDialog(QDialog):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("Insert Student Data")
        self.setFixedSize(300, 300)

        layout = QVBoxLayout()

        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        self.course_name = QComboBox()
        self.course_name.addItems(["Biology", "Physics", "Astronomy", "Maths"])
        layout.addWidget(self.course_name)

        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        button = QPushButton("Register")
        button.clicked.connect(self.add_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def add_student(self):
        name = self.student_name.text()
        course = self.course_name.currentText()
        mobile = self.mobile.text()

        if not name.strip() or not mobile.strip():
            QMessageBox.warning(self, "Input Error", "Please fill all fields.")
            return

        self.main_window.db.add_student(name, course, mobile)
        self.main_window.load_data()
        self.close()


class StudentDatabase:
    def __init__(self):
        self.initialize()

    def initialize(self):
        connection = DataBaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name TEXT NOT NULL,
            course TEXT NOT NULL,
            mobile TEXT NOT NULL
        )
        """)
        connection.commit()
        connection.close()

    def get_all_students(self):
        connection = DataBaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students")
        result = cursor.fetchall()
        connection.close()
        return result

    def add_student(self, name, course, mobile):
        connection = DataBaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, course, mobile) VALUES (%s, %s, %s)", (name, course, mobile))
        connection.commit()
        connection.close()

    def search(self, search_item):
        connection = DataBaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students WHERE name = %s", (search_item,))
        result = cursor.fetchall()

        connection.close()
        return result


class EdithDialog(QDialog):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        self.setWindowTitle("Update Student Data")
        self.setFixedSize(300, 300)

        layout = QVBoxLayout()

        index = self.main_window.table.currentRow()

        if index == -1:
            QMessageBox.warning(self, "Selection Error", "Please select a student to edit.")
            self.close()
            return

        student_name = self.main_window.table.item(index, 1).text()

        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        course_name = self.main_window.table.item(index, 2).text()
        self.course_name = QComboBox()
        self.course_name.addItems(["Biology", "Physics", "Astronomy", "Maths"])
        self.course_name.setCurrentText(course_name)
        layout.addWidget(self.course_name)

        mobile = self.main_window.table.item(index, 3).text()
        self.mobile = QLineEdit(mobile)
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        button = QPushButton("Update")
        button.clicked.connect(self.update_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def update_student(self):
        student_id = self.main_window.table.item(self.main_window.table.currentRow(), 0).text()

        if not self.student_name.text().strip() or not self.mobile.text().strip():
            QMessageBox.warning(self, "Input Error", "Please fill all fields.")
            return

        connection = DataBaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE students SET name = %s, course = %s, mobile = %s WHERE id = %s",
            (self.student_name.text().strip(),
             self.course_name.currentText(),
             self.mobile.text().strip(),
             student_id)
        )
        connection.commit()
        connection.close()

        self.main_window.load_data()
        QMessageBox.information(self, "Success", "Student record updated successfully!")
        self.close()


class DeleteDialog(QDialog):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        self.setWindowTitle("Delete Student Data")

        layout = QVBoxLayout()

        index = self.main_window.table.currentRow()

        if index == -1:
            QMessageBox.warning(self, "Selection Error", "Please select a student to delete.")
            self.close()
            return

        student_name = self.main_window.table.item(index, 1).text()

        confirmation = QMessageBox.question(self, "Confirm Deletion",
                                            f"Are you sure you want to delete student '{student_name}'?",
                                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if confirmation == QMessageBox.StandardButton.Yes:
            student_id = self.main_window.table.item(index, 0).text()

            connection = DataBaseConnection().connect()
            cursor = connection.cursor()
            cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
            connection.commit()
            connection.close()

            self.main_window.load_data()
            QMessageBox.information(self, "Success", "Student record deleted successfully!")
            self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    database = StudentDatabase()
    window = MainWindow(database)
    window.show()
    sys.exit(app.exec())
