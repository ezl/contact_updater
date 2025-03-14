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
                    
                    // Create FormData and append the file
                    const formData = new FormData();
                    formData.append('csv_file', files[0]);
                    
                    // Get the CSRF token
                    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
                    
                    // Submit the form using fetch
                    fetch(importForm.action, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': csrfToken,
                            'X-Requested-With': 'XMLHttpRequest'
                        },
                        body: formData
                    })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Network response was not ok');
                        }
                        return response.json();
                    })
                    .then(data => {
                        // Remove loading toast if it exists
                        const loadingToast = document.querySelector('.fixed.bottom-4.right-4');
                        if (loadingToast) {
                            loadingToast.remove();
                        }
                        
                        if (data.success) {
                            // Wait a brief moment to ensure session is set before redirect
                            setTimeout(() => {
                                window.location.href = data.redirect;
                            }, 100);
                        } else {
                            throw new Error(data.message || 'Error uploading file');
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        // Remove loading toast if it exists
                        const loadingToast = document.querySelector('.fixed.bottom-4.right-4');
                        if (loadingToast) {
                            loadingToast.remove();
                        }
                        
                        // Handle error and redirect
                        const uploadErrorUrl = importForm.getAttribute('data-error-url') || '/upload/error';
                        return fetch(uploadErrorUrl, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': csrfToken
                            },
                            body: JSON.stringify({
                                error_message: error.message || 'Error uploading file. Please try again.'
                            })
                        })
                        .then(() => {
                            // Wait a brief moment to ensure session is set before redirect
                            setTimeout(() => {
                                window.location.href = importForm.getAttribute('data-dashboard-url') || '/';
                            }, 100);
                        });
                    });
                } else {
                    // For non-CSV files, we need to send a request to set the error in session
                    const uploadErrorUrl = importForm.getAttribute('data-error-url') || '/upload/error';
                    const dashboardUrl = importForm.getAttribute('data-dashboard-url') || '/';
                    
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
                        setTimeout(() => {
                            window.location.href = dashboardUrl;
                        }, 100);
                    })
                    .catch(() => {
                        // Fallback if the error endpoint fails
                        setTimeout(() => {
                            window.location.href = dashboardUrl;
                        }, 100);
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