from file_transfer import config,server
from PySide6.QtWidgets import QFileDialog
import psutil,webbrowser,platform,subprocess,threading
from gevent.pywsgi import WSGIServer
from gevent import socket

flask_server_process = None
selected_ip = None

def update_global_folders():
    global SHARED_FOLDER, TARGET_FOLDER
    SHARED_FOLDER = config.config_manager.get_shared_folder()
    TARGET_FOLDER = config.config_manager.get_target_folder()

def select_shared_folder(parent):
    shared_folder = QFileDialog.getExistingDirectory(parent, "选择共享文件夹")
    if shared_folder:
        config.config_manager.update_shared_folder(shared_folder)
    update_global_folders()
    print(f"选择的共享文件夹路径：{SHARED_FOLDER}")

def select_target_folder(parent):
    target_folder = QFileDialog.getExistingDirectory(parent,"选择上传文件夹")
    if target_folder:
        config.config_manager.update_target_folder(target_folder)
    update_global_folders()
    print(f"选择的上传文件夹路径：{TARGET_FOLDER}")

def open_firewall_port():
    port = config.PORT
    try:
        subprocess.run(
            ["netsh", "advfirewall", "firewall", "add", "rule", "name=FileTransfer", "dir=in", "action=allow", "protocol=TCP", "localport=" + str(port)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print(f"已开放端口 {port} 到 Windows 防火墙")
    except subprocess.CalledProcessError as e:
        print(f"打开端口时出错: {e}")

def close_firewall_port():
    port = config.PORT
    try:
        subprocess.run(
            ["netsh", "advfirewall", "firewall", "delete", "rule", "name=FileTransfer"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print(f"已关闭端口 {port} 在 Windows 防火墙")
    except subprocess.CalledProcessError as e:
        print(f"关闭端口时出错: {e}")

def get_network_interfaces():
    interfaces = []
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET:
                interfaces.append((interface, addr.address))
    return interfaces

def on_interface_select(selected_interface):
    global selected_ip
    selected_ip = selected_interface
    print(f"已选择网络接口: {selected_ip}")

def stop_flask_server():
    global flask_server_process
    
    if flask_server_process is not None:
        print("服务器正在运行，正在关闭...")
        try:
            flask_server_process.stop()
            #关闭防火墙端口
            #close_firewall_port()
            print("服务器已关闭")
        except Exception as e:
            print(f"关闭服务器时出错: {e}")
        flask_server_process = None
    else:
        print("没有运行中的服务器。")

def start_server(port_entry):
    global flask_thread,selected_ip
    try:
        new_port = port_entry
        if new_port < 1024 or new_port > 65535:
            print("端口号无效，请输入有效的端口号（范围：1024-65535）", "red")
            return
    except ValueError:
        print("端口号格式错误，请输入一个数字", "red")
        return

    global PORT
    PORT = new_port

    if not selected_ip:
        selected_ip = get_local_ip()
    
    update_global_folders()
    '''shared_folder = config.config_manager.get_shared_folder()
    target_folder = config.config_manager.get_target_folder()

    print(f"启动服务器前的 SHARED_FOLDER: {shared_folder}")
    print(f"启动服务器前的 SHARED_FOLDER: {shared_folder}")
    print(f"启动服务器前的 TARGET_FOLDER: {target_folder}")
    print(f"启动服务器前的 TARGET_FOLDER: {target_folder}")'''

    ip_address = selected_ip.split(" - ")[-1].lstrip()

    global flask_server_process
    if flask_server_process is not None:
        print("服务器正在运行，正在关闭...")
        try:
            flask_server_process.stop()
            print("服务器已关闭")
        except Exception as e:
            print(f"关闭服务器时出错: {e}")
        flask_server_process = None
    else:
        print("")

    flask_thread = threading.Thread(target=run_flask_server, args=(ip_address,))
    flask_thread.daemon = True
    flask_thread.start()

    #打开防火墙端口
    #open_firewall_port()

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
        print(f"服务器可用的本地 IP 地址: {local_ip}")
    else:
        print(f"无法获取本地 IP 地址")

    if config.cert_file is None or config.key_file is None:
        print(f"访问 http://{ip_address}:{PORT}/files 查看文件列表")
        flask_server_process = WSGIServer((ip_address, PORT), server.app)
    else:
        print(f"访问 https://{ip_address}:{PORT}/files 查看文件列表")
        flask_server_process = WSGIServer((ip_address, PORT), server.app, keyfile=config.key_file, certfile=config.cert_file)
    flask_server_process.serve_forever()