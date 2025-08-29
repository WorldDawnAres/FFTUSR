document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const folderInput = document.getElementById('folder-input');
    const uploadForm = document.getElementById('upload-form');
    const progressBar = document.getElementById('progress-bar');
    const clearBtn = document.getElementById('cancel-all-btn');
    let selectedFiles = [];

    const fileSelectionButtons = document.createElement('div');
    fileSelectionButtons.className = 'file-selection-buttons';
    fileSelectionButtons.style.display = 'none';
    
    const selectFilesBtn = document.createElement('button');
    selectFilesBtn.type = 'button';
    selectFilesBtn.id = 'select-files-btn';
    selectFilesBtn.textContent = '选择文件';
    
    const selectFolderBtn = document.createElement('button');
    selectFolderBtn.type = 'button';
    selectFolderBtn.id = 'select-folder-btn';
    selectFolderBtn.textContent = '选择文件夹';
    
    fileSelectionButtons.appendChild(selectFilesBtn);
    fileSelectionButtons.appendChild(selectFolderBtn);
    dropZone.appendChild(fileSelectionButtons);

    if (clearBtn) {
        clearBtn.addEventListener('click', function () {
            selectedFiles = [];
            fileInput.value = '';
            folderInput.value = '';

            const existingListContainer = dropZone.querySelector('.file-list-container');
            if (existingListContainer) {
                existingListContainer.remove();
            }

            document.getElementById('drop-zone-text').style.display = 'block';
            fileSelectionButtons.style.display = 'none';

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
        
        if (e.dataTransfer.items && e.dataTransfer.items.length > 0) {
            handleFileSelection(e.dataTransfer.items, true);
        } else if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            handleFileSelection(e.dataTransfer.files, true);
        }
    });

    dropZone.addEventListener('click', (e) => {
        if (e.target.id === 'select-files-btn' || e.target.id === 'select-folder-btn' ||
            e.target.className === 'file-selection-buttons') {
            return;
        }
        
        if (dropZone.querySelector('.file-list-container')) {
            return;
        }
        
        document.getElementById('drop-zone-text').style.display = 'none';
        fileSelectionButtons.style.display = 'block';
    });

    selectFilesBtn.addEventListener('click', () => {
        fileInput.click();
    });

    selectFolderBtn.addEventListener('click', () => {
        folderInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        handleFileSelection(e.target.files, true);
    });

    folderInput.addEventListener('change', (e) => {
        handleFileSelection(e.target.files, true);
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

    async function handleFileSelection(input, append = false) {
        if (!append) {
            selectedFiles = [];
        }
        
        let newFiles = [];
        let fileListContainer;
        const existingListContainer = dropZone.querySelector('.file-list-container');
        
        if (existingListContainer && append) {
            fileListContainer = existingListContainer;
        } else {
            fileListContainer = document.createElement('div');
            fileListContainer.className = 'file-list-container';
            fileListContainer.style.width = '100%';
            fileListContainer.style.maxHeight = '300px';
            fileListContainer.style.overflowY = 'auto';
            document.getElementById('drop-zone-text').style.display = 'none';
            fileSelectionButtons.style.display = 'none';
            
            if (existingListContainer) {
                existingListContainer.remove();
            }
        }

        const ul = existingListContainer && append ? existingListContainer.querySelector('.file-list') : document.createElement('ul');
        if (!ul.className) {
            ul.className = 'file-list';
        }

        async function traverseFileTree(item, path) {
            path = path || "";
            if (item.isFile) {
                return new Promise((resolve) => {
                    item.file((file) => {
                        file.webkitRelativePath = path + file.name;
                        newFiles.push(file);
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
                newFiles.push(input[i]);
            }
        } else if (input instanceof DataTransferItemList) {
            const promises = [];
            for (let i = 0; i < input.length; i++) {
                const item = input[i].webkitGetAsEntry();
                if (item) {
                    if (item.isDirectory) {
                        promises.push(traverseFileTree(item, ""));
                    } else {
                        promises.push(traverseFileTree(item));
                    }
                }
            }
            await Promise.all(promises);
        }

        selectedFiles = [...selectedFiles, ...newFiles];

        newFiles.forEach(file => {
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
                    fileSelectionButtons.style.display = 'none';
                    const existingListContainer = dropZone.querySelector('.file-list-container');
                    if (existingListContainer) {
                        existingListContainer.remove();
                    }
                }
            };

            li.appendChild(removeButton);
            ul.appendChild(li);
        });

        if (!existingListContainer || !append) {
            fileListContainer.appendChild(ul);
            dropZone.appendChild(fileListContainer);
        }

        fileInput.value = '';
        folderInput.value = '';

        if (selectedFiles.length === 0) {
            document.getElementById('drop-zone-text').style.display = 'block';
            fileSelectionButtons.style.display = 'none';
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
