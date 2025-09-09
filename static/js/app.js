// Main JavaScript for Bubble Drawing Tool Web App

// Utility functions
function showElement(elementId) {
    document.getElementById(elementId).style.display = 'block';
}

function hideElement(elementId) {
    document.getElementById(elementId).style.display = 'none';
}

function setElementText(elementId, text) {
    document.getElementById(elementId).textContent = text;
}

// File upload validation
function validateFile(file) {
    const maxSize = 16 * 1024 * 1024; // 16MB
    const allowedTypes = ['application/pdf'];
    
    if (!file) {
        return { valid: false, message: 'Please select a file.' };
    }
    
    if (!allowedTypes.includes(file.type)) {
        return { valid: false, message: 'Only PDF files are allowed.' };
    }
    
    if (file.size > maxSize) {
        return { valid: false, message: 'File size must be less than 16MB.' };
    }
    
    return { valid: true };
}

// Format file size for display
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Show file info when selected
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('fileInput');
    
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            const validation = validateFile(file);
            
            if (file) {
                const fileInfo = document.createElement('div');
                fileInfo.className = 'mt-2 small text-muted';
                fileInfo.innerHTML = `
                    <i class="fas fa-file-pdf me-1"></i>
                    ${file.name} (${formatFileSize(file.size)})
                `;
                
                // Remove any existing file info
                const existingInfo = fileInput.parentNode.querySelector('.file-info');
                if (existingInfo) {
                    existingInfo.remove();
                }
                
                fileInfo.className += ' file-info';
                fileInput.parentNode.appendChild(fileInfo);
                
                if (!validation.valid) {
                    fileInfo.className += ' text-danger';
                    fileInfo.innerHTML = `
                        <i class="fas fa-exclamation-triangle me-1"></i>
                        ${validation.message}
                    `;
                }
            }
        });
    }
});

// Add smooth scrolling to anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add loading animation to buttons when clicked
document.addEventListener('click', function(e) {
    if (e.target.matches('button[type="submit"], .btn-primary, .btn-success')) {
        const button = e.target;
        const originalText = button.innerHTML;
        
        // Don't add loading if already disabled
        if (button.disabled) return;
        
        // Add loading state after a short delay to allow form validation
        setTimeout(() => {
            if (button.disabled) {
                button.innerHTML = `
                    <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    Processing...
                `;
            }
        }, 100);
    }
});

// Auto-hide alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert:not(.alert-info):not(.alert-warning)');
    alerts.forEach(alert => {
        if (alert.classList.contains('alert-success')) {
            setTimeout(() => {
                alert.style.opacity = '0';
                setTimeout(() => {
                    alert.style.display = 'none';
                }, 300);
            }, 5000);
        }
    });
});

// Add tooltips to elements with title attributes
document.addEventListener('DOMContentLoaded', function() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Progress tracking for long operations
function trackProgress(jobId, callback) {
    const checkStatus = () => {
        fetch(`/status/${jobId}`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'completed') {
                    callback(null, data);
                } else if (data.status === 'processing') {
                    setTimeout(checkStatus, 2000); // Check again in 2 seconds
                } else {
                    callback(new Error('Job not found'), null);
                }
            })
            .catch(error => {
                callback(error, null);
            });
    };
    
    checkStatus();
}

// Error handling for network requests
function handleNetworkError(error) {
    console.error('Network error:', error);
    
    let message = 'A network error occurred. Please check your connection and try again.';
    
    if (error.message.includes('Failed to fetch')) {
        message = 'Unable to connect to the server. Please check your internet connection.';
    } else if (error.message.includes('timeout')) {
        message = 'The request timed out. Please try again.';
    }
    
    return message;
}

// Copy text to clipboard
function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
        return navigator.clipboard.writeText(text);
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        return new Promise((resolve, reject) => {
            if (document.execCommand('copy')) {
                resolve();
            } else {
                reject();
            }
            textArea.remove();
        });
    }
}

