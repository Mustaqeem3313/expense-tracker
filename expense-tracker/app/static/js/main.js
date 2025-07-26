// Main JavaScript file for Expense Tracker

// Function to show/hide custom date range
function toggleCustomDateRange() {
    const period = document.getElementById('period');
    const customRange = document.getElementById('custom-date-range');
    
    if (period && customRange) {
        if (period.value === 'custom') {
            customRange.style.display = 'flex';
        } else {
            customRange.style.display = 'none';
        }
    }
}

// Set default date to today
function setDefaultDate() {
    const today = new Date().toISOString().split('T')[0];
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        if (!input.value) {
            input.value = today;
        }
    });
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Set default dates
    setDefaultDate();
    
    // Handle custom date range toggle
    const periodSelect = document.getElementById('period');
    if (periodSelect) {
        periodSelect.addEventListener('change', toggleCustomDateRange);
    }
    
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 5000);
    });
});

// Utility functions for edit/delete operations
function editExpense(id) {
    // Placeholder for edit functionality
    console.log('Edit expense:', id);
    alert('Edit functionality will be implemented soon');
}

function deleteExpense(id) {
    if (confirm('Are you sure you want to delete this expense?')) {
        // Placeholder for delete functionality
        console.log('Delete expense:', id);
        alert('Delete functionality will be implemented soon');
    }
}

function editIncome(id) {
    // Placeholder for edit functionality
    console.log('Edit income:', id);
    alert('Edit functionality will be implemented soon');
}

function deleteIncome(id) {
    if (confirm('Are you sure you want to delete this income?')) {
        // Placeholder for delete functionality
        console.log('Delete income:', id);
        alert('Delete functionality will be implemented soon');
    }
}

function editInvestment(id) {
    console.log('Edit investment:', id);
    alert('Edit functionality will be implemented soon');
}

function deleteInvestment(id) {
    if (confirm('Are you sure you want to delete this investment?')) {
        console.log('Delete investment:', id);
        alert('Delete functionality will be implemented soon');
    }
}
