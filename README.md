# 文件共享与传输程序
[下载链接](https://github.com/WorldDawnAres/FFTUSR/releases)

<br/>

>对这个程序感兴趣吗？ 希望感兴趣的可以给这个项目留个星 ⭐

## 功能

- 在局域网内共享指定文件夹
- 允许其他设备上传文件
- 在程序的HTML界面用于文件下载和上传
- 有上传进度条
- 根据程序运行目录自动切换http或HTTPS协议（使用HTTPS需提供证书文件，默认使用HTTP）
- 自动检测网口ip (可自定义选择启动程序的ip)
- 可自定义端口设置 (默认12345)
- 日志显示功能

## 介绍

这个程序允许在局域网内共享指定文件夹，并支持其他设备上传文件到运行该程序的设备。程序使用Tkinter制作GUI界面，并支持HTTPS协议（只需在程序运行目录放置 .crt 和 .key 文件）。默认情况下，程序使用HTTP协议。

<img src="./Pictures/1.png" alt="Screenshot 1" width="600" />

用户可以通过自定义的HTML界面下载和上传文件。用户可以选择自定义端口来开启服务。在程序运行时，用户可以点击选择共享文件夹和选择上传文件夹来自定义选择程序使用的文件夹，最后通过启动服务器来实现文件共享。程序的GUI界面支持日志显示，便于用户查看操作记录。

<img src="./Pictures/2.png" alt="Screenshot 1" width="600" />

此外程序还可以切换浅色和深色模式。

<img src="./Pictures/2.png" alt="Screenshot 1" width="600" />

## 安装与运行

### 安装依赖

使用以下命令安装所需的Python库：

```
pip install gevent threading webbrowser socket platform subprocess psutil flask pillow json
```
### 运行程序
你可以使用以下任一方式来运行程序：

#### 方法一
使用 PyInstaller 打包程序：
```
PyInstaller -F --add-data "icon/*;icon" -i file-transfer\icon\icon.jpg main.py
```
然后在 dist 目录下找到可执行文件。

#### 方法二
直接运行 Python 脚本：
```
python main.py
```
### 用法
启动程序后，选择上传文件夹和共享文件夹。
点击“启动服务器”按钮。
通过局域网内的其他设备访问共享文件夹。
上传文件到指定的文件夹。
### 注意事项
确保在程序运行目录下放置 .crt 和 .key 文件以启用HTTPS。

默认情况下，程序使用HTTP协议。
