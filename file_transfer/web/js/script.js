document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const uploadForm = document.getElementById('upload-form');
    const progressBar = document.getElementById('progress-bar');
    const clearBtn = document.getElementById('cancel-all-btn');
    let selectedFiles = [];

    if (clearBtn) {
        clearBtn.addEventListener('click', function () {
            selectedFiles = [];
            fileInput.value = '';

            const existingListContainer = dropZone.querySelector('.file-list-container');
            if (existingListContainer) {
                existingListContainer.remove();
            }

            document.getElementById('drop-zone-text').style.display = 'block';

            progressBar.style.width = '0%';
            progressBar.textContent = '0%';
        });
    }

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('drag-over');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        handleFileSelection(e.dataTransfer.items);
    });

    dropZone.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        handleFileSelection(e.target.files);
    });

    uploadForm.addEventListener('submit', function (event) {
        event.preventDefault();
        if (selectedFiles.length === 0) {
            alert('请先选择文件或文件夹');
            return;
        }
        const targetFolder = document.getElementById('target_folder').value;
        uploadFiles(selectedFiles, targetFolder);
    });

    async function handleFileSelection(input) {
        selectedFiles = [];
        const fileListContainer = document.createElement('div');
        fileListContainer.className = 'file-list-container';
        fileListContainer.style.width = '100%';
        fileListContainer.style.maxHeight = '300px';
        fileListContainer.style.overflowY = 'auto';
        document.getElementById('drop-zone-text').style.display = 'none';

        const ul = document.createElement('ul');
        ul.className = 'file-list';

        async function traverseFileTree(item, path) {
            path = path || "";
            if (item.isFile) {
                return new Promise((resolve) => {
                    item.file((file) => {
                        file.webkitRelativePath = path + file.name;
                        selectedFiles.push(file);
                        resolve();
                    });
                });
            } else if (item.isDirectory) {
                const dirReader = item.createReader();
                return new Promise((resolve) => {
                    dirReader.readEntries(async (entries) => {
                        for (let i = 0; i < entries.length; i++) {
                            await traverseFileTree(entries[i], path + item.name + "/");
                        }
                        resolve();
                    });
                });
            }
        }

        if (input instanceof FileList) {
            for (let i = 0; i < input.length; i++) {
                selectedFiles.push(input[i]);
            }
        } else if (input instanceof DataTransferItemList) {
            for (let i = 0; i < input.length; i++) {
                const item = input[i].webkitGetAsEntry();
                if (item) {
                    if (item.isDirectory) {
                        await traverseFileTree(item, "");
                    } else {
                        await traverseFileTree(item);
                    }
                }
            }
        }

        selectedFiles.forEach(file => {
            const li = document.createElement('li');
            li.className = 'file-item';
            li.textContent = file.webkitRelativePath ? file.webkitRelativePath : file.name;

            const removeButton = document.createElement('span');
            removeButton.textContent = ' x';
            removeButton.className = 'remove-file';
            removeButton.onclick = function (event) {
                event.stopPropagation();
                selectedFiles = selectedFiles.filter(f => f !== file);
                li.remove();
                if (selectedFiles.length === 0) {
                    document.getElementById('drop-zone-text').style.display = 'block';
                    const existingListContainer = dropZone.querySelector('.file-list-container');
                    if (existingListContainer) {
                        existingListContainer.remove();
                    }
                }
            };

            li.appendChild(removeButton);
            ul.appendChild(li);
        });

        fileListContainer.appendChild(ul);

        const existingListContainer = dropZone.querySelector('.file-list-container');
        if (existingListContainer) {
            existingListContainer.remove();
        }
        dropZone.appendChild(fileListContainer);

        fileInput.value = '';

        if (selectedFiles.length === 0) {
            document.getElementById('drop-zone-text').style.display = 'block';
            fileListContainer.remove();
        }
    }

    function uploadFiles(files, targetFolder) {
        const formData = new FormData();
        let isFolderUpload = false;

        if (files.length > 0 && files[0].webkitRelativePath) {
            isFolderUpload = files[0].webkitRelativePath.includes('/');
        }

        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            formData.append('files', file);
            if (isFolderUpload) {
                formData.append('relative_paths', file.webkitRelativePath);
            }
        }

        formData.append('target_folder', targetFolder);

        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/upload', true);

        xhr.upload.onprogress = function (event) {
            if (event.lengthComputable) {
                const percent = Math.round((event.loaded / event.total) * 100);
                progressBar.style.width = percent + '%';
                progressBar.textContent = percent + '%';
            }
        };

        xhr.onload = function () {
            if (xhr.status === 200) {
                const response = JSON.parse(xhr.responseText);
                alert(response.message);
                progressBar.style.width = '0%';
                progressBar.textContent = '0%';
                window.location.reload();
            } else {
                alert('上传失败');
            }
        };

        xhr.send(formData);
    }
});
