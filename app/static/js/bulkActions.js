/**
 * Bulk Actions Module
 * Handles checkbox selection and bulk operations on contacts
 */

// Initialize bulk actions functionality
function initializeBulkActions() {
    const selectAllCheckbox = document.getElementById('selectAllCheckbox');
    const contactCheckboxes = document.querySelectorAll('.contact-checkbox');
    const bulkActionButtons = document.getElementById('bulkActionButtons');
    const selectedCountElement = document.getElementById('selectedCount');
    
    // Function to update the selected count and toggle bulk action buttons
    function updateSelectedState() {
        const selectedCheckboxes = document.querySelectorAll('.contact-checkbox:checked');
        const selectedCount = selectedCheckboxes.length;
        
        if (selectedCount > 0) {
            bulkActionButtons.classList.remove('hidden');
            if (selectedCountElement) {
                selectedCountElement.textContent = selectedCount;
            }
        } else {
            bulkActionButtons.classList.add('hidden');
        }
        
        // Update "select all" checkbox state
        if (selectedCount === contactCheckboxes.length && selectedCount > 0) {
            selectAllCheckbox.checked = true;
            selectAllCheckbox.indeterminate = false;
        } else if (selectedCount > 0) {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = true;
        } else {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = false;
        }
    }
    
    // Add event listeners to all contact checkboxes
    contactCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateSelectedState);
        
        // Make sure row clicks don't trigger when clicking on checkboxes
        checkbox.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    });
    
    // Handle "select all" checkbox
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const isChecked = this.checked;
            
            contactCheckboxes.forEach(checkbox => {
                checkbox.checked = isChecked;
            });
            
            updateSelectedState();
        });
    }
    
    // Set up bulk action button event listeners
    setupBulkActionButtons();
}

// Set up bulk action button event listeners
function setupBulkActionButtons() {
    document.getElementById('bulkConfirmAddress')?.addEventListener('click', function() {
        const selectedIds = getSelectedContactIds();
        console.log('Request address confirmation for:', selectedIds);
    });
    
    document.getElementById('bulkEnrichData')?.addEventListener('click', function() {
        const selectedIds = getSelectedContactIds();
        console.log('Enrich client data for:', selectedIds);
    });
    
    document.getElementById('bulkSendGift')?.addEventListener('click', function() {
        const selectedIds = getSelectedContactIds();
        console.log('Send gift to:', selectedIds);
    });
    
    document.getElementById('bulkSendMessage')?.addEventListener('click', function() {
        const selectedIds = getSelectedContactIds();
        console.log('Send message to:', selectedIds);
    });
    
    document.getElementById('bulkDelete')?.addEventListener('click', function(e) {
        const selectedIds = getSelectedContactIds();
        
        if (selectedIds.length === 0) {
            alert('No contacts selected for deletion.');
            e.preventDefault();
            return;
        }
        
        if (confirm(`Are you sure you want to delete ${selectedIds.length} selected contact(s)?`)) {
            // Get the form
            const form = document.getElementById('bulkDeleteForm');
            
            // Clear any existing hidden inputs
            const selectedContactIdsDiv = document.getElementById('selectedContactIds');
            selectedContactIdsDiv.innerHTML = '';
            
            // Add selected IDs
            selectedIds.forEach(id => {
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = 'contact_ids[]';
                input.value = id;
                selectedContactIdsDiv.appendChild(input);
            });
            
            // Submit the form
            form.submit();
        } else {
            e.preventDefault();
        }
    });
}

// Helper function to get selected contact IDs
function getSelectedContactIds() {
    return Array.from(document.querySelectorAll('.contact-checkbox:checked'))
        .map(checkbox => checkbox.getAttribute('data-contact-id'));
}

export { initializeBulkActions, getSelectedContactIds }; 