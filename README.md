# 文件共享与传输程序

## 介绍

这个程序允许在局域网内共享指定文件夹，并支持其他设备上传文件到运行该程序的设备。用户可以通过自定义的HTML界面下载和上传文件。程序使用Tkinter制作GUI界面，并支持HTTPS协议（只需在程序运行目录放置 `.crt` 和 `.key` 文件）。默认情况下，程序使用HTTP协议，用户可以选择自定义端口来开启服务。在程序运行时，用户可以选择上传文件夹和共享文件夹，以自定义使用的目录，最后通过启动服务器来实现文件共享。程序的GUI界面支持日志显示，便于用户查看操作记录。

## 功能

- 在局域网内共享指定文件夹
- 允许其他设备上传文件
- 自定义HTML界面用于文件下载和上传
- 使用Tkinter制作的用户友好GUI
- 支持HTTPS协议（需提供证书文件）
- 默认使用HTTP协议
- 自定义端口设置
- 日志显示功能

## 安装与运行

### 安装依赖

使用以下命令安装所需的Python库：

```bash
pip install gevent threading webbrowser socket platform subprocess psutil flask pillow json
运行程序
你可以使用以下任一方式来运行程序：

使用 PyInstaller 打包程序：

pyinstaller --onefile main.py
然后在 dist 目录下找到可执行文件。

直接运行 Python 脚本：

python main.py
示例用法
启动程序后，选择上传文件夹和共享文件夹。
点击“启动服务器”按钮。
通过局域网内的其他设备访问共享文件夹。
上传文件到指定的文件夹。
注意事项
确保在程序运行目录下放置 .crt 和 .key 文件以启用HTTPS。
默认情况下，程序使用HTTP协议。
