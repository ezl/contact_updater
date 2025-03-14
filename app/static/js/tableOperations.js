/**
 * Table Operations Module
 * Handles search filtering, table sorting, and other table-related operations
 */

// Initialize search functionality
function initializeSearch() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const rows = document.querySelectorAll('.contact-row');
            
            rows.forEach(row => {
                const name = row.querySelector('td:nth-child(1)').textContent.toLowerCase();
                const cell = row.querySelector('td:nth-child(2)').textContent.toLowerCase();
                const email = row.querySelector('td:nth-child(3)').textContent.toLowerCase();
                const notes = row.querySelector('td:nth-child(5)') ? row.querySelector('td:nth-child(5)').textContent.toLowerCase() : '';
                
                if (name.includes(searchTerm) || cell.includes(searchTerm) || email.includes(searchTerm) || notes.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }
}

// Initialize table sorting functionality
function initializeTableSorting() {
    const sortableHeaders = document.querySelectorAll('.sortable-header');
    let currentSort = { column: null, direction: 'asc' };
    
    sortableHeaders.forEach(header => {
        header.addEventListener('click', function() {
            const column = this.getAttribute('data-sort');
            const direction = currentSort.column === column && currentSort.direction === 'asc' ? 'desc' : 'asc';
            
            // Update sort icons
            document.querySelectorAll('.sort-icon i').forEach(icon => {
                icon.className = 'fas fa-sort text-gray-400';
            });
            
            const sortIcon = this.querySelector('.sort-icon i');
            sortIcon.className = `fas fa-sort-${direction === 'asc' ? 'up' : 'down'} text-forest-green`;
            
            // Sort the table
            const tbody = document.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            
            rows.sort((a, b) => {
                let aValue, bValue;
                
                if (column === 'name') {
                    aValue = a.querySelector('td:nth-child(1)').textContent.trim().toLowerCase();
                    bValue = b.querySelector('td:nth-child(1)').textContent.trim().toLowerCase();
                } else if (column === 'birthday') {
                    const aText = a.querySelector('td:nth-child(5)').textContent.trim();
                    const bText = b.querySelector('td:nth-child(5)').textContent.trim();
                    
                    // Handle empty values
                    if (aText === '-') aValue = 'z'; // Sort empty values to the end
                    if (bText === '-') bValue = 'z';
                    
                    // If both values are valid dates
                    if (aText !== '-' && bText !== '-') {
                        // Parse the "MMM D" format (e.g., "Jan 5")
                        const aParts = aText.split(' ');
                        const bParts = bText.split(' ');
                        
                        const aMonth = getMonthNumber(aParts[0]);
                        const aDay = parseInt(aParts[1]);
                        
                        const bMonth = getMonthNumber(bParts[0]);
                        const bDay = parseInt(bParts[1]);
                        
                        // Compare months first, then days
                        if (aMonth !== bMonth) {
                            aValue = aMonth;
                            bValue = bMonth;
                        } else {
                            aValue = aDay;
                            bValue = bDay;
                        }
                    } else {
                        aValue = aText;
                        bValue = bText;
                    }
                }
                
                if (direction === 'asc') {
                    return aValue > bValue ? 1 : -1;
                } else {
                    return aValue < bValue ? 1 : -1;
                }
            });
            
            // Re-append rows in the new order
            rows.forEach(row => tbody.appendChild(row));
            
            // Update current sort
            currentSort = { column, direction };
        });
    });
}

// Helper function to convert month name to number
function getMonthNumber(monthName) {
    if (!monthName) return 0;
    
    const months = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
        'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12,
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'jun': 6,
        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
    };
    return months[monthName.toLowerCase()] || 0;
}

// Initialize close alert buttons
function initializeAlerts() {
    const closeAlertButtons = document.querySelectorAll('.close-alert');
    closeAlertButtons.forEach(button => {
        button.addEventListener('click', function() {
            this.parentElement.style.display = 'none';
        });
    });
}

export { 
    initializeSearch, 
    initializeTableSorting, 
    getMonthNumber,
    initializeAlerts
}; 