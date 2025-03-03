import re,subprocess
from file_transfer import ui,config
import tkinter as tk

def update_display(message, log_type="info"):
    if re.search(r'GET /files', message):
        log_type = "info1"
    elif re.search(r'200', message):
        log_type = "great"
    elif re.search(r'404', message):
        log_type = "error"
    elif re.search(r'POST /upload', message):
        log_type = "info2"
    elif re.search(r'文件不存在', message):
        log_type = "error"
    elif re.search(r'尝试下载文件', message):
        log_type = "info1"
    elif re.search(r'下载文件时出错', message):
        log_type = "error"
    elif re.search(r'SHARED_FOLDER', message):
        log_type = "info2"
    elif re.search(r'TARGET_FOLDER', message):
        log_type = "info2"
    elif re.search(r'Item added', message):
        log_type = "info"

    ui.log_text.insert(tk.END, message + '\n', log_type)
    ui.log_text.yview(tk.END)

def open_firewall_port():
    port = config.PORT
    try:
        subprocess.run(
            ["netsh", "advfirewall", "firewall", "add", "rule", "name=FileTransfer", "dir=in", "action=allow", "protocol=TCP", "localport=" + str(port)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        update_display(f"已开放端口 {port} 到 Windows 防火墙")
    except subprocess.CalledProcessError as e:
        update_display(f"打开端口时出错: {e}")

def close_firewall_port():
    port = config.PORT
    try:
        subprocess.run(
            ["netsh", "advfirewall", "firewall", "delete", "rule", "name=FileTransfer"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        update_display(f"已关闭端口 {port} 在 Windows 防火墙")
    except subprocess.CalledProcessError as e:
        update_display(f"关闭端口时出错: {e}")