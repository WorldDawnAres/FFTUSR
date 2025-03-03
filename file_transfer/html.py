FILE_LIST_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>文件传输</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        
        /* 🌟 默认左右排列：PC端 */
        .container { display: flex; gap: 20px; }
        .file-list, .upload-form { flex: 1; padding: 20px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); border-radius: 5px; }

        h1, h2 { color: #333; }
        ul { list-style-type: none; padding: 0; }
        li { margin: 10px 0; }
        a { text-decoration: none; color: #007BFF; }
        a:hover { text-decoration: underline; }

        /* 上传部分的样式 */
        input[type="file"], select, input[type="submit"] { 
            margin: 15px 0;
            font-size: 14px; 
            color: #333; 
            border: 1px solid #ccc; 
            border-radius: 5px;
            background-color: #f9f9f9;
            padding: 12px; /* 增加内边距以调节高度 */
            width: 100%;
            max-width: 400px;  /* 限制最大宽度 */
            box-sizing: border-box;  /* 确保 padding 和边框不会影响总宽度 */
        }

        input[type="file"] {
            /* 修改文件选择框的样式，使其与其他输入框一致 */
            padding: 12px;
        }

        input[type="submit"]:hover {
            background-color: #4CAF50;
            color: white;
            cursor: pointer;
        }

        input[type="file"]:focus, select:focus, input[type="submit"]:focus {
            outline: none;
            border-color: #4CAF50;
            box-shadow: 0 0 5px rgba(0, 200, 0, 0.5);
        }
        
        /* 上传进度条样式 */
        #progress-container { margin-top: 10px; width: 100%; background: #ddd; border-radius: 5px; }
        #progress-bar { height: 20px; width: 0%; background: #4CAF50; border-radius: 5px; text-align: center; color: white; line-height: 20px; }

        /* 📱 手机端自动切换为上下结构 */
        @media screen and (max-width: 768px) {
            .container { flex-direction: column; }
        }

        /* 🌟 PC端：上传部分垂直排列 */
        @media screen and (min-width: 768px) {
            .upload-form {
                display: block;
                width: 100%;
            }
            .upload-form input[type="file"],
            .upload-form select,
            .upload-form input[type="submit"] {
                width: 100%; /* 确保宽度填满 */
            }

            .upload-form label {
                display: block; /* 确保 label 也在新的一行 */
                margin-bottom: 5px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- 📤 文件上传 -->
        <div class="upload-form">
            <h2>上传文件</h2>
            <form id="upload-form" method="post" action="/upload" enctype="multipart/form-data">
                <input type="file" id="file-input" name="file" required>
                <label for="target_folder">选择目标文件夹：</label>
                <select id="target_folder" name="target_folder">
                    <option value="">默认上传目录</option>
                    {% for folder in subfolders %}
                        <option value="{{ folder }}">{{ folder }}</option>
                    {% endfor %}
                </select>
                <input type="submit" value="上传">
            </form>
            <div id="progress-container">
                <div id="progress-bar">0%</div>
            </div>
        </div>

        <!-- 📂 文件列表 -->
        <div class="file-list">
            <h1>文件列表</h1>
            <p>当前路径: /{{ current_path }}</p>
            <ul>
                {% for item in items %}
                    <li>
                        {% if item.is_dir %}
                            <a href="/files/{{ item.path }}">{{ item.name }}/</a>
                        {% else %}
                            <a href="/download/{{ item.path }}" target="_blank">{{ item.name }}</a>
                        {% endif %}
                    </li>
                {% endfor %}
            </ul>
        </div>
    </div>

    <script>
        // 上传功能的 JavaScript 代码
        document.getElementById('upload-form').addEventListener('submit', function(event) {
            event.preventDefault();
            let fileInput = document.getElementById('file-input');
            let targetFolder = document.getElementById('target_folder').value;
            let formData = new FormData();
            formData.append('file', fileInput.files[0]);
            formData.append('target_folder', targetFolder);

            let xhr = new XMLHttpRequest();
            xhr.open('POST', '/upload', true);

            xhr.upload.onprogress = function(event) {
                if (event.lengthComputable) {
                    let percent = Math.round((event.loaded / event.total) * 100);
                    document.getElementById('progress-bar').style.width = percent + '%';
                    document.getElementById('progress-bar').textContent = percent + '%';
                }
            };

            xhr.onload = function() {
                if (xhr.status === 200) {
                    alert('上传成功');
                    document.getElementById('progress-bar').style.width = '0%';
                    document.getElementById('progress-bar').textContent = '0%';
                    window.location.reload();
                } else {
                    alert('上传失败');
                }
            };

            xhr.send(formData);
        });
    </script>
</body>
</html>
"""