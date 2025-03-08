/**
 * Main JavaScript Module
 * Initializes all modules and sets up the application
 */

import { initializeModals, openModal, closeModal } from './modals.js';
import { initializeContactRows, formatDate, formatBirthday } from './contacts.js';
import { setupEditableFields } from './editableFields.js';
import { initializeSearch, initializeTableSorting, initializeAlerts } from './tableOperations.js';
import { initializeFileUpload } from './fileUpload.js';
import { initializeBulkActions } from './bulkActions.js';
import { initializeKebabMenu, initializeActionButtons, initializeFlatpickrCloseButton } from './uiUtils.js';
import { initializeDeleteContact } from './deleteContact.js';
import { initializeEmailCampaigns } from './emailCampaigns.js';

// Make certain functions available globally
window.openModal = openModal;
window.closeModal = closeModal;
window.formatDate = formatDate;
window.formatBirthday = formatBirthday;
window.setupEditableFields = setupEditableFields;

// Initialize everything when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing dashboard.js modules...');
    
    // Initialize modals
    initializeModals();
    
    // Initialize contact rows
    initializeContactRows();
    
    // Initialize search functionality
    initializeSearch();
    
    // Initialize table sorting
    initializeTableSorting();
    
    // Initialize alerts
    initializeAlerts();
    
    // Initialize file upload
    initializeFileUpload();
    
    // Initialize bulk actions
    initializeBulkActions();
    
    // Initialize kebab menu
    initializeKebabMenu();
    
    // Initialize action buttons
    initializeActionButtons();
    
    // Initialize flatpickr close button
    initializeFlatpickrCloseButton();
    
    // Initialize delete contact functionality
    initializeDeleteContact();
    
    // Initialize email campaigns
    initializeEmailCampaigns();
    
    console.log('All dashboard.js modules initialized successfully.');
}); 