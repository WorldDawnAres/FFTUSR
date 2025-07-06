from PySide6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QWidget, QMessageBox, QFileDialog, QApplication
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from file_transfer.tools import tool
from file_transfer.tools.config import image

class QRCodeWindow(QMainWindow):
    def __init__(self, parent=None, ip_address=None, port=None):
        super().__init__(parent)
        self.setWindowTitle("访问二维码")
        self.setWindowIcon(QIcon(image))
        self.resize(310, 400)
        
        if parent:
            self.setPalette(parent.palette())
        
        self.ip_address = ip_address
        self.port = port
        self.qr_pixmap = None
        self.server_url = ""
        
        self.init_ui()
        self.generate_qr_code()
    
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        self.qr_label = QLabel("正在生成二维码...")
        self.qr_label.setAlignment(Qt.AlignCenter)
        self.qr_label.setMinimumHeight(280)
        self.qr_label.setStyleSheet("border: 2px solid #ddd; margin: 10px; padding: 10px; border-radius: 8px; background-color: white;")
        layout.addWidget(self.qr_label)
        
        self.url_label = QLabel("")
        self.url_label.setAlignment(Qt.AlignCenter)
        self.url_label.setStyleSheet("font-size: 11px; color: #666; margin: 8px; padding: 5px; word-wrap: break-word;")
        self.url_label.setWordWrap(True)
        layout.addWidget(self.url_label)
        
        self.status_label = QLabel("就绪")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 10px; color: #888; margin: 5px;")
        layout.addWidget(self.status_label)
        
        button_layout = QHBoxLayout()
        
        save_button = QPushButton("保存二维码")
        save_button.setStyleSheet("padding: 8px 15px; font-size: 12px;")
        save_button.clicked.connect(self.save_qr_code)
        button_layout.addWidget(save_button)
        
        copy_button = QPushButton("复制链接")
        copy_button.setStyleSheet("padding: 8px 15px; font-size: 12px;")
        copy_button.clicked.connect(self.copy_url)
        button_layout.addWidget(copy_button)
        
        layout.addLayout(button_layout)
        
        central_widget.setLayout(layout)
    
    def generate_qr_code(self):
        try:
            self.status_label.setText("正在生成二维码...")
            
            ip_address = self.extract_ip_address(self.ip_address)
            
            qr_pixmap, server_url = tool.generate_qr_code(ip_address, self.port)
            
            if qr_pixmap and server_url:
                scaled_pixmap = qr_pixmap.scaled(250, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.qr_label.setPixmap(scaled_pixmap)
                self.qr_label.setText("")
                
                self.qr_pixmap = qr_pixmap
                self.server_url = server_url
                
                self.url_label.setText(f"访问地址:\n{server_url}")
                self.status_label.setText("二维码生成成功")
            else:
                self.qr_label.setText("二维码生成失败\n请检查网络配置或安装qrcode库")
                self.url_label.setText("")
                self.status_label.setText("生成失败")
                
        except Exception as e:
            print(f"生成二维码时出错: {e}")
            self.qr_label.setText(f"生成二维码失败:\n{str(e)}")
            self.url_label.setText("")
            self.status_label.setText("出现错误")

    def extract_ip_address(self, ip_info):
        try:
            if " - " in ip_info:
                ip_part = ip_info.split(" - ")[-1].strip()
            elif "：" in ip_info:
                ip_part = ip_info.split("：")[-1].strip()
            elif ":" in ip_info:
                ip_part = ip_info.split(":")[-1].strip()
            else:
                ip_part = ip_info.strip()
            
            parts = ip_part.split('.')
            if len(parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in parts):
                return ip_part
            else:
                return tool.get_local_ip()
                
        except Exception as e:
            print(f"提取IP地址时出错: {e}")
            return tool.get_local_ip()

    def save_qr_code(self):
        if self.qr_pixmap:
            try:
                clean_ip = self.extract_ip_address(self.ip_address).replace(".", "_")
                file_path, _ = QFileDialog.getSaveFileName(
                    self, 
                    "保存二维码", 
                    f"qr_code_{clean_ip}_{self.port}.png", 
                    "PNG files (*.png);;JPG files (*.jpg);;All files (*.*)"
                )
                if file_path:
                    self.qr_pixmap.save(file_path)
                    QMessageBox.information(self, "保存成功", f"二维码已保存到:\n{file_path}")
                    self.status_label.setText("二维码已保存")
            except Exception as e:
                QMessageBox.warning(self, "保存失败", f"保存二维码时出错:\n{str(e)}")
                self.status_label.setText("保存失败")
        else:
            QMessageBox.warning(self, "无法保存", "没有可保存的二维码，请先生成二维码")

    def copy_url(self):
        if self.server_url:
            try:
                clipboard = QApplication.clipboard()
                clipboard.setText(self.server_url)
                QMessageBox.information(self, "复制成功", f"访问链接已复制到剪贴板:\n{self.server_url}")
                self.status_label.setText("链接已复制")
            except Exception as e:
                QMessageBox.warning(self, "复制失败", f"复制链接时出错:\n{str(e)}")
        else:
            QMessageBox.warning(self, "无法复制", "没有可复制的链接")
    
    def update_server_info(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port
        self.generate_qr_code()
    
    def closeEvent(self, event):
        event.accept()
