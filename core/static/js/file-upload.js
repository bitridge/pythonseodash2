document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('id_files');
    const fileList = document.getElementById('file-list');
    const maxFileSize = 50 * 1024 * 1024; // 50MB
    const allowedTypes = [
        'image/jpeg',
        'image/png',
        'image/gif',
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ];

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    // Highlight drop zone when dragging over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    // Handle dropped files
    dropZone.addEventListener('drop', handleDrop, false);

    // Handle file input change
    fileInput.addEventListener('change', handleFiles, false);

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function highlight(e) {
        dropZone.classList.add('drag-over');
    }

    function unhighlight(e) {
        dropZone.classList.remove('drag-over');
    }

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles({ target: { files: files } });
    }

    function handleFiles(e) {
        const files = [...e.target.files];
        files.forEach(validateAndPreviewFile);
        
        // Update the file input with the new files
        const dt = new DataTransfer();
        const existingFiles = fileInput.files;
        [...existingFiles].forEach(file => dt.items.add(file));
        files.forEach(file => dt.items.add(file));
        fileInput.files = dt.files;
    }

    function validateAndPreviewFile(file) {
        // Validate file type
        if (!allowedTypes.includes(file.type)) {
            showError(`File type not allowed: ${file.name}`);
            return;
        }

        // Validate file size
        if (file.size > maxFileSize) {
            showError(`File too large (max 50MB): ${file.name}`);
            return;
        }

        // Create preview
        const reader = new FileReader();
        reader.onloadend = function() {
            const preview = createFilePreview(file, reader.result);
            fileList.appendChild(preview);
        }

        if (file.type.startsWith('image/')) {
            reader.readAsDataURL(file);
        } else {
            reader.readAsArrayBuffer(file);
        }
    }

    function createFilePreview(file, result) {
        const div = document.createElement('div');
        div.className = 'file-preview';

        // Add appropriate icon or image preview
        if (file.type.startsWith('image/')) {
            const img = document.createElement('img');
            img.src = result;
            img.className = 'file-thumbnail';
            div.appendChild(img);
        } else {
            const icon = document.createElement('i');
            icon.className = getFileIcon(file.type);
            div.appendChild(icon);
        }

        // Add file info
        const info = document.createElement('div');
        info.className = 'file-info';
        info.innerHTML = `
            <span class="file-name">${file.name}</span>
            <span class="file-size">${formatFileSize(file.size)}</span>
        `;
        div.appendChild(info);

        // Add remove button
        const removeBtn = document.createElement('button');
        removeBtn.type = 'button';
        removeBtn.className = 'remove-file';
        removeBtn.innerHTML = '×';
        removeBtn.onclick = function() {
            div.remove();
            removeFileFromInput(file);
        };
        div.appendChild(removeBtn);

        return div;
    }

    function removeFileFromInput(fileToRemove) {
        const dt = new DataTransfer();
        const files = fileInput.files;
        
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            if (file !== fileToRemove) {
                dt.items.add(file);
            }
        }
        
        fileInput.files = dt.files;
    }

    function getFileIcon(fileType) {
        if (fileType.startsWith('image/')) {
            return 'fas fa-file-image';
        } else if (fileType.includes('pdf')) {
            return 'fas fa-file-pdf';
        } else if (fileType.includes('word')) {
            return 'fas fa-file-word';
        } else if (fileType.includes('sheet') || fileType.includes('excel')) {
            return 'fas fa-file-excel';
        }
        return 'fas fa-file';
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    function showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger alert-dismissible fade show';
        errorDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        document.querySelector('.messages').appendChild(errorDiv);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }
}); 