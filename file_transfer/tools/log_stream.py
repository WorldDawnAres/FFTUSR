from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QTextCursor,QColor
from PySide6.QtWidgets import QTextEdit

class EmittingStream(QObject):
    text_written = Signal(str, str)

    def __init__(self, text_edit: QTextEdit):
        super().__init__()
        self.text_edit = text_edit
        self.text_written.connect(self.write_to_output)

    def write(self, text):
        text = text.rstrip()
        if not text:
            return
        
        if "GET /files" in text or "尝试下载文件" in text:
            style = "success"
        elif "文件不存在" in text or "404" in text or "下载文件时出错" in text:
            style = "error"
        elif "POST /upload" in text or "SHARED_FOLDER" in text or "TARGET_FOLDER" in text:
            style = "info1"
        elif "200" in text:
            style = "great"
        else:
            style = "info"

        self.text_written.emit(text, style)

    def write_to_output(self, text, style):
        color = {
            "info": QColor("orange"),
            "info1": QColor("purple"),
            "great": QColor("pink"),
            "error": QColor("red"),
            "success": QColor("green"),
        }.get(style, QColor("black"))

        self.text_edit.setTextColor(color)
        self.text_edit.append(text)
        self.text_edit.moveCursor(QTextCursor.End)

    def flush(self):
        pass
