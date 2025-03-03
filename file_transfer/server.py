from flask import Flask, jsonify, render_template_string, request, send_from_directory, redirect
from file_transfer import file_utils,main,config,html
import os

app = Flask(__name__)
@app.route('/files')
@app.route('/files/<path:path>')
def list_files(path=""):
    try:
        config.SHARED_FOLDER = config.config_manager.get_shared_folder()
        config.TARGET_FOLDER = config.config_manager.get_target_folder()
        shared_folder_path = config.SHARED_FOLDER
        target_folder_path = config.TARGET_FOLDER
        
        subfolders = main.get_target_subfolders(target_folder_path)
        items = main.get_items(os.path.join(shared_folder_path, path))

        return render_template_string(html.FILE_LIST_HTML, items=items, subfolders=subfolders, current_path=path)
    except Exception as e:
        return f"获取文件列表时出错: {str(e)}", 500

@app.route('/files/json')
@app.route('/files/json/<path:path>')
def list_files_json(path=""):
    try:
        config.SHARED_FOLDER = config.config_manager.get_shared_folder()
        shared_folder_path = config.SHARED_FOLDER
        items = main.get_items(os.path.join(shared_folder_path, path))

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
        file_utils.update_display(f"尝试下载文件: {file_path}")
        if not os.path.exists(file_path):
            file_utils.update_display(f"文件不存在: {file_path}")
            return jsonify({"error": "文件不存在"}), 404
        return send_from_directory(config.SHARED_FOLDER, filename, as_attachment=True)
    except Exception as e:
        file_utils.update_display(f"下载文件时出错: {str(e)}")
        return jsonify({"error": f"下载文件时出错: {str(e)}"}), 500
    
@app.route('/shutdown', methods=['POST'])
def shutdown():
    shared_folder="D:\\"
    target_folder="C:\\"
    config.config_manager.update_shared_folder(shared_folder)
    config.config_manager.update_target_folder(target_folder)
    file_utils.update_display("正在关闭服务器...")
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        file_utils.update_display("无法使用 Werkzeug 关闭服务器，正在强制关闭...")
        os._exit(0)
    else:
        func()
        return jsonify({"message": "服务器已关闭"}), 200

@app.before_request
def log_request_info():
    log_message = f'{request.remote_addr} - - [{request.date}] "{request.method} {request.path} HTTP/{request.environ.get("SERVER_PROTOCOL")}" {request.status_code if hasattr(request, "status_code") else ""}'
    file_utils.update_display(log_message)

@app.after_request
def log_response_info(response):
    log_message = f'{request.remote_addr} - - [{request.date}] "{request.method} {request.path} HTTP/{request.environ.get("SERVER_PROTOCOL")}" {response.status_code}'
    file_utils.update_display(log_message)
    return response

@app.route('/refresh')
def refresh():
    return jsonify({"message": "页面已刷新"})
'''
@app.before_request
def before_request():
    # 如果请求是 HTTP（不是 HTTPS），就重定向到 HTTPS
    if not request.is_secure:
        return redirect(request.url.replace("http://", "https://"), code=301)'''