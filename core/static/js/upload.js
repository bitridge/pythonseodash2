class FileUpload {
    constructor(dropArea, fileInput, previewArea, maxFileSize = 10) {
        this.dropArea = dropArea;
        this.fileInput = fileInput;
        this.previewArea = previewArea;
        this.maxFileSize = maxFileSize; // MB
        this.setupListeners();
    }

    setupListeners() {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            this.dropArea.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            this.dropArea.addEventListener(eventName, () => {
                this.dropArea.classList.add('drag-active');
            });
        });

        ['dragleave', 'drop'].forEach(eventName => {
            this.dropArea.addEventListener(eventName, () => {
                this.dropArea.classList.remove('drag-active');
            });
        });

        this.dropArea.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            this.handleFiles(files);
        });

        this.fileInput.addEventListener('change', () => {
            this.handleFiles(this.fileInput.files);
        });
    }

    handleFiles(files) {
        [...files].forEach(file => {
            if (file.size > this.maxFileSize * 1024 * 1024) {
                alert(`File ${file.name} is too large. Maximum size is ${this.maxFileSize}MB.`);
                return;
            }
            this.previewFile(file);
        });
    }

    previewFile(file) {
        const reader = new FileReader();
        const preview = document.createElement('div');
        preview.className = 'file-preview';
        
        reader.onloadend = () => {
            const fileType = file.type.split('/')[0];
            let previewContent = '';
            
            if (fileType === 'image') {
                previewContent = `
                    <div class="preview-item">
                        <img src="${reader.result}" alt="${file.name}">
                        <div class="preview-info">
                            <span>${file.name}</span>
                            <button type="button" class="btn btn-sm btn-danger remove-file">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                    </div>
                `;
            } else {
                const icon = this.getFileIcon(file.type);
                previewContent = `
                    <div class="preview-item">
                        <div class="file-icon">
                            <i class="${icon}"></i>
                        </div>
                        <div class="preview-info">
                            <span>${file.name}</span>
                            <button type="button" class="btn btn-sm btn-danger remove-file">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                    </div>
                `;
            }
            
            preview.innerHTML = previewContent;
            this.previewArea.appendChild(preview);
            
            preview.querySelector('.remove-file').addEventListener('click', () => {
                preview.remove();
                // Remove from FileList
                const dt = new DataTransfer();
                const files = [...this.fileInput.files];
                const fileIndex = files.indexOf(file);
                if (fileIndex > -1) {
                    files.splice(fileIndex, 1);
                    files.forEach(file => dt.items.add(file));
                    this.fileInput.files = dt.files;
                }
            });
        };

        if (file) {
            reader.readAsDataURL(file);
        }
    }

    getFileIcon(mimeType) {
        const icons = {
            'application/pdf': 'fas fa-file-pdf',
            'application/msword': 'fas fa-file-word',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'fas fa-file-word',
            'application/vnd.ms-excel': 'fas fa-file-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'fas fa-file-excel',
            'application/vnd.ms-powerpoint': 'fas fa-file-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'fas fa-file-powerpoint',
            'text/plain': 'fas fa-file-alt',
            'application/zip': 'fas fa-file-archive',
            'application/x-rar-compressed': 'fas fa-file-archive',
            'image': 'fas fa-file-image',
            'default': 'fas fa-file'
        };
        
        return icons[mimeType] || icons['default'];
    }
} 