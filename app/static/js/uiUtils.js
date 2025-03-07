/**
 * UI Utilities Module
 * Handles dropdown menus, alerts, and other UI elements
 */

// Initialize kebab menu dropdown
function initializeKebabMenu() {
    const kebabMenuBtn = document.getElementById('kebabMenuBtn');
    const kebabDropdown = document.getElementById('kebabMenu');
    
    if (kebabMenuBtn && kebabDropdown) {
        kebabMenuBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            kebabDropdown.classList.toggle('hidden');
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!kebabDropdown.contains(e.target) && e.target !== kebabMenuBtn) {
                kebabDropdown.classList.add('hidden');
            }
        });
    }
}

// Initialize action buttons
function initializeActionButtons() {
    // Action button event listeners
    const addContactBtn = document.getElementById('addClientBtn');
    const importBtn = document.getElementById('importCSVBtn');
    const exportBtn = document.getElementById('exportBtn');
    const deleteAllBtn = document.getElementById('deleteAllBtn');
    const removeDuplicatesBtn = document.getElementById('removeDuplicatesBtn');
    
    if (addContactBtn) {
        addContactBtn.addEventListener('click', function() {
            window.openModal('addContactModal');
        });
    }
    
    if (importBtn) {
        importBtn.addEventListener('click', function() {
            window.openModal('importModal');
        });
    }
    
    if (exportBtn) {
        exportBtn.addEventListener('click', function() {
            // The URL is already handled in the HTML with url_for
            // This is just a fallback
            const downloadUrl = exportBtn.getAttribute('href') || '/download_all_contacts';
            window.location.href = downloadUrl;
        });
    }
    
    if (deleteAllBtn) {
        deleteAllBtn.addEventListener('click', function() {
            window.openModal('deleteAllModal');
        });
    }
    
    if (removeDuplicatesBtn) {
        removeDuplicatesBtn.addEventListener('click', function() {
            window.openModal('removeDuplicatesModal');
        });
    }
}

// Initialize flatpickr close button
function initializeFlatpickrCloseButton() {
    document.addEventListener('click', function(e) {
        // Check if the click is on the flatpickr close button
        if (e.target && e.target.closest('.flatpickr-calendar') && 
            e.clientX >= e.target.closest('.flatpickr-calendar').getBoundingClientRect().right - 30 &&
            e.clientY <= e.target.closest('.flatpickr-calendar').getBoundingClientRect().top + 30) {
            
            // Find and close all open flatpickr instances
            const openCalendars = document.querySelectorAll('.flatpickr-calendar.open');
            if (openCalendars.length > 0) {
                // Find the flatpickr instance and close it
                const input = document.querySelector('.flatpickr-input');
                if (input && input._flatpickr) {
                    input._flatpickr.close();
                }
            }
        }
    });
}

export { 
    initializeKebabMenu, 
    initializeActionButtons, 
    initializeFlatpickrCloseButton 
}; 