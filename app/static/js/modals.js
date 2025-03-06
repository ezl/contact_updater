/**
 * Modal Management Module
 * Handles opening, closing, and event handling for modals
 */

// Function to open a modal properly
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        // Reset any previous state
        modal.classList.remove('hidden');
        
        // Ensure backdrop is visible
        const backdrop = modal.querySelector('.modal-backdrop');
        if (backdrop) {
            backdrop.style.opacity = '0.75';
        }
        
        // Re-initialize click handlers for this modal
        setupModalClickHandlers(modal);
    }
}

// Function to close a modal properly
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('hidden');
    }
}

// Setup event handlers for a specific modal
function setupModalClickHandlers(modal) {
    // Store the form action if this is the contact detail modal
    let deleteFormAction = '';
    if (modal.id === 'contactDetailModal') {
        const deleteForm = modal.querySelector('form');
        if (deleteForm) {
            deleteFormAction = deleteForm.action;
        }
    }
    
    // Remove any existing event listeners (to prevent duplicates)
    const newModal = modal.cloneNode(true);
    modal.parentNode.replaceChild(newModal, modal);
    
    // Restore the form action if this is the contact detail modal
    if (newModal.id === 'contactDetailModal' && deleteFormAction) {
        const deleteForm = newModal.querySelector('form');
        if (deleteForm) {
            deleteForm.action = deleteFormAction;
        }
    }
    
    // Add click handlers to close buttons within this modal
    newModal.querySelectorAll('.modal-close, .modal-cancel').forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            closeModal(newModal.id);
        });
    });
    
    // Add click handler to the modal container for outside clicks
    newModal.addEventListener('click', function(e) {
        // If clicking directly on the modal container or on a backdrop element
        if (e.target === this || e.target.classList.contains('modal-backdrop')) {
            closeModal(this.id);
        }
    });
    
    // Prevent clicks on modal content from closing the modal
    const modalContent = newModal.querySelector('.inline-block') || newModal.querySelector('.relative');
    if (modalContent) {
        modalContent.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    }
    
    // If this is the contact detail modal, re-setup the editable fields
    if (newModal.id === 'contactDetailModal') {
        // We'll call this from main.js after importing editableFields.js
        if (typeof setupEditableFields === 'function') {
            setupEditableFields();
        }
    }
}

// Initialize all modals
function initializeModals() {
    document.querySelectorAll('.fixed').forEach(modal => {
        setupModalClickHandlers(modal);
    });
    
    // Close modals with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            // Check if any field is in edit mode
            const editingFields = document.querySelectorAll('.modal-value.editing');
            if (editingFields.length > 0) {
                // Don't close the modal if a field is being edited
                return;
            }
            
            // Find visible modals and hide them
            document.querySelectorAll('.fixed:not(.hidden)').forEach(modal => {
                closeModal(modal.id);
            });
        }
    });
}

// Export functions for use in other modules
export { openModal, closeModal, setupModalClickHandlers, initializeModals }; 