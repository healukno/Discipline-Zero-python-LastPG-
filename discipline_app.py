import sys
import json
from datetime import datetime
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget, QLineEdit, 
                             QDateTimeEdit, QComboBox, QMessageBox, QHBoxLayout)
from PyQt5.QtGui import QFont
import matplotlib.pyplot as plt
import os

class ProductivityApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("DisciplineZero")
        self.setGeometry(100, 100, 500, 600)

        # Task list
        self.tasks = []

        # Layout setup
        self.layout = QVBoxLayout()

        # Task Manager UI
        self.task_list = QListWidget()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Enter a new task")
        self.task_date = QDateTimeEdit(datetime.now())
        self.task_date.setCalendarPopup(True)
        self.task_category = QComboBox()
        self.task_category.addItems(["Work", "Personal", "Errands"])
        self.add_task_button = QPushButton("Add Task")
        self.add_task_button.clicked.connect(self.add_task)
        
        # Button to remove selected task
        self.remove_task_button = QPushButton("Remove Selected Task")
        self.remove_task_button.clicked.connect(self.remove_task)
        
        # Button to finish selected task
        self.finish_task_button = QPushButton("Finish Selected Task")
        self.finish_task_button.clicked.connect(self.finish_task)

        # Pomodoro Timer UI
        self.timer_label = QLabel("Pomodoro Timer")
        self.timer_label.setFont(QFont("Arial", 16))
        self.timer_display = QLabel("25:00")
        self.timer_display.setFont(QFont("Arial", 24))
        self.start_timer_button = QPushButton("Start Timer")
        self.start_timer_button.clicked.connect(self.start_timer)

        # Button to stop timer
        self.stop_timer_button = QPushButton("Stop Timer")
        self.stop_timer_button.clicked.connect(self.stop_timer)

        # Productivity Reports Button
        self.show_report_button = QPushButton("Show Productivity Report")
        self.show_report_button.clicked.connect(self.show_report)

        # Add Widgets to Layout
        self.layout.addWidget(QLabel("Task Manager"))
        self.layout.addWidget(self.task_list)
        self.layout.addWidget(self.task_input)
        self.layout.addWidget(self.task_date)
        self.layout.addWidget(self.task_category)
        self.layout.addWidget(self.add_task_button)
        self.layout.addWidget(self.remove_task_button)
        self.layout.addWidget(self.finish_task_button)
        self.layout.addWidget(self.timer_label)
        self.layout.addWidget(self.timer_display)
        self.layout.addWidget(self.start_timer_button)
        self.layout.addWidget(self.stop_timer_button)
        self.layout.addWidget(self.show_report_button)

        self.setLayout(self.layout)

        # Timer setup
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.pomodoro_duration = 25 * 60  # 25 minutes
        self.break_duration = 5 * 60  # 5 minutes
        self.long_break_duration = 15 * 60  # 15 minutes
        self.timer_seconds = self.pomodoro_duration
        self.on_break = False

        # Load saved data if available
        self.load_data()

    def add_task(self):
        """Add a new task to the task list."""
        task_text = self.task_input.text()
        task_due = self.task_date.dateTime().toPyDateTime()
        task_category = self.task_category.currentText()
        if task_text:
            self.tasks.append({"task": task_text, "due": task_due.strftime('%Y-%m-%d %H:%M:%S'), "category": task_category, "completed": False})
            self.task_list.addItem(f"{task_text} - Due: {task_due} - Category: {task_category}")
            self.task_input.clear()
            self.save_data()  # Save data every time a new task is added

    def remove_task(self):
        """Remove the selected task from the task list."""
        selected_item = self.task_list.currentItem()
        if selected_item:
            row = self.task_list.row(selected_item)
            del self.tasks[row]
            self.task_list.takeItem(row)
            self.save_data()  # Save data after removing a task

    def finish_task(self):
        """Mark the selected task as completed."""
        selected_item = self.task_list.currentItem()
        if selected_item:
            row = self.task_list.row(selected_item)
            self.tasks[row]['completed'] = True
            self.task_list.takeItem(row)
            self.save_data()  # Save data after finishing a task

    def start_timer(self):
        """Start the Pomodoro timer."""
        self.timer.start(1000)  # Timer updates every 1 second

    def stop_timer(self):
        """Stop the Pomodoro timer."""
        self.timer.stop()

    def update_timer(self):
        """Update the timer display."""
        if self.timer_seconds > 0:
            self.timer_seconds -= 1
            minutes = self.timer_seconds // 60
            seconds = self.timer_seconds % 60
            self.timer_display.setText(f"{minutes:02d}:{seconds:02d}")
        else:
            self.timer.stop()
            if not self.on_break:
                self.on_break = True
                self.timer_seconds = self.break_duration
                QMessageBox.information(self, "Break Time", "Take a short break!")
            else:
                self.on_break = False
                self.timer_seconds = self.pomodoro_duration
                QMessageBox.information(self, "Work Time", "Back to work!")
            self.save_data()  # Save data after each Pomodoro cycle

    def show_report(self):
        """Show productivity report with a simple bar chart."""
        total_tasks = len(self.tasks)
        completed_tasks = len([task for task in self.tasks if task["completed"]])
        pomodoros_completed = completed_tasks * 2 

        fig, ax = plt.subplots()
        ax.bar(["Tasks Completed", "Pomodoros Completed"], [completed_tasks, pomodoros_completed])
        ax.set_ylabel("Count")
        ax.set_title("Productivity Report")
        plt.show()

    def save_data(self):
        """Save the current state of the application to a JSON file."""
        data = {
            "tasks": self.tasks,
            "timer_seconds": self.timer_seconds,
            "on_break": self.on_break
        }
        with open("app_data.json", "w") as f:
            json.dump(data, f)

    def load_data(self):
        """Load the saved state of the application from a JSON file."""
        if os.path.exists("app_data.json"):
            with open("app_data.json", "r") as f:
                data = json.load(f)
                self.tasks = data.get("tasks", [])
                self.timer_seconds = data.get("timer_seconds", self.pomodoro_duration)
                self.on_break = data.get("on_break", False)

                # Populate the task list
                for task in self.tasks:
                    due = datetime.strptime(task["due"], '%Y-%m-%d %H:%M:%S')
                    status = "Completed" if task["completed"] else "Pending"
                    self.task_list.addItem(f"{task['task']} - Due: {due} - Category: {task['category']} - Status: {status}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProductivityApp()
    window.show()
    sys.exit(app.exec_())
