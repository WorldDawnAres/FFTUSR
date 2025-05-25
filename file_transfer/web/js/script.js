document.addEventListener('DOMContentLoaded', function() {
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
});
