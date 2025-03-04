import tkinter as tk
from file_transfer import file_utils,config,tool
import threading

flask_thread = None

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

def create_network_interface_selector(root, button_frame):
    interfaces = tool.get_network_interfaces()
    if not interfaces:
        file_utils.update_display("没有可用的网络接口", "red")
        return

    interface_names = [f"{iface[0]} - {iface[1]}" for iface in interfaces]

    label = tk.Label(button_frame, text="请选择网络接口：")
    label.pack(side=tk.LEFT, padx=10)
    
    interface_listbox = tk.Listbox(button_frame, height=6, width=50)
    for interface in interface_names:
        interface_listbox.insert(tk.END, interface)

    interface_listbox.bind("<<ListboxSelect>>", lambda event: tool.on_interface_select(interface_listbox, event))

    interface_listbox.pack(side=tk.LEFT, padx=10)

    return interface_listbox

def create_tkinter_window(root):

    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    interface_frame = tk.Frame(root)
    interface_frame.pack(pady=10)

    global selected_ip
    create_network_interface_selector(root, interface_frame)

    port_frame = tk.Frame(root)
    port_frame.pack(pady=10)

    tk.Label(button_frame, text="端口号:",).pack(side=tk.LEFT, padx=10)
    global port_entry
    port_entry = tk.Entry(button_frame)
    port_entry.insert(0, str(config.PORT))
    port_entry.pack(side=tk.LEFT, padx=10)

    tk.Button(button_frame, text="选择共享文件夹", command=tool.select_shared_folder).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="选择上传文件夹", command=tool.select_target_folder).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="启动服务器", command=lambda: tool.start_server(port_entry)).pack(side=tk.LEFT, padx=10)
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

def on_closing(root):
    if flask_thread is not None and flask_thread.is_alive():
        file_utils.update_display("关闭服务器")

        threading.Thread(target=tool.stop_flask_server, daemon=True).start()
        root.quit()

        # 关闭防火墙端口
        #file_utils.close_firewall_port()
    else:
        file_utils.update_display("没有启动服务器，直接退出程序")
        root.quit()
