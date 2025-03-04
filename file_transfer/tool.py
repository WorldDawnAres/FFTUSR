from file_transfer import config,file_utils,server
from tkinter import filedialog
import psutil,webbrowser,platform,subprocess,threading
from gevent.pywsgi import WSGIServer
from gevent import socket

flask_server_process = None
selected_ip = None

def update_global_folders():
    global SHARED_FOLDER, TARGET_FOLDER
    SHARED_FOLDER = config.config_manager.get_shared_folder()
    TARGET_FOLDER = config.config_manager.get_target_folder()

def select_shared_folder():
    shared_folder = filedialog.askdirectory(title="选择共享文件夹")
    if shared_folder:
        config.config_manager.update_shared_folder(shared_folder)
    update_global_folders()
    file_utils.update_display(f"选择的共享文件夹路径：{SHARED_FOLDER}")
    print(f"选择的共享文件夹路径：{SHARED_FOLDER}")

def select_target_folder():
    target_folder = filedialog.askdirectory(title="选择上传文件夹")
    if target_folder:
        config.config_manager.update_target_folder(target_folder)
    update_global_folders()
    file_utils.update_display(f"选择的上传文件夹路径：{TARGET_FOLDER}")
    print(f"选择的上传文件夹路径：{TARGET_FOLDER}")

def get_network_interfaces():
    interfaces = []
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET:
                interfaces.append((interface, addr.address))
    return interfaces

def on_interface_select(interface_listbox, event):
    global selected_ip
    selection = interface_listbox.curselection()
    if selection:
        selected_ip = interface_listbox.get(selection[0])
        file_utils.update_display(f"已选择网络接口: {selected_ip}")
    else:
        selected_ip = None

def stop_flask_server():
    global flask_server_process
    
    if flask_server_process is not None:
        file_utils.update_display("服务器正在运行，正在关闭...")
        try:
            flask_server_process.stop()
            file_utils.update_display("服务器已关闭")
        except Exception as e:
            file_utils.update_display(f"关闭服务器时出错: {e}")
        flask_server_process = None
    else:
        file_utils.update_display("没有运行中的服务器。")

def start_server(port_entry):
    global flask_thread,selected_ip
    try:
        new_port = int(port_entry.get())
        if new_port < 1024 or new_port > 65535:
            file_utils.update_display("端口号无效，请输入有效的端口号（范围：1024-65535）", "red")
            return
    except ValueError:
        file_utils.update_display("端口号格式错误，请输入一个数字", "red")
        return

    global PORT
    PORT = new_port

    if not selected_ip:
        selected_ip = get_local_ip()
    
    update_global_folders()
    '''shared_folder = config.config_manager.get_shared_folder()
    target_folder = config.config_manager.get_target_folder()

    file_utils.update_display(f"启动服务器前的 SHARED_FOLDER: {shared_folder}")
    print(f"启动服务器前的 SHARED_FOLDER: {shared_folder}")
    file_utils.update_display(f"启动服务器前的 TARGET_FOLDER: {target_folder}")
    print(f"启动服务器前的 TARGET_FOLDER: {target_folder}")'''

    ip_address = selected_ip.split(" - ")[-1].lstrip()

    global flask_server_process
    if flask_server_process is not None:
        file_utils.update_display("服务器正在运行，正在关闭...")
        try:
            flask_server_process.stop()
            file_utils.update_display("服务器已关闭")
        except Exception as e:
            file_utils.update_display(f"关闭服务器时出错: {e}")
        flask_server_process = None
    else:
        file_utils.update_display("没有运行中的服务器。")

    flask_thread = threading.Thread(target=run_flask_server, args=(ip_address,))
    flask_thread.daemon = True
    flask_thread.start()

    #打开防火墙端口
    #file_utils.open_firewall_port()

    if config.cert_file is None or config.key_file is None:
        server_url = f'http://{ip_address}:{PORT}/files'
    else:
        server_url = f'https://{ip_address}:{PORT}/files'

    webbrowser.open(server_url)

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        s.connect(('10.254.254.254', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = None
    finally:
        s.close()

    if ip is None:
        if platform.system() == "Windows":
            result = subprocess.run("ipconfig", capture_output=True, text=True, shell=True)
            adapter_name = "WLAN"
        else:
            result = subprocess.run("ifconfig", capture_output=True, text=True, shell=True)
            adapter_name = "wlan"

        ip_address = None
        found_wifi = False
        for line in result.stdout.splitlines():
            if adapter_name in line: 
                found_wifi = True
            elif found_wifi and ("inet " in line or "IPv4 地址" in line):
                ip_address = line.split()[-1]
                break

        ip = ip_address if ip_address else None

    return ip

def run_flask_server(ip_address):
    global flask_server_process
    local_ip = get_local_ip()
    if local_ip:
        file_utils.update_display(f"服务器可用的本地 IP 地址: {local_ip}")
    else:
        file_utils.update_display(f"无法获取本地 IP 地址")

    if config.cert_file is None or config.key_file is None:
        file_utils.update_display(f"访问 http://{ip_address}:{PORT}/files 查看文件列表")
        flask_server_process = WSGIServer((ip_address, PORT), server.app)
    else:
        file_utils.update_display(f"访问 https://{ip_address}:{PORT}/files 查看文件列表")
        flask_server_process = WSGIServer((ip_address, PORT), server.app, keyfile=config.key_file, certfile=config.cert_file)
    flask_server_process.serve_forever()