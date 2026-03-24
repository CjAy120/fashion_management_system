import webbrowser
import time
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QHBoxLayout
)
from PyQt6.QtCore import QTimer
import sqlite3

class AIChatDialog(QDialog):
    def __init__(self, parent=None, fullname=None):
        super().__init__(parent)
        self.fullname = fullname

        self.setWindowTitle("Smart Fashion Assistant")
        self.setFixedSize(500, 500)

        self.setStyleSheet("""
        QDialog { background-color: #222267; color: white; }
        QTextEdit { background-color: #5b5ba4; border-radius: 8px; padding: 10px; color: white; }
        QLineEdit { padding: 6px; border-radius: 6px; color: black; }
        QPushButton { background-color: #4CAF50; color: white; padding: 6px; border-radius: 6px; }
        QPushButton:hover { background-color: #45a049; }
        """)

        # Layouts
        layout = QVBoxLayout()
        self.chatBox = QTextEdit()
        self.chatBox.setReadOnly(True)

        self.inputField = QLineEdit()
        self.inputField.setPlaceholderText("Ask something about your products...")

        self.sendBtn = QPushButton("Ask")
        self.sendBtn.clicked.connect(self.handle_question)

        # Quick-reply buttons
        quick_layout = QHBoxLayout()
        self.quick_buttons = []
        for text in ["Total Products", "List Products", "Total Customers", "List Customers"]:
            btn = QPushButton(text)
            btn.clicked.connect(lambda _, t=text: self.inputField.setText(t) or self.handle_question())
            self.quick_buttons.append(btn)
            quick_layout.addWidget(btn)

        # Add widgets to layout
        layout.addWidget(self.chatBox)
        layout.addLayout(quick_layout)
        layout.addWidget(self.inputField)
        layout.addWidget(self.sendBtn)
        self.setLayout(layout)

        self.chatBox.append(f"<b>AI:</b> Hello, {self.fullname}! How can I help you today?")

    def handle_question(self):
        question = self.inputField.text().strip()
        if not question:
            return

        self.chatBox.append(f"<b>You:</b> {question}")
        self.inputField.clear()
        self.chatBox.append("<i>AI is thinking...</i>")
        self.chatBox.verticalScrollBar().setValue(self.chatBox.verticalScrollBar().maximum())

        # Delay response to simulate thinking (1–1.5 sec)
        QTimer.singleShot(1200, lambda: self.process_response(question))

    def process_response(self, question):
        # Remove last "thinking" line
        cursor = self.chatBox.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.select(cursor.SelectionType.BlockUnderCursor)
        cursor.removeSelectedText()
        cursor.deletePreviousChar()

        # Process offline
        answer = self.process_offline(question)
        if answer:
            self.chatBox.append(f"<b>AI:</b> {answer}")
        # Online queries
        elif "trending" in question.lower():
            self.chatBox.append("<b>AI:</b> Fetching trending fashion designs...")
            self.open_trending_fashion_designs()
        else:
            self.chatBox.append("<b>AI:</b> Sorry, I don’t understand that question yet.")

        # Auto-scroll
        self.chatBox.verticalScrollBar().setValue(self.chatBox.verticalScrollBar().maximum())

    def process_offline(self, question):
        question = question.lower()
        conn = sqlite3.connect("fashion.db")
        cursor = conn.cursor()
        try:
            if "hello" in question or "hi" in question:
                return f"Hello, {self.fullname}! How can I help you today?"

            elif "total product" in question:
                cursor.execute("SELECT COUNT(*) FROM products")
                total = cursor.fetchone()[0]
                return f"You have {total} products in your system."

            elif "most expensive" in question:
                cursor.execute("""
                    SELECT product_name, product_price
                    FROM products
                    ORDER BY CAST(product_price AS REAL) DESC
                    LIMIT 1
                """)
                result = cursor.fetchone()
                if result:
                    return f"The most expensive product is {result[0]} costing GHS {result[1]}."
                return "No products found."

            elif "list" in question and "product" in question:
                cursor.execute("SELECT product_name, brand, product_price FROM products")
                results = cursor.fetchall()
                if results:
                    items = "\n".join([f"- {r[0]} ({r[1]}) - GHS {r[2]}" for r in results])
                    return f"Here are your products:\n{items}"
                return "No products available."

            elif "total customer" in question:
                cursor.execute("SELECT COUNT(*) FROM customers")
                total = cursor.fetchone()[0]
                return f"You have {total} registered customers."

            elif "list customer" in question:
                cursor.execute("SELECT customer_fullname, contact FROM customers")
                results = cursor.fetchall()
                if results:
                    names = "\n".join([f"- {r[0]} ({r[1]})" for r in results])
                    return f"Your customers:\n{names}"
                return "No customers found."

            elif "measurement" in question:
                name = question.lower().replace("measurement", "").replace("measurements", "").replace("'s", "").strip()
                cursor.execute("""
                    SELECT top_length, around_arm, wrist, waist, sleeve, thighs, seat, trouser_length
                    FROM customers
                    WHERE customer_fullname LIKE ?
                """, ('%' + name + '%',))
                result = cursor.fetchone()
                if result:
                    return (f"Measurements:\nTop Length: {result[0]}\nAround Arm: {result[1]}\n"
                            f"Wrist: {result[2]}\nWaist: {result[3]}\nSleeve: {result[4]}\n"
                            f"Thighs: {result[5]}\nSeat: {result[6]}\nTrouser Length: {result[7]}")
                return "Customer not found."

            elif "total staff" in question:
                cursor.execute("SELECT COUNT(*) FROM staff")
                total = cursor.fetchone()[0]
                return f"You have {total} staff members."

            elif "list staff" in question:
                cursor.execute("SELECT staff_fullname, payment_status FROM staff")
                results = cursor.fetchall()
                if results:
                    staff_list = "\n".join([f"- {r[0]} (Payment: {r[1]})" for r in results])
                    return f"Your staff:\n{staff_list}"
                return "No staff found."

            return None
        except Exception as e:
            return f"Database Error: {str(e)}"
        finally:
            conn.close()

    def open_trending_fashion_designs(self):
        search_url = "https://www.pinterest.com/search/pins/?q=ghana%20fashion"
        webbrowser.open(search_url)