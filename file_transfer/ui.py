import tkinter as tk
from file_transfer import file_utils,config,server
from tkinter import filedialog
import requests,threading,webbrowser,socket,platform,subprocess,psutil
from gevent.pywsgi import WSGIServer

flask_thread = None
flask_server_process = None

light_mode_colors = {
    "bg": "#ffffff",
    "fg": "#000000",
    "button_bg": "#f0f0f0",
    "button_fg": "#000000",
    "text_bg": "#ffffff",
    "text_fg": "#000000",
}

dark_mode_colors = {
    "bg": "#2e2e2e",
    "fg": "#ffffff",
    "button_bg": "#4a4a4a",
    "button_fg": "#ffffff",
    "text_bg": "#333333",
    "text_fg": "#ffffff",
}

current_mode = "dark"

def toggle_mode(root, button_frame,log_text,mode_button,interface_frame):
    global current_mode
    if current_mode == "light":
        apply_dark_mode(root, button_frame,log_text,mode_button,interface_frame)
        mode_button.config(text="切换到浅色模式")
        current_mode = "dark"
    else:
        apply_light_mode(root,button_frame,log_text,mode_button,interface_frame)
        mode_button.config(text="切换到暗色模式")
        current_mode = "light"

def apply_light_mode(root, button_frame,log_text,mode_button,interface_frame):
    root.config(bg=light_mode_colors["bg"])
    button_frame.config(bg=light_mode_colors["bg"])
    interface_frame.config(bg=light_mode_colors["bg"])
    log_text.config(bg=light_mode_colors["text_bg"], fg=light_mode_colors["text_fg"])
    
    for button in button_frame.winfo_children():
        button.config(bg=light_mode_colors["button_bg"], fg=light_mode_colors["button_fg"])
    for button in interface_frame.winfo_children():
        button.config(bg=light_mode_colors["button_bg"], fg=light_mode_colors["button_fg"])
    
    mode_button.config(bg=light_mode_colors["button_bg"], fg=light_mode_colors["button_fg"])

def apply_dark_mode(root, button_frame,log_text,mode_button,interface_frame):
    root.config(bg=dark_mode_colors["bg"])
    button_frame.config(bg=dark_mode_colors["bg"])
    interface_frame.config(bg=dark_mode_colors["bg"])
    log_text.config(bg=dark_mode_colors["text_bg"], fg=dark_mode_colors["text_fg"])

    for button in button_frame.winfo_children():
        button.config(bg=dark_mode_colors["button_bg"], fg=dark_mode_colors["button_fg"])
    for button in interface_frame.winfo_children():
        button.config(bg=dark_mode_colors["button_bg"], fg=dark_mode_colors["button_fg"])
    
    mode_button.config(bg=dark_mode_colors["button_bg"], fg=dark_mode_colors["button_fg"])

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

def create_network_interface_selector(root, button_frame):
    interfaces = get_network_interfaces()
    if not interfaces:
        file_utils.update_display("没有可用的网络接口", "red")
        return

    interface_names = [f"{iface[0]} - {iface[1]}" for iface in interfaces]

    label = tk.Label(button_frame, text="请选择网络接口：")
    label.pack(side=tk.LEFT, padx=10)
    
    interface_listbox = tk.Listbox(button_frame, height=6, width=50)
    for interface in interface_names:
        interface_listbox.insert(tk.END, interface)

    interface_listbox.bind("<<ListboxSelect>>", lambda event: on_interface_select(interface_listbox, event))

    interface_listbox.pack(side=tk.LEFT, padx=10)

    return interface_listbox

def create_tkinter_window(root):

    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    interface_frame = tk.Frame(root)
    interface_frame.pack(pady=10, fill=tk.X)

    global selected_ip
    selected_ip = None
    create_network_interface_selector(root, interface_frame)

    port_frame = tk.Frame(root)
    port_frame.pack(pady=10, fill=tk.Y)

    tk.Label(button_frame, text="端口号: ").pack(side=tk.LEFT, padx=10)
    global port_entry
    port_entry = tk.Entry(button_frame)
    port_entry.insert(0, str(config.PORT))
    port_entry.pack(side=tk.LEFT, padx=10)

    tk.Button(button_frame, text="选择共享文件夹", command=select_shared_folder).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="选择上传文件夹", command=select_target_folder).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="启动服务器", command=start_server).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="停止服务器", command=lambda: on_closing(root)).pack(side=tk.LEFT, padx=10)

    global log_text
    log_text = tk.Text(root, height=30, width=90)
    log_text.pack(pady=10)
    log_text.insert(tk.END, "日志信息：\n")

    mode_button = tk.Button(root, text="切换到浅色模式", command=lambda: toggle_mode(root,button_frame,log_text,mode_button,interface_frame))
    mode_button.pack(pady=10)

    apply_dark_mode(root, button_frame,log_text,mode_button,interface_frame)

    log_text.tag_configure("info", foreground="orange")
    log_text.tag_configure("info1", foreground="green")  # GET /files 请求，绿色
    log_text.tag_configure("great", foreground="pink")  # 200 状态码，紫色
    log_text.tag_configure("error", foreground="red")  # 404 错误，红色
    log_text.tag_configure("info2", foreground="purple")  # POST 请求，粉色

def stop_flask_server():
    global flask_server_process
    
    if flask_server_process is not None:
        file_utils.update_display("服务器正在运行，正在关闭...")
        try:
            flask_server_process.stop()  # 尝试优雅停止服务器
            file_utils.update_display("服务器已关闭")
        except Exception as e:
            file_utils.update_display(f"关闭服务器时出错: {e}")
        flask_server_process = None  # 清除进程对象
    else:
        file_utils.update_display("没有运行中的服务器。")

def on_closing(root):
    if flask_thread is not None and flask_thread.is_alive():
        file_utils.update_display("关闭服务器")

        threading.Thread(target=stop_flask_server, daemon=True).start()
        root.quit()

        # 关闭防火墙端口
        #file_utils.close_firewall_port()
    else:
        file_utils.update_display("没有启动服务器，直接退出程序")
        root.quit()

def start_server():
    global flask_thread , selected_ip
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
