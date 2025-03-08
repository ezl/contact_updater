/**
 * Email Campaigns Module
 * Handles email campaign functionality
 */

// Initialize email campaign functionality
function initializeEmailCampaigns() {
    // Set up the Send Email button in bulk actions
    setupSendEmailButton();
    
    // Initialize rich text editor if on compose page
    initializeRichTextEditor();
    
    // Set up recipient list functionality if on compose page
    setupRecipientList();
}

// Set up the Send Email button in bulk actions
function setupSendEmailButton() {
    const sendEmailBtn = document.getElementById('bulkSendEmail');
    if (sendEmailBtn) {
        sendEmailBtn.addEventListener('click', function() {
            const selectedIds = getSelectedContactIds();
            
            if (selectedIds.length === 0) {
                alert('No contacts selected for email campaign.');
                return;
            }
            
            // Send selected contact IDs to server
            fetch('/email-campaigns/select-contacts', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || ''
                },
                body: JSON.stringify({
                    contact_ids: selectedIds
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success' && data.redirect) {
                    window.location.href = data.redirect;
                } else {
                    alert(data.message || 'Error selecting contacts for email campaign.');
                }
            })
            .catch(error => {
                console.error('Error selecting contacts:', error);
                alert('Error selecting contacts for email campaign.');
            });
        });
    }
}

// Initialize rich text editor on compose page
function initializeRichTextEditor() {
    const editorContainer = document.getElementById('email-body-editor');
    if (!editorContainer) return;
    
    // Simple rich text controls
    const controls = document.getElementById('rich-text-controls');
    if (controls) {
        // Bold button
        const boldBtn = controls.querySelector('.bold-btn');
        if (boldBtn) {
            boldBtn.addEventListener('click', function() {
                document.execCommand('bold', false, null);
                editorContainer.focus();
            });
        }
        
        // Italic button
        const italicBtn = controls.querySelector('.italic-btn');
        if (italicBtn) {
            italicBtn.addEventListener('click', function() {
                document.execCommand('italic', false, null);
                editorContainer.focus();
            });
        }
        
        // Underline button
        const underlineBtn = controls.querySelector('.underline-btn');
        if (underlineBtn) {
            underlineBtn.addEventListener('click', function() {
                document.execCommand('underline', false, null);
                editorContainer.focus();
            });
        }
        
        // Link button
        const linkBtn = controls.querySelector('.link-btn');
        if (linkBtn) {
            linkBtn.addEventListener('click', function() {
                const url = prompt('Enter URL:');
                if (url) {
                    document.execCommand('createLink', false, url);
                }
                editorContainer.focus();
            });
        }
    }
    
    // Update hidden input with HTML content when form is submitted
    const form = editorContainer.closest('form');
    if (form) {
        form.addEventListener('submit', function() {
            const hiddenInput = document.getElementById('body');
            if (hiddenInput) {
                hiddenInput.value = editorContainer.innerHTML;
            }
        });
    }
    
    // Make editor container editable
    editorContainer.contentEditable = true;
    editorContainer.focus();
}

// Set up recipient list functionality
function setupRecipientList() {
    const recipientList = document.getElementById('recipient-list');
    if (!recipientList) return;
    
    // Toggle recipient list visibility
    const toggleBtn = document.getElementById('toggle-recipients');
    if (toggleBtn && recipientList) {
        toggleBtn.addEventListener('click', function() {
            recipientList.classList.toggle('hidden');
            
            // Update button text
            if (recipientList.classList.contains('hidden')) {
                toggleBtn.textContent = 'Show Recipients';
            } else {
                toggleBtn.textContent = 'Hide Recipients';
            }
        });
    }
    
    // Remove recipient buttons
    const removeButtons = document.querySelectorAll('.remove-recipient');
    removeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const contactId = this.getAttribute('data-contact-id');
            const listItem = this.closest('li');
            
            if (listItem && contactId) {
                // Remove from DOM
                listItem.remove();
                
                // Update hidden input with remaining contact IDs
                updateContactIds();
                
                // Update recipient count
                updateRecipientCount();
            }
        });
    });
}

// Update hidden input with contact IDs
function updateContactIds() {
    const recipientItems = document.querySelectorAll('#recipient-list li');
    const contactIds = Array.from(recipientItems).map(item => 
        item.getAttribute('data-contact-id')
    ).filter(id => id);
    
    const hiddenInput = document.getElementById('contact_ids');
    if (hiddenInput) {
        hiddenInput.value = JSON.stringify(contactIds);
    }
}

// Update recipient count
function updateRecipientCount() {
    const recipientItems = document.querySelectorAll('#recipient-list li');
    const countElement = document.getElementById('recipient-count');
    
    if (countElement) {
        countElement.textContent = recipientItems.length;
    }
}

// Helper function to get selected contact IDs (from bulkActions.js)
function getSelectedContactIds() {
    if (typeof window.getSelectedContactIds === 'function') {
        return window.getSelectedContactIds();
    }
    
    // Fallback implementation
    return Array.from(document.querySelectorAll('.contact-checkbox:checked'))
        .map(checkbox => checkbox.getAttribute('data-contact-id'));
}

export { initializeEmailCampaigns }; 