/**
 * File Upload Module
 * Handles drag-and-drop file uploads and CSV processing
 */

// Initialize file upload functionality
function initializeFileUpload() {
    const fileInput = document.getElementById('csv_file');
    const importForm = fileInput ? fileInput.closest('form') : null;
    const globalDropzone = document.getElementById('globalDropzone');
    
    if (fileInput && importForm && globalDropzone) {
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            document.addEventListener(eventName, preventDefaults, false);
        });

        // Counter to track drag enter/leave events
        let dragCounter = 0;
        
        // Show global dropzone when dragging over the document
        document.addEventListener('dragenter', function(e) {
            dragCounter++;
            if (e.dataTransfer.types && e.dataTransfer.types.includes('Files')) {
                globalDropzone.classList.add('global-dropzone-active');
                console.log('Drag enter - showing dropzone', dragCounter);
            }
        });
        
        // Hide global dropzone when leaving the document
        document.addEventListener('dragleave', function(e) {
            dragCounter--;
            if (dragCounter === 0) {
                globalDropzone.classList.remove('global-dropzone-active');
                console.log('Drag leave - hiding dropzone', dragCounter);
            }
        });
        
        // Keep dropzone visible during dragover
        document.addEventListener('dragover', function(e) {
            e.preventDefault();
            if (e.dataTransfer.types && e.dataTransfer.types.includes('Files')) {
                if (!globalDropzone.classList.contains('global-dropzone-active')) {
                    globalDropzone.classList.add('global-dropzone-active');
                    console.log('Drag over - showing dropzone');
                }
            }
        });
        
        // Handle file drop anywhere on the document
        document.addEventListener('drop', function(e) {
            e.preventDefault();
            dragCounter = 0;
            globalDropzone.classList.remove('global-dropzone-active');
            console.log('Drop - hiding dropzone');
            
            const dt = e.dataTransfer;
            const files = dt.files;
            
            if (files.length > 0) {
                if (isCSVFile(files[0])) {
                    // Show loading indicator
                    const loadingToast = document.createElement('div');
                    loadingToast.className = 'fixed bottom-4 right-4 bg-forest-green text-white px-4 py-2 rounded shadow-lg z-50 flex items-center';
                    loadingToast.innerHTML = `
                        <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Uploading ${files[0].name}...
                    `;
                    document.body.appendChild(loadingToast);
                    
                    // Set the file input value
                    fileInput.files = files;
                    
                    // Instead of using fetch, submit the form directly
                    importForm.submit();
                } else {
                    // For non-CSV files, we need to send a request to set the error in session
                    const uploadErrorUrl = importForm.getAttribute('data-error-url') || '/upload/error';
                    const dashboardUrl = importForm.getAttribute('data-dashboard-url') || '/dashboard';
                    
                    fetch(uploadErrorUrl, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || ''
                        },
                        body: JSON.stringify({
                            error_message: `Invalid file type: ${files[0].name}. Only CSV files are supported.`
                        })
                    })
                    .then(() => {
                        window.location.href = dashboardUrl;
                    })
                    .catch(() => {
                        // Fallback if the error endpoint fails
                        window.location.href = dashboardUrl;
                    });
                }
            }
        });
    }
}

// Prevent default drag behaviors
function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

// Helper function to check if file is a CSV
function isCSVFile(file) {
    return file.name.toLowerCase().endsWith('.csv');
}

export { initializeFileUpload, preventDefaults, isCSVFile }; 