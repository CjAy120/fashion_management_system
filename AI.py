import webbrowser
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QLineEdit, QPushButton
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

        layout = QVBoxLayout()
        self.chatBox = QTextEdit()
        self.chatBox.setReadOnly(True)
        self.inputField = QLineEdit()
        self.inputField.setPlaceholderText("Ask something about your products...")
        self.sendBtn = QPushButton("Ask")
        self.sendBtn.clicked.connect(self.handle_question)

        layout.addWidget(self.chatBox)
        layout.addWidget(self.inputField)
        layout.addWidget(self.sendBtn)
        self.setLayout(layout)

        self.chatBox.append(f"Hello, {self.fullname}! How can I help you today.")

    def handle_question(self):
        question = self.inputField.text().strip()
        if not question:
            return

        self.chatBox.append(f"\nYou: {question}")
        self.inputField.clear()

        # offline requests
        answer = self.process_offline(question)
        if answer:
            self.chatBox.append(f"AI: {answer}")
            return

        # online requests
        if "trending fashion designs" in question.lower() or "trending designs" in question.lower():
            self.chatBox.append("AI is fetching trending fashion designs...")
            self.open_trending_fashion_designs()
        else:
            self.chatBox.append("AI: Sorry, I don’t understand that question yet.")

    def process_offline(self, question):
        question = question.lower()
        conn = sqlite3.connect("fashion.db")
        cursor = conn.cursor()

        try:
            # Greeting
            if "hello" in question or "hi" in question:
                return f"Hello, {self.fullname}! How can I help you today?"

            # Products Intelligence
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

            elif "list" and "product" in question:
                cursor.execute("SELECT product_name, brand, product_price FROM products")
                results = cursor.fetchall()
                if results:
                    items = "\n".join(
                        [f"- {r[0]} ({r[1]}) - GHS {r[2]}" for r in results]
                    )
                    return f"Here are your products:\n{items}"
                return "No products available."

            # Customer questions
            elif "total customer" in question:
                cursor.execute("SELECT COUNT(*) FROM customer")
                total = cursor.fetchone()[0]
                return f"You have {total} registered customers."

            elif "list customer" in question:
                cursor.execute("SELECT customer_fullname, contact FROM customer")
                results = cursor.fetchall()
                if results:
                    names = "\n".join(
                        [f"- {r[0]} ({r[1]})" for r in results]
                    )
                    return f"Your customers:\n{names}"
                return "No customers found."

            elif "measurement" in question:
                # Example: "show measurement for John"
                words = question.split()
                name = words[-1]  # basic version (can improve later)

                cursor.execute("""
                    SELECT chest, waist, sleeve, trouser_length
                    FROM customer
                    WHERE customer_fullname LIKE ?
                """, ('%' + name + '%',))

                result = cursor.fetchone()
                if result:
                    return (f"Measurements:\n"
                            f"Chest: {result[0]}\n"
                            f"Waist: {result[1]}\n"
                            f"Sleeve: {result[2]}\n"
                            f"Trouser Length: {result[3]}")
                return "Customer not found."


            # Staff questions
            elif "total staff" in question:
                cursor.execute("SELECT COUNT(*) FROM staff")
                total = cursor.fetchone()[0]
                return f"You have {total} staff members."

            elif "list staff" in question:
                cursor.execute("SELECT staff_fullname, payment_status FROM staff")
                results = cursor.fetchall()
                if results:
                    staff_list = "\n".join(
                        [f"- {r[0]} (Payment: {r[1]})" for r in results]
                    )
                    return f"Your staff:\n{staff_list}"
                return "No staff found."

            return None

        except Exception as e:
            return f"Database Error: {str(e)}"

        finally:
            conn.close()

    def open_trending_fashion_designs(self):
        # Open browser with search query for trending Ghanaian fashion designs on Pixabay
        search_url = "https://www.pinterest.com/search/pins/?q=ghana%20fashion"
        webbrowser.open(search_url)