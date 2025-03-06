/**
 * Editable Fields Module
 * Handles making fields editable, saving changes, and displaying success messages
 */

import { formatDate } from './contacts.js';

// Setup editable fields in the modal
function setupEditableFields() {
    console.log('Setting up editable fields');
    const editableFields = document.querySelectorAll('#contactDetailModal .modal-value[data-field]');
    
    editableFields.forEach(field => {
        // Skip fields that shouldn't be editable
        const fieldName = field.getAttribute('data-field');
        if (!fieldName || fieldName === 'date_added' || fieldName === 'email_updated' || fieldName === 'cell_updated') {
            return;
        }
        
        console.log('Adding click listener to field:', fieldName);
        
        // Remove any existing listeners by cloning and replacing
        const newField = field.cloneNode(true);
        field.parentNode.replaceChild(newField, field);
        
        // Add the click event listener to the new field
        newField.addEventListener('click', function(e) {
            console.log('Field clicked:', fieldName);
            if (!this.classList.contains('editing')) {
                makeFieldEditable(this);
            }
        });
    });
}

// Make a field editable
function makeFieldEditable(field) {
    const fieldName = field.getAttribute('data-field');
    const currentValue = field.textContent;
    const contactDetailModal = document.getElementById('contactDetailModal');
    const contactId = contactDetailModal.getAttribute('data-contact-id');
    
    // Store original value for potential cancellation
    field.setAttribute('data-original-value', currentValue);
    
    // Create input element based on field type
    let inputElement;
    let flatpickrInstance = null;
    
    if (fieldName === 'notes') {
        inputElement = document.createElement('textarea');
        inputElement.rows = 3;
    } else if (fieldName === 'birthday') {
        inputElement = document.createElement('input');
        inputElement.type = 'text';
        inputElement.placeholder = 'MMM DD (e.g. Jan 15)';
        inputElement.className = 'w-full p-2 border border-gray-200 rounded-md focus:ring-2 focus:ring-forest-green focus:border-forest-green';
        
        // Add datepicker immediately
        if (typeof flatpickr !== 'undefined') {
            // Add the input to DOM first so flatpickr can find it
            field.innerHTML = '';
            field.appendChild(inputElement);
            
            // Initialize flatpickr
            flatpickrInstance = flatpickr(inputElement, {
                dateFormat: "M d",
                defaultDate: currentValue,
                allowInput: true,
                monthSelectorType: "static",
                disableMobile: true,
                onOpen: function() {
                    // Lock scrolling when calendar opens
                    document.body.style.overflow = 'hidden';
                    
                    // Add custom close button
                    setTimeout(() => {
                        const calendar = document.querySelector('.flatpickr-calendar.open');
                        if (calendar && !calendar.querySelector('.flatpickr-close-button')) {
                            const closeBtn = document.createElement('button');
                            closeBtn.className = 'flatpickr-close-button';
                            closeBtn.innerHTML = '×';
                            closeBtn.addEventListener('click', function(e) {
                                e.preventDefault();
                                e.stopPropagation();
                                if (flatpickrInstance) {
                                    flatpickrInstance.close();
                                    // Force close by hiding the calendar
                                    const calendar = document.querySelector('.flatpickr-calendar');
                                    if (calendar) {
                                        calendar.style.display = 'none';
                                    }
                                }
                            });
                            calendar.appendChild(closeBtn);
                        }
                    }, 0);
                },
                onClose: function(selectedDates, dateStr) {
                    // Unlock scrolling when calendar closes
                    document.body.style.overflow = '';
                    
                    if (dateStr) {
                        // Automatically save when a date is selected
                        saveFieldEdit(field, dateStr, fieldName, contactId);
                    }
                    
                    // Force close by hiding the calendar
                    setTimeout(() => {
                        const calendar = document.querySelector('.flatpickr-calendar');
                        if (calendar) {
                            calendar.style.display = 'none';
                        }
                    }, 0);
                },
                onChange: function(selectedDates, dateStr) {
                    if (dateStr) {
                        // Close the calendar after selecting a date
                        setTimeout(() => {
                            if (flatpickrInstance) {
                                flatpickrInstance.close();
                            }
                        }, 100);
                    }
                }
            });
            
            // Open the calendar immediately
            setTimeout(() => {
                flatpickrInstance.open();
            }, 50);
        }
    } else {
        inputElement = document.createElement('input');
        inputElement.type = fieldName.includes('email') ? 'email' : 'text';
    }
    
    // Set input value and styling
    inputElement.value = currentValue;
    if (fieldName !== 'birthday') { // Already set for birthday above
        inputElement.className = 'w-full p-2 border border-gray-200 rounded-md focus:ring-2 focus:ring-forest-green focus:border-forest-green';
    }
    
    // Create save and cancel buttons
    const actionsDiv = document.createElement('div');
    actionsDiv.className = 'edit-actions';
    
    const saveButton = document.createElement('button');
    saveButton.textContent = 'Save';
    saveButton.className = 'edit-save-btn';
    
    const cancelButton = document.createElement('button');
    cancelButton.textContent = 'Cancel';
    cancelButton.className = 'edit-cancel-btn';
    
    // Add event listeners
    saveButton.addEventListener('click', function() {
        if (flatpickrInstance) {
            flatpickrInstance.close();
        }
        saveFieldEdit(field, inputElement.value, fieldName, contactId);
    });
    
    cancelButton.addEventListener('click', function(e) {
        e.stopPropagation(); // Prevent event bubbling
        if (flatpickrInstance) {
            flatpickrInstance.close();
        }
        cancelFieldEdit(field, currentValue);
    });
    
    // Add blur event to exit edit mode when clicking outside
    inputElement.addEventListener('blur', function(e) {
        // Don't cancel if the related target is the flatpickr calendar or the save/cancel buttons
        if (e.relatedTarget && 
            (e.relatedTarget.classList.contains('flatpickr-day') || 
             e.relatedTarget.classList.contains('flatpickr-month') ||
             e.relatedTarget.classList.contains('flatpickr-monthDropdown-month') ||
             e.relatedTarget.classList.contains('flatpickr-close-button') ||
             e.relatedTarget === saveButton || 
             e.relatedTarget === cancelButton)) {
            return;
        }
        
        // Also don't cancel if we're clicking inside the flatpickr calendar
        if (e.relatedTarget && e.relatedTarget.closest('.flatpickr-calendar')) {
            return;
        }
        
        // For birthday field, only cancel if we're clicking outside the flatpickr
        if (fieldName === 'birthday') {
            // Check if flatpickr is open
            const flatpickrCalendar = document.querySelector('.flatpickr-calendar.open');
            if (flatpickrCalendar) {
                // Don't cancel if the flatpickr is open
                return;
            }
        }
        
        cancelFieldEdit(field, currentValue);
    });
    
    // Add keydown event to handle ESC key and Enter key
    inputElement.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            e.stopPropagation(); // Prevent modal from closing
            if (flatpickrInstance) {
                flatpickrInstance.close();
            }
            cancelFieldEdit(field, currentValue);
        } else if (e.key === 'Enter') {
            // For regular inputs, submit on Enter
            if (inputElement.tagName.toLowerCase() !== 'textarea' || (e.metaKey || e.ctrlKey)) {
                e.preventDefault(); // Prevent default behavior (newline in textarea)
                if (flatpickrInstance) {
                    flatpickrInstance.close();
                }
                saveFieldEdit(field, inputElement.value, fieldName, contactId);
            }
        }
    });
    
    // Add elements to the DOM
    actionsDiv.appendChild(saveButton);
    actionsDiv.appendChild(cancelButton);
    
    // Only append to DOM if not already done for birthday
    if (fieldName !== 'birthday') {
        field.innerHTML = '';
        field.appendChild(inputElement);
    }
    
    field.appendChild(actionsDiv);
    field.classList.add('editing');
    
    // Focus the input
    inputElement.focus();
}

