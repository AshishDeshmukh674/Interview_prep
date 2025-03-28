// Common JavaScript functionality for AI Interview Assistant

// Utility function to format numbers as percentages
function formatPercentage(value) {
    return `${Math.round(value * 100)}%`;
}

// Utility function to show notifications
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    const container = document.createElement('div');
    container.style.position = 'fixed';
    container.style.top = '20px';
    container.style.right = '20px';
    container.style.zIndex = '1000';
    container.appendChild(notification);
    
    document.body.appendChild(container);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        container.remove();
    }, 5000);
}

// Utility function to handle API errors
function handleApiError(error, message = 'An error occurred') {
    console.error('API Error:', error);
    showNotification(message, 'danger');
}

// Utility function to validate form inputs
function validateForm(formData) {
    const errors = [];
    
    for (const [key, value] of formData.entries()) {
        if (!value.trim()) {
            errors.push(`${key} is required`);
        }
    }
    
    return errors;
}

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Handle form submissions
document.addEventListener('submit', function(event) {
    const form = event.target;
    if (form.dataset.validate === 'true') {
        const formData = new FormData(form);
        const errors = validateForm(formData);
        
        if (errors.length > 0) {
            event.preventDefault();
            errors.forEach(error => showNotification(error, 'warning'));
        }
    }
});

// Handle file uploads
function handleFileUpload(input, maxSize = 5) {
    const file = input.files[0];
    if (!file) return true;
    
    const sizeInMB = file.size / (1024 * 1024);
    if (sizeInMB > maxSize) {
        showNotification(`File size must be less than ${maxSize}MB`, 'warning');
        input.value = '';
        return false;
    }
    
    return true;
}

// Export utility functions
window.utils = {
    formatPercentage,
    showNotification,
    handleApiError,
    validateForm,
    handleFileUpload
}; 