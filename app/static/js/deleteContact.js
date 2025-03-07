/**
 * Delete Contact Module
 * Handles the delete contact modal and form submission
 */

// Initialize delete contact functionality
function initializeDeleteContact() {
    // Get the delete button in the contact detail modal
    const deleteContactButtons = document.querySelectorAll('.contact-detail-delete-btn');
    
    deleteContactButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Get the contact ID from the modal
            const contactDetailModal = document.getElementById('contactDetailModal');
            const contactId = contactDetailModal.getAttribute('data-contact-id');
            
            if (!contactId) {
                console.error('No contact ID found');
                return;
            }
            
            // Set up the delete contact modal form
            const deleteContactModalForm = document.getElementById('deleteContactModalForm');
            deleteContactModalForm.action = `/contacts/delete_contact/${contactId}`;
            
            // Close the contact detail modal
            window.closeModal('contactDetailModal');
            
            // Open the delete contact modal
            window.openModal('deleteContactModal');
        });
    });
}

export { initializeDeleteContact }; 