// Save field edit
function saveFieldEdit(field, newValue, fieldName, contactId) {
    console.log('Saving field edit:', fieldName, newValue, 'for contact:', contactId);
    
    // Get CSRF token
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    
    // Prepare data for the API call
    const data = {
        field: fieldName,
        value: newValue
    };
    
    console.log('Sending data to server:', data);
    
    // Make API call to update the contact
    fetch(`/update_contact/${contactId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        console.log('Update response status:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('Update response data:', data);
        if (data.success) {
            // Format the display value if needed
            let displayValue = newValue;
            
            // Format birthday if it has a specific format
            if (fieldName === 'birthday' && newValue) {
                try {
                    // Try to parse and format the date
                    const dateParts = newValue.split(/[\/\-\s]/);
                    if (dateParts.length >= 2) {
                        const month = isNaN(dateParts[0]) ? dateParts[0] : new Date(2000, parseInt(dateParts[0])-1, 1).toLocaleString('default', { month: 'short' });
                        const day = dateParts[1];
                        displayValue = `${month} ${day}`;
                    }
                } catch (e) {
                    console.error('Error formatting date:', e);
                }
            }
            
            // Update the field with the new value
            field.textContent = displayValue;
            field.classList.remove('editing');
            
            // Update timestamp display if provided in the response
            if (data.updated_timestamp && data.updated_field) {
                const formattedDate = formatDate(data.updated_timestamp);
                const updatedText = `Updated: ${formattedDate}`;
                
                if (data.updated_field === 'email') {
                    document.getElementById('detailEmailUpdated').textContent = updatedText;
                } else if (data.updated_field === 'cell') {
                    document.getElementById('detailCellUpdated').textContent = updatedText;
                } else if (data.updated_field === 'mailing_address') {
                    document.getElementById('detailAddressUpdated').textContent = updatedText;
                }
            }
            
            // Show success indicator
            const successIndicator = field.closest('.modal-field').querySelector('.success-indicator');
            if (successIndicator) {
                successIndicator.classList.remove('hidden');
                successIndicator.style.opacity = '1';
                setTimeout(() => {
                    successIndicator.style.opacity = '0';
                    setTimeout(() => {
                        successIndicator.classList.add('hidden');
                    }, 300);
                }, 2000);
            }
            
            // Also update the row in the table if visible
            updateTableRow(contactId, fieldName, displayValue);
            
            // Update contact name in modal header if name was changed
            if (fieldName === 'name') {
                document.getElementById('contactName').textContent = displayValue;
                document.getElementById('contactInitial').textContent = displayValue ? displayValue[0].toUpperCase() : '';
            }
        } else {
            // Show error and revert to original value
            alert('Error updating contact: ' + data.message);
            field.textContent = field.getAttribute('data-original-value') || '';
            field.classList.remove('editing');
        }
    })
    .catch(error => {
        console.error('Error updating contact:', error);
        field.textContent = field.getAttribute('data-original-value') || '';
        field.classList.remove('editing');
    });
}

// Cancel field edit
function cancelFieldEdit(field, originalValue) {
    field.textContent = originalValue || field.getAttribute('data-original-value') || '';
    field.classList.remove('editing');
}

// Update table row after edit
function updateTableRow(contactId, fieldName, newValue) {
    const row = document.querySelector(`.contact-row[data-contact-id="${contactId}"]`);
    if (!row) return;
    
    if (fieldName === 'name') {
        const nameElement = row.querySelector('.text-sm.font-medium');
        if (nameElement) nameElement.textContent = newValue;
        
        const initialElement = row.querySelector('.text-forest-green.font-semibold');
        if (initialElement) initialElement.textContent = newValue ? newValue[0].toUpperCase() : '';
    }
    
    if (fieldName === 'cell') {
        const cellElement = row.querySelector('td:nth-child(2) .hidden.md\\:inline');
        if (cellElement) cellElement.textContent = newValue || '-';
        
        const cellLink = row.querySelector('td:nth-child(2) a');
        if (cellLink) {
            if (newValue) {
                cellLink.href = `tel:${newValue}`;
                cellLink.classList.remove('text-gray-300');
                cellLink.classList.add('text-forest-green');
            } else {
                cellLink.removeAttribute('href');
                cellLink.classList.remove('text-forest-green');
                cellLink.classList.add('text-gray-300');
            }
        }
    }
    
    if (fieldName === 'email') {
        const emailElement = row.querySelector('td:nth-child(3) .hidden.md\\:inline');
        if (emailElement) emailElement.textContent = newValue || '-';
        
        const emailLink = row.querySelector('td:nth-child(3) a');
        if (emailLink) {
            if (newValue) {
                emailLink.href = `mailto:${newValue}`;
                emailLink.classList.remove('text-gray-300');
                emailLink.classList.add('text-forest-green');
            } else {
                emailLink.removeAttribute('href');
                emailLink.classList.remove('text-forest-green');
                emailLink.classList.add('text-gray-300');
            }
        }
    }
    
    if (fieldName === 'birthday') {
        const birthdayElement = row.querySelector('td:nth-child(4) .text-sm');
        if (birthdayElement) birthdayElement.textContent = newValue || '-';
    }
    
    if (fieldName === 'notes') {
        const notesElement = row.querySelector('td:nth-child(5) .text-sm');
        if (notesElement) notesElement.textContent = newValue || '-';
    }
}

export { setupEditableFields, makeFieldEditable, saveFieldEdit, cancelFieldEdit, updateTableRow }; 