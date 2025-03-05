/**
 * Contacts Management Module
 * Handles fetching, displaying, and formatting contact details
 */

import { openModal } from './modals.js';

// Function to open contact detail modal
function openContactDetailModal(contactId) {
    fetchContactDetails(contactId);
}

// Function to fetch contact details
function fetchContactDetails(contactId) {
    console.log('Fetching contact details for ID:', contactId);
    fetch(`/get_contact/${contactId}`)
        .then(response => response.json())
        .then(data => {
            // Populate the modal with contact data
            document.getElementById('contactName').textContent = data.name || '';
            document.getElementById('contactInitial').textContent = data.name ? data.name[0].toUpperCase() : '';
            
            // Store the contact ID for editing
            const contactDetailModal = document.getElementById('contactDetailModal');
            contactDetailModal.setAttribute('data-contact-id', contactId);
            
            // Show the modal first, so the client_actions component is rendered
            openModal('contactDetailModal');
            
            // Set the delete form action - do this after modal is opened
            setTimeout(() => {
                const deleteForm = document.getElementById('deleteContactForm');
                if (deleteForm) {
                    deleteForm.action = `/delete_contact/${contactId}`;
                    console.log('Delete form action set to:', deleteForm.action);
                    
                    // Add a direct event listener to the delete button
                    const deleteButton = deleteForm.querySelector('button[type="submit"]');
                    if (deleteButton) {
                        // Remove any existing listeners
                        const newDeleteButton = deleteButton.cloneNode(true);
                        deleteButton.parentNode.replaceChild(newDeleteButton, deleteButton);
                        
                        // Add new listener
                        newDeleteButton.addEventListener('click', function(e) {
                            if (!confirm('Are you sure you want to delete this contact?')) {
                                e.preventDefault();
                            }
                            // Let the form submit normally to get the redirect with undo parameters
                        });
                    } else {
                        console.error('Delete button not found in the form');
                    }
                } else {
                    console.error('Delete form not found in the modal');
                }
            }, 100); // Short delay to ensure modal is fully rendered
            
            // Populate all fields - wrap in try/catch to handle missing elements
            try {
                document.getElementById('detailName').textContent = data.name || '';
                document.getElementById('detailCell').textContent = data.cell || '';
                document.getElementById('detailEmail').textContent = data.email || '';
                document.getElementById('detailAddress').textContent = data.mailing_address || '';
                document.getElementById('detailNotes').textContent = data.notes || '';
                
                // Format date fields - these are not editable
                document.getElementById('detailDateAdded').textContent = formatDate(data.dateAdded) || '';
                document.getElementById('dateAddedDisplay').textContent = formatDate(data.dateAdded) || '';
                
                // Format birthday in MMM DD format
                document.getElementById('detailBirthday').textContent = formatBirthday(data.birthday) || '';
                
                // Format and display last updated dates as help text
                const emailUpdatedText = data.email_updated ? `Updated: ${formatDate(data.email_updated)}` : '';
                document.getElementById('detailEmailUpdated').textContent = emailUpdatedText;
                
                const cellUpdatedText = data.cell_updated ? `Updated: ${formatDate(data.cell_updated)}` : '';
                document.getElementById('detailCellUpdated').textContent = cellUpdatedText;
                
                const addressUpdatedText = data.mailing_address_updated ? `Updated: ${formatDate(data.mailing_address_updated)}` : '';
                document.getElementById('detailAddressUpdated').textContent = addressUpdatedText;
                
                document.getElementById('detailFacebook').textContent = data.facebook || '';
                document.getElementById('detailInstagram').textContent = data.instagram || '';
                document.getElementById('detailTwitter').textContent = data.twitter || '';
            } catch (error) {
                console.error('Error populating modal fields:', error);
            }
        })
        .catch(error => {
            console.error('Error fetching contact details:', error);
        });
}

// Format date for display
function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    
    // Format: Month Day, Year at Hour:Minute AM/PM
    const options = { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    
    return date.toLocaleString(undefined, options);
}

// Format birthday for display (MMM DD format)
function formatBirthday(birthdayString) {
    if (!birthdayString) return '';
    
    // The server will handle the formatting via the format_date filter
    // This function is kept for backward compatibility
    return birthdayString;
}

// Initialize contact row click events
function initializeContactRows() {
    const contactRows = document.querySelectorAll('.contact-row');
    contactRows.forEach(row => {
        row.addEventListener('click', function(e) {
            // Skip if the click was on or inside a checkbox
            if (e.target.closest('.contact-checkbox') || e.target.classList.contains('contact-checkbox')) {
                return;
            }
            
            const contactId = this.getAttribute('data-contact-id');
            openContactDetailModal(contactId);
        });
    });
}

// Initialize single client action buttons
function initializeSingleClientActions() {
    // Set up single client action button event listeners in the contact detail modal
    document.getElementById('singleConfirmAddress')?.addEventListener('click', function() {
        const contactId = document.getElementById('deleteContactForm')?.action.split('/').pop();
        console.log('Request address confirmation for client:', contactId);
    });
    
    document.getElementById('singleEnrichData')?.addEventListener('click', function() {
        const contactId = document.getElementById('deleteContactForm')?.action.split('/').pop();
        console.log('Enrich data for client:', contactId);
    });
    
    document.getElementById('singleSendGift')?.addEventListener('click', function() {
        const contactId = document.getElementById('deleteContactForm')?.action.split('/').pop();
        console.log('Send gift to client:', contactId);
    });
    
    document.getElementById('singleSendMessage')?.addEventListener('click', function() {
        const contactId = document.getElementById('deleteContactForm')?.action.split('/').pop();
        console.log('Send message to client:', contactId);
    });
}

export { 
    openContactDetailModal, 
    fetchContactDetails, 
    formatDate, 
    formatBirthday, 
    initializeContactRows,
    initializeSingleClientActions
}; 