from PyQt6.QtWidgets import QMainWindow, QGraphicsBlurEffect, QMessageBox, QTableView
from PyQt6.QtWidgets import (QMainWindow, QPushButton, QGraphicsOpacityEffect, QGraphicsDropShadowEffect,
                             QLabel, QProgressBar, QCompleter)
from PyQt6.QtCore import QPropertyAnimation, QTimer, QRect, QEasingCurve, QParallelAnimationGroup, QDate,QPoint, Qt
from AI import AIChatDialog
from PyQt6.uic import loadUi
from PyQt6.QtGui import QColor
from databaseconn import (add_staff, add_customer, add_orders, add_product, get_customer_names,
                          get_product_names, get_product_id_by_name, get_customer_id_by_name, get_staff_count,
                          get_order_count, get_product_count, get_customer_count)
from PyQt6.QtSql import QSqlDatabase, QSqlTableModel

class managerDashboard(QMainWindow):
    def __init__(self, parent=None, fullname=None):
        super().__init__(parent)
        loadUi('freshManagerDashboard.ui', self)

        self.orderDate.setDate(QDate.currentDate())
        customer_name = get_customer_names()
        autoComplete = QCompleter(customer_name)
        autoComplete.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.txtBoxCustomerfullName.setCompleter(autoComplete)

        product_names = get_product_names()
        self.comboBoxSelectProduct.addItems(product_names)
        self.txtBoxPaid.addItems(["Select payment status", "Paid", "Not Paid"])
        self.txtBoxGender.addItems(["Select gender", "Male","Female"])

        self.username.setText(fullname)

        self.load_staff()
        self.load_customers()
        self.load_product()
        self.load_orders()
        self.load_dashboard_data()

        self.button_geometries = {}
        self.button_animations = {}

        self.stretch_label_left(self.username)

        for btn in [self.customerBtn, self.staffBtn, self.dashboardBtn, self.ordersBtn, self.productsBtn,
                    self.logoutBtn, self.staffAddBtn, self.addCustomerWidget, self.StaffTile, self.ordersTile,
                    self.productsTile, self.customerTile, self.addCustomer, self.addProductBtn, self.addOrdersBtn,
                    self.customerTable, self.productView, self.orderView, self.staffView, self.addStaffField,
                    self.addOrdersWidget, self.addProductWidget, self.measurementWidget,
                    self.customerDetailsWidget, self.AIBtn, self.sidebar, self.profilePic]:
                    make_3d_button(btn)

        for button in [self.logoutBtn, self.dashboardBtn, self.staffBtn,self.customerBtn, self.ordersBtn,
                       self.productsBtn, self.addCustomer, self.addProductBtn, self.addOrdersBtn, self.staffAddBtn]:
            self.hover_animation(button)

        self.customerDelete.clicked.connect(
            lambda: self.delete_record(self.customerTable, self.customerModel, "customer")
        )
        self.deleteProductBtn.clicked.connect(
            lambda: self.delete_record(self.productView, self.productModel, "product")
        )
        self.deleteOrderBtn.clicked.connect(
            lambda: self.delete_record(self.orderView, self.orderModel, "order")
        )
        self.deleteStaffBtn.clicked.connect(
            lambda: self.delete_record(self.staffView, self.staffModel, "staff")
        )
        #         Click events

        self.dashboardBtn.clicked.connect(lambda: self.slide_page(5))
        self.customerBtn.clicked.connect(lambda: self.slide_page(0))
        self.staffBtn.clicked.connect(lambda: self.slide_page(4))
        self.ordersBtn.clicked.connect(lambda: self.slide_page(1))
        self.productsBtn.clicked.connect(lambda: self.slide_page(3))
        self.addCustomer.clicked.connect(lambda: self.slide_page(2))
        self.AIBtn.clicked.connect(self.open_ai_summary)
        self.AddStaffBtn.clicked.connect(self.handle_add_staff)
        self.saveCustomer.clicked.connect(self.handle_add_customer)
        self.BtnAddProduct.clicked.connect(self.handle_add_product)
        self.btnAddOrder.clicked.connect(self.handle_add_orders)
        self.logoutBtn.clicked.connect(self.log_out)
        self.searchCustomer.textChanged.connect(self.search_customer)

        self.staffAddBtn.clicked.connect(
            lambda:self.toggle_slide_widget(self.addStaffField)
        )
        self.addOrdersBtn.clicked.connect(
            lambda: self.toggle_slide_widget(self.addOrdersWidget)
        )
        self.addProductBtn.clicked.connect(
            lambda:self.toggle_slide_widget(self.addProductWidget)
        )

    # BUTTON FUNCTIONALITES
    def handle_add_staff(self):
        name = self.txtBoxFullName.text()
        contact = self.txtBoxStaffContact.text()
        payment_status = self.txtBoxPaid.currentText()

        if payment_status == "Select payment status":
            QMessageBox.warning(self, "Unfilled field","No payment status selected")
            return

        if not name or not contact or not payment_status:
            QMessageBox.warning(self , "Empty", "Fill all the fields")
            return

        if add_staff(name, contact, payment_status):
            QMessageBox.information(self, "Success", "Staff added successfully!")
            self.staffModel.select()
            self.load_dashboard_data()

    def handle_add_customer(self):
        fullname = self.fullName.text()
        address = self.txtBoxAddress.text()
        contact =  self.txtBoxCustomerContact.text()
        gender = self.txtBoxCustomerGender.text()

        if not fullname or not address or not contact or not gender:
            QMessageBox.warning(self,"empty","name,address,contact,gender should not be empty")
            return

        if add_customer(fullname, address, contact, gender):
            QMessageBox.information(self, "Success", "Customer added successfully")
            self.customerModel.select()
            self.load_dashboard_data()

    def handle_add_product(self):
        productName = self.txtBoxProductName.text()
        brand = self.txtBoxBrand.text()
        gender = self.txtBoxGender.currentText()
        price = self.txtBoxPrice.text()
        description = self.txtBoxDescription.text()

        if gender == "Select gender":
            QMessageBox.warning(self, "Unfilled field", "Select gender")

        if not productName or not brand or not gender or not price or not description:
            QMessageBox.warning(self, "Empty", "Fill all the fields")
            return

        if add_product(productName, description, brand, price, gender):
            QMessageBox.information(self ,"Success", "Product added successfully")
            self.productModel.select()
            self.load_dashboard_data()

    def handle_add_orders(self):
        customer_name = self.txtBoxCustomerfullName.text().strip()
        product_name = self.comboBoxSelectProduct.currentText()
        quantity = self.txtBoxQuantity.text().strip()
        date = self.orderDate.date().toString("yyyy-MM-dd")
        status = self.txtPaymentStatus.text().strip()

        if not customer_name or not product_name or not quantity or not date:
            QMessageBox.warning(self, "Input Error", "Quantity and Date are required.")
            return

        customer_id = get_customer_id_by_name(customer_name)
        product_id = get_product_id_by_name(product_name)

        if not customer_id or not product_id:
            QMessageBox.warning(self, "Input Error", "Customer or Product Name are required.")

        if add_orders(product_id, customer_id, quantity, date, status):
            QMessageBox.information(self, "Success", "Order added successfully.")
            self.orderModel.select()

            self.txtBoxQuantity.clear()
            self.txtPaymentStatus.clear()
            self.load_dashboard_data()

        else:
            QMessageBox.critical(self, "Error", "Failed to add order.")

    #TABLES
    def load_staff(self):

        if QSqlDatabase.contains("qt_sql_default_connection"):
            self.db = QSqlDatabase.database("qt_sql_default_connection")
        else:
            self.db = QSqlDatabase.addDatabase("QSQLITE")
            self.db.setDatabaseName("fashion.db")

        if not self.db.open():
            print("Database not open")
            return

        self.staffModel = QSqlTableModel(self, self.db)
        self.staffModel.setTable("staff")
        self.staffModel.select()

        self.staffView.setModel(self.staffModel)
        self.staffView.setAlternatingRowColors(True)
        self.staffView.verticalHeader().setVisible(False)
        self.staffView.setShowGrid(False)
        self.staffView.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)

    def load_product(self):
        if QSqlDatabase.contains("qt_sql_default_connection"):
            self.db = QSqlDatabase.database("qt_sql_default_connection")
        else:
            self.db = QSqlDatabase.addDatabase("QSQLITE")
            self.db.setDatabaseName("fashion.db")

        if not self.db.open():
            print("Database not open")
            return

        self.productModel = QSqlTableModel(self, self.db)
        self.productModel.setTable("products")
        self.productModel.select()

        self.productView.setModel(self.productModel)
        self.productView.setAlternatingRowColors(True)
        self.productView.verticalHeader().setVisible(False)
        self.productView.setShowGrid(False)
        self.productView.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)

    def load_customers(self):
        if QSqlDatabase.contains("qt_sql_default_connection"):
            self.db = QSqlDatabase.database("qt_sql_default_connection")
        else:
            self.db = QSqlDatabase.addDatabase("QSQLITE")
            self.db.setDatabaseName("fashion.db")

        if not self.db.open():
            print("Database not open")
            return

        self.customerModel = QSqlTableModel(self, self.db)
        self.customerModel.setTable("customer")
        self.customerModel.select()

        self.customerTable.setModel(self.customerModel)
        self.customerTable.setAlternatingRowColors(True)
        self.customerTable.verticalHeader().setVisible(False)
        self.customerTable.setShowGrid(False)
        self.customerTable.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)

    def load_orders(self):
        if QSqlDatabase.contains("qt_sql_default_connection"):
            self.db = QSqlDatabase.database("qt_sql_default_connection")
        else:
            self.db = QSqlDatabase.addDatabase("QSQLITE")
            self.db.setDatabaseName("fashion.db")
        if not self.db.open():
            print("Database not open")
            return

        self.orderModel = QSqlTableModel(self, self.db)
        self.orderModel.setTable("orders")
        self.orderModel.select()

        self.orderView.setModel(self.orderModel)
        self.orderView.setAlternatingRowColors(True)
        self.orderView.verticalHeader().setVisible(False)
        self.orderView.setShowGrid(False)
        self.orderView.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)

    # ANIMATIONS
    def open_ai_summary(self):
        self.ai_window = AIChatDialog(self, self.username.text())
        self.ai_window.show()

    def log_out(self):
         from login import Login

         self.login_window = Login()
         self.login_window.show()
         self.close()

    def slide_page(self, index):
        current_page = self.stackedWidget.currentWidget()
        next_page = self.stackedWidget.widget(index)

        w = self.stackedWidget.width()
        h = self.stackedWidget.height()

        next_page.setGeometry(w, 0, w, h)
        self.stackedWidget.setCurrentWidget(next_page)
        anim_old = QPropertyAnimation(current_page, b"pos")
        anim_old.setDuration(400)
        anim_old.setStartValue(QPoint(0, 0))
        anim_old.setEndValue(QPoint(-w, 0))
        anim_old.setEasingCurve(QEasingCurve.Type.InOutCubic)

        anim_new = QPropertyAnimation(next_page, b"pos")
        anim_new.setDuration(400)
        anim_new.setStartValue(QPoint(w, 0))
        anim_new.setEndValue(QPoint(0, 0))
        anim_new.setEasingCurve(QEasingCurve.Type.InOutCubic)

        self.anim_old = anim_old
        self.anim_new = anim_new

        anim_old.start()
        anim_new.start()

        if index == 0:
            self.lblTitle.setText("Customer")
        elif index == 1:
            self.lblTitle.setText("Order")
        elif index == 2:
            self.lblTitle.setText("Customer")
        elif index == 3:
            self.lblTitle.setText("Product")
        elif index == 4:
            self.lblTitle.setText("Staff")
        elif index == 5:
            self.lblTitle.setText("Dashboard")



    def hover_animation(self, button: QPushButton):
        button.installEventFilter(self)
        self.button_geometries[button] = None
        animation = QPropertyAnimation(button, b"geometry")
        animation.setDuration(200)
        self.button_animations[button] = animation

    def eventFilter(self, obj, event):
        if obj in self.button_animations:
            if event.type() == event.Type.Enter:
                if obj in [self.logoutBtn, self.searchCustomer]:
                    self.stretch_right(obj)
                else:
                    self.stretch_left(obj)
            elif event.type() == event.Type.Leave:
                if obj in [self.logoutBtn, self.searchCustomer]:
                    self.reset_button_right(obj)
                else:
                    self.reset_button(obj)
        return super().eventFilter(obj, event)

    def stretch_left(self, button: QPushButton):
        if self.button_geometries[button] is None:
            self.button_geometries[button] = button.geometry()

        animation = self.button_animations[button]
        animation.stop()
        animation.setStartValue(button.geometry())
        animation.setEndValue(QRect(
            button.geometry().x() - 20,
            button.geometry().y(),
            button.geometry().width() + 20,
            button.geometry().height()
        ))
        animation.start()

    def reset_button(self, button: QPushButton):
        if self.button_geometries[button] is not None:
            animation = self.button_animations[button]
            animation.stop()
            animation.setStartValue(button.geometry())
            animation.setEndValue(self.button_geometries[button])
            animation.start()

    def hover_animation_right(self, button: QPushButton):
        button.installEventFilter(self)
        self.button_geometries[button] = None
        animation = QPropertyAnimation(button, b"geometry")
        animation.setDuration(200)
        self.button_animations[button] = animation

    def stretch_right(self, button: QPushButton):
        if self.button_geometries[button] is None:
            self.button_geometries[button] = button.geometry()

        animation = self.button_animations[button]
        animation.stop()
        animation.setStartValue(button.geometry())
        animation.setEndValue(QRect(
            button.geometry().x(),
            button.geometry().y(),
            button.geometry().width() + 20,
            button.geometry().height()
        ))
        animation.start()

    def reset_button_right(self, button: QPushButton):
        if self.button_geometries[button] is not None:
            animation = self.button_animations[button]
            animation.stop()
            animation.setStartValue(button.geometry())
            animation.setEndValue(self.button_geometries[button])
            animation.start()

    def toggle_slide_widget(self, widget, duration=400):
        current_x = widget.x()

        visible_x = 200
        hidden_x = self.stackedWidget.width()
        y = widget.y()

        animation = QPropertyAnimation(widget, b"pos")
        animation.setDuration(duration)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        if current_x == visible_x:
            start_pos = QPoint(visible_x, y)
            end_pos = QPoint(hidden_x, y)
        else:
            start_pos = QPoint(hidden_x, y)
            end_pos = QPoint(visible_x, y)

        animation.setStartValue(start_pos)
        animation.setEndValue(end_pos)
        animation.start()

        self.current_animation = animation

    def stretch_label_left(self, label):
        orig_geom = label.geometry()

        font_metrics = label.fontMetrics()
        text_width = font_metrics.horizontalAdvance(label.text()) + 1

        new_geom = QRect(orig_geom.x() - (text_width - orig_geom.width()),
                         orig_geom.y(),
                         text_width,
                         orig_geom.height())

        animation = QPropertyAnimation(label, b"geometry")
        animation.setDuration(400)
        animation.setStartValue(orig_geom)
        animation.setEndValue(new_geom)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.start()

        self.label_animation = animation

    # adding count to cards
    def load_dashboard_data(self):
        staffCount = get_staff_count()
        customerCount = get_customer_count()
        orderCount = get_order_count()
        productCount = get_product_count()
        self.staffCount.setText(str(staffCount))
        self.customerCount.setText(str(customerCount))
        self.orderCount.setText(str(orderCount))
        self.productCount.setText(str(productCount))

#     customer Search Logic
    def search_customer(self):
        text = self.searchCustomer.text().strip()

        if text == "":
            self.customerModel.setFilter("")
        else:
            self.customerModel.setFilter(f"customer_fullname LIKE '%{text}%'")

        self.customerModel.select()

    def delete_record(self, table, model, item_name="record"):
        selected = table.selectionModel().currentIndex()

        if not selected.isValid():
            QMessageBox.warning(self, "No Selection", f"Please select a {item_name} to delete.")
            return

        row = selected.row()

        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete this {item_name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            model.removeRow(row)
            model.submitAll()
            model.select()

            self.load_dashboard_data()
            QMessageBox.information(self, "Deleted", f"{item_name.capitalize()} deleted successfully.")

def make_3d_button(button):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(10)
    shadow.setXOffset(2)
    shadow.setYOffset(2)
    shadow.setColor(QColor(0, 0, 0, 200))
    button.setGraphicsEffect(shadow)
