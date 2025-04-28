from PySide6.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QStyleFactory, QLabel, QComboBox,
    QDialogButtonBox, QDialog, QVBoxLayout, QWidget, QInputDialog
)
from PySide6.QtGui import QIcon,QAction,QPalette, QColor
from file_transfer.LogWidget import LogWidget
from file_transfer.config import image
from file_transfer import tool

flask_thread = None

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("文件传输工具")
        self.resize(700, 500)
        self.set_dark_mode()

        self.setWindowIcon(QIcon(image))

        self.interface_frame = tool.get_local_ip()
        self.port_entry = 12345
        self.init_ui()
        self.create_menu()
    
    def init_ui(self):
        layout = QVBoxLayout()

        self.interface_frame = QLabel(f"当前指定网络接口ip：{self.interface_frame}")
        layout.addWidget(self.interface_frame)

        self.port_label = QLabel(f"当前指定端口号：{self.port_entry}")
        layout.addWidget(self.port_label)

        self.log_widget = LogWidget()
        layout.addWidget(self.log_widget)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def create_menu(self):
        menubar = self.menuBar()

        select_menu= menubar.addMenu("文件夹")

        select_folder = QAction("选择共享文件夹", self)
        select_folder.triggered.connect(lambda: tool.select_shared_folder(self))
        select_menu.addAction(select_folder)

        select_folder1 = QAction("选择上传文件夹", self)
        select_folder1.triggered.connect(lambda: tool.select_target_folder(self))
        select_menu.addAction(select_folder1)

        server_menu = menubar.addMenu("服务器")

        interface_frame_action = QAction("选择接口", self)
        interface_frame_action.triggered.connect(self.select_interface)
        server_menu.addAction(interface_frame_action)

        select_port_action = QAction("选择端口号", self)
        select_port_action.triggered.connect(self.select_port)
        server_menu.addAction(select_port_action)

        server_start = QAction("启动服务器", self)
        server_start.triggered.connect(lambda: tool.start_server(self.port_entry))
        server_menu.addAction(server_start)

        exit_server = QAction("停止服务器", self)
        exit_server.triggered.connect(lambda: tool.stop_flask_server())
        server_menu.addAction(exit_server)

        theme_menu = menubar.addMenu("主题")

        light_action = QAction("浅色模式", self)
        light_action.triggered.connect(self.set_light_mode)
        theme_menu.addAction(light_action)

        dark_action = QAction("深色模式", self)
        dark_action.triggered.connect(self.set_dark_mode)
        theme_menu.addAction(dark_action)

        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        menubar.addAction(about_action)
    
    def set_dark_mode(self):
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Base, QColor(35, 35, 35))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Text, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))

        QApplication.instance().setPalette(dark_palette)
        QApplication.instance().setStyle(QStyleFactory.create("Fusion"))

    def set_light_mode(self):
        light_palette = QPalette()
        light_palette.setColor(QPalette.Window, QColor(240, 240, 240))
        light_palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
        light_palette.setColor(QPalette.Base, QColor(255, 255, 255))
        light_palette.setColor(QPalette.AlternateBase, QColor(240, 240, 240))
        light_palette.setColor(QPalette.ToolTipBase, QColor(0, 0, 0))
        light_palette.setColor(QPalette.ToolTipText, QColor(0, 0, 0))
        light_palette.setColor(QPalette.Text, QColor(0, 0, 0))
        light_palette.setColor(QPalette.Button, QColor(240, 240, 240))
        light_palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))
        light_palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        light_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        light_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        light_palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))

        app = QApplication.instance()
        app.setPalette(light_palette)
        app.setStyle(QStyleFactory.create("Fusion"))
    
    def select_interface(self):
        dialog = InterfaceSelectorDialog(self)
        dialog.exec()
        if dialog.selected_interface:
            self.update_interface_label(dialog.selected_interface)
    
    def update_interface_label(self, selected_interface):
        self.interface_frame.setText(f"当前指定网络接口：{selected_interface}")
    
    def select_port(self):
        port, ok = QInputDialog.getInt(self, "设置端口", "请输入端口号：", self.port_entry, 0, 65535)
        if ok:
            self.port_entry = port
            self.update_port_label()

    def update_port_label(self):
        self.port_label.setText(f"当前指定端口号：{self.port_entry}")
        print(f"当前指定端口号：{self.port_entry}")

    def show_about(self):
        QMessageBox.about(
            self,
            "关于",
            "本程序为之前版本的移植版\n\n"
            "支持老版本所有功能(自定义选择文件夹，自定义端口，自定义网络接口等)\n\n"
            "版本：v1.1\n\n"
            )

class InterfaceSelectorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择网络接口")

        interfaces = tool.get_network_interfaces()
        if not interfaces:
            self.show_no_interfaces_message()
            return
        
        interface_names = [f"{iface[0]} - {iface[1]}" for iface in interfaces]

        layout = QVBoxLayout(self)

        label = QLabel("请选择网络接口：", self)
        layout.addWidget(label)

        self.interface_combobox = QComboBox(self)
        self.interface_combobox.addItems(interface_names)
        layout.addWidget(self.interface_combobox)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

        self.selected_interface = None

    def accept(self):
        selected_interface = self.interface_combobox.currentText()
        tool.on_interface_select(selected_interface)
        self.selected_interface = selected_interface
        super().accept()

    def reject(self):
        super().reject()

    def show_no_interfaces_message(self):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("错误")
        msg.setText("没有找到可用的网络接口。")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()
        self.close()
