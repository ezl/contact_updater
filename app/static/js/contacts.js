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
            
            // Update the delete form action in the client_actions component
            const deleteContactForm = contactDetailModal.querySelector('#deleteContactForm');
            if (deleteContactForm) {
                deleteContactForm.action = `/delete_contact/${contactId}`;
            }
            
            // Show the modal first, so the client_actions component is rendered
            openModal('contactDetailModal');
            
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
    if (!birthdayString) return 'Not set';
    
    // Check if the birthday is in MM-DD format
    if (birthdayString.match(/^\d{2}-\d{2}$/)) {
        // Parse MM-DD format
        const [month, day] = birthdayString.split('-');
        const monthInt = parseInt(month);
        const dayInt = parseInt(day);
        
        // Create a date object to get the month name
        const date = new Date(2000, monthInt - 1, dayInt);
        const monthName = date.toLocaleString('en-US', { month: 'short' });
        return `${monthName} ${dayInt}`;
    }
    
    // Try to parse as a full date if not in MM-DD format
    try {
        const date = new Date(birthdayString);
        if (isNaN(date.getTime())) {
            return 'Invalid date';
        }
        const monthName = date.toLocaleString('en-US', { month: 'short' });
        const day = date.getDate();
        return `${monthName} ${day}`;
    } catch (e) {
        console.error('Error formatting birthday:', e);
        return 'Invalid date';
    }
}

// Initialize contact row click events
function initializeContactRows() {
    const contactRows = document.querySelectorAll('.contact-row');
    
    contactRows.forEach(row => {
        row.addEventListener('click', function(e) {
            // Ignore clicks on checkboxes or action buttons
            if (e.target.closest('.contact-checkbox') || e.target.closest('.contact-actions')) {
                return;
            }
            
            const contactId = this.getAttribute('data-contact-id');
            openContactDetailModal(contactId);
        });
    });
}

export { 
    openContactDetailModal, 
    fetchContactDetails, 
    formatDate, 
    formatBirthday, 
    initializeContactRows
}; 