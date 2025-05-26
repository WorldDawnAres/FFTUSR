import functools,os
from flask import Flask, jsonify, redirect, render_template_string, request, send_from_directory, session, url_for
from file_transfer.tools import config
from file_transfer.tools.user_config import UiConfigManager

def get_target_subfolders(target_folder_path):
    subfolders = []
    if os.path.isdir(target_folder_path):
        for filename in os.listdir(target_folder_path):
            item_full_path = os.path.join(target_folder_path, filename)
            if os.path.isdir(item_full_path):
                subfolders.append(filename)
    return subfolders

def get_items(folder_path):
    items = []
    if os.path.isdir(folder_path):
        for filename in os.listdir(folder_path):
            item_full_path = os.path.join(folder_path, filename)
            is_dir = os.path.isdir(item_full_path)
            relative_path = os.path.relpath(item_full_path, config.SHARED_FOLDER)
            items.append({'name': filename, 'path': relative_path, 'is_dir': is_dir})
            #print(f"Item added: {relative_path}")
    return items

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        ui_config = UiConfigManager()
        if not ui_config.get_auth_enabled() or session.get('logged_in'):
            return view(**kwargs)
        return redirect(url_for('login'))
    return wrapped_view

app = Flask(__name__,
    static_folder=config.get_resource_path('web'),
    static_url_path='')
@app.route('/')
def index():
    return redirect(url_for('list_files'))

@app.route('/files')
@app.route('/files/<path:path>')
@login_required
def list_files(path=""):
    try:
        config.SHARED_FOLDER = config.config_manager.get_shared_folder()
        config.TARGET_FOLDER = config.config_manager.get_target_folder()
        shared_folder_path = config.SHARED_FOLDER
        target_folder_path = config.TARGET_FOLDER
        
        subfolders = get_target_subfolders(target_folder_path)
        items = get_items(os.path.join(shared_folder_path, path))

        return render_template_string(config.FILE_LIST_HTML, items=items, subfolders=subfolders, current_path=path)
    except Exception as e:
        return f"获取文件列表时出错: {str(e)}", 500

@app.route('/files/json')
@app.route('/files/json/<path:path>')
def list_files_json(path=""):
    try:
        config.SHARED_FOLDER = config.config_manager.get_shared_folder()
        shared_folder_path = config.SHARED_FOLDER
        items = get_items(os.path.join(shared_folder_path, path))

        file_list = [
            {
                "name": item['name'],
                "path": item['path'],
                "is_dir": item['is_dir']
            }
            for item in items
        ]

        return jsonify({"items": file_list})

    except Exception as e:
        return jsonify({"error": f"获取文件列表时出错: {str(e)}"}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "没有文件被上传"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "没有选择文件"}), 400

        if not config.TARGET_FOLDER:
            return jsonify({"error": "目标文件夹未设置"}), 500

        target_folder_name = request.form.get('target_folder', '')
        target_folder_path = os.path.join(config.TARGET_FOLDER, target_folder_name)
        os.makedirs(target_folder_path, exist_ok=True)

        save_path = os.path.join(target_folder_path, file.filename)
        with open(save_path, 'wb') as f:
            while True:
                chunk = file.stream.read(1024 * 1024)  # 1MB
                if not chunk:
                    break
                f.write(chunk)

        return jsonify({"success": True, "message": "上传成功"})
    except Exception as e:
        return jsonify({"error": f"上传文件时出错: {str(e)}"}), 500

@app.route('/download/<path:filename>')
def download_file(filename):
    try:
        file_path = os.path.join(config.SHARED_FOLDER, filename)
        print(f"尝试下载文件: {file_path}")
        if not os.path.exists(file_path):
            print(f"文件不存在: {file_path}")
            return jsonify({"error": "文件不存在"}), 404
        return send_from_directory(config.SHARED_FOLDER, filename, as_attachment=True)
    except Exception as e:
        print(f"下载文件时出错: {str(e)}")
        return jsonify({"error": f"下载文件时出错: {str(e)}"}), 500
    
@app.route('/shutdown', methods=['POST'])
def shutdown():
    # shared_folder="D:\\"
    # target_folder="C:\\"
    # config.config_manager.update_shared_folder(shared_folder)
    # config.config_manager.update_target_folder(target_folder)
    print("正在关闭服务器...")
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        print("无法使用 Werkzeug 关闭服务器，正在强制关闭...")
        os._exit(0)
    else:
        func()
        return jsonify({"message": "服务器已关闭"}), 200

@app.before_request
def log_request_info():
    log_message = f'{request.remote_addr} - - [{request.date}] "{request.method} {request.path} HTTP/{request.environ.get("SERVER_PROTOCOL")}" {request.status_code if hasattr(request, "status_code") else ""}'
    print(log_message)

@app.after_request
def log_response_info(response):
    log_message = f'{request.remote_addr} - - [{request.date}] "{request.method} {request.path} HTTP/{request.environ.get("SERVER_PROTOCOL")}" {response.status_code}'
    print(log_message)
    return response

@app.route('/refresh')
def refresh():
    return jsonify({"message": "页面已刷新"})

app.secret_key = os.urandom(24)
@app.route('/login', methods=['GET', 'POST'])
def login():
    ui_config = UiConfigManager()
    if not ui_config.get_auth_enabled():
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        users = ui_config.get_users()
        
        if UiConfigManager.get_active_sessions_count() >= UiConfigManager.max_sessions:
            return render_template_string(config.LOGIN_HTML, error="系统已达到最大登录人数限制，请稍后再试")
        
        existing_session_id, existing_session = UiConfigManager.get_user_session(username)
        if existing_session_id:
            UiConfigManager.remove_active_session(existing_session_id)
        
        if username in users and users[username] == password:
            session['logged_in'] = True
            session['username'] = username
            session_id = os.urandom(16).hex()
            session['sid'] = session_id
            UiConfigManager.add_active_session(username, session_id)
            return redirect(url_for('index'))
        else:
            try:
                return render_template_string(config.LOGIN_HTML, error="用户名或授权码错误")
            except Exception as e:
                app.logger.error(f"渲染模板错误: {str(e)}")
                return f"模板错误: {str(e)}", 500
    else:
        return render_template_string(config.LOGIN_HTML)
            
@app.route('/logout')
def logout():
    if session.get('logged_in'):
        UiConfigManager.remove_active_session(session.get('sid',''))
    session.clear()
    return redirect(url_for('login'))

@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"未处理的异常: {str(e)}")
    return "服务器内部错误", 500
