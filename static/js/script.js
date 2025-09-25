// Custom JavaScript for PPT AI Analyzer

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Color swatch interactions
    initializeColorSwatches();
    
    // Upload progress simulation
    initializeUploadProgress();
    
    // Smooth scrolling for anchor links
    initializeSmoothScrolling();
    
    // Initialize charts if on analysis page
    if (document.getElementById('analysisCharts')) {
        initializeCharts();
    }
});

function initializeColorSwatches() {
    const colorSwatches = document.querySelectorAll('.color-swatch, .color-mini-swatch');
    
    colorSwatches.forEach(function(swatch) {
        // Add click to copy functionality
        swatch.addEventListener('click', function() {
            const color = this.getAttribute('data-color') || 
                         this.getAttribute('title') || 
                         this.style.backgroundColor;
            
            if (color && color.startsWith('#')) {
                copyToClipboard(color, this);
            }
        });
        
        // Add hover effects
        swatch.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.1)';
            this.style.zIndex = '10';
        });
        
        swatch.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
            this.style.zIndex = '1';
        });
    });
}

function copyToClipboard(text, element) {
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(function() {
            showCopyFeedback(element, 'Copied!');
        }).catch(function() {
            fallbackCopyToClipboard(text, element);
        });
    } else {
        fallbackCopyToClipboard(text, element);
    }
}

function fallbackCopyToClipboard(text, element) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showCopyFeedback(element, 'Copied!');
    } catch (err) {
        showCopyFeedback(element, 'Copy failed');
    }
    
    document.body.removeChild(textArea);
}

function showCopyFeedback(element, message) {
    // Create temporary tooltip
    const feedback = document.createElement('div');
    feedback.className = 'copy-feedback';
    feedback.textContent = message;
    feedback.style.cssText = `
        position: absolute;
        background: #333;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        z-index: 1000;
        pointer-events: none;
        opacity: 0;
        transition: opacity 0.3s ease;
    `;
    
    document.body.appendChild(feedback);
    
    // Position the feedback
    const rect = element.getBoundingClientRect();
    feedback.style.left = (rect.left + rect.width / 2 - feedback.offsetWidth / 2) + 'px';
    feedback.style.top = (rect.top - feedback.offsetHeight - 8) + 'px';
    
    // Show and hide feedback
    setTimeout(() => feedback.style.opacity = '1', 10);
    setTimeout(() => {
        feedback.style.opacity = '0';
        setTimeout(() => document.body.removeChild(feedback), 300);
    }, 1500);
}

function initializeUploadProgress() {
    const uploadForm = document.getElementById('uploadForm');
    const fileInput = document.getElementById('fileInput');
    if (!uploadForm) return;
    
    // File size validation (4MB = 4 * 1024 * 1024 bytes)
    const MAX_FILE_SIZE = 4 * 1024 * 1024;
    
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                if (file.size > MAX_FILE_SIZE) {
                    alert(`File is too large! Maximum size is 4MB. Your file is ${(file.size / (1024 * 1024)).toFixed(2)}MB.`);
                    this.value = '';
                    document.getElementById('uploadBtn').disabled = true;
                    document.getElementById('fileInfo').style.display = 'none';
                    return;
                }
                
                // Show file info
                document.getElementById('fileName').textContent = file.name;
                document.getElementById('fileSize').textContent = `(${(file.size / (1024 * 1024)).toFixed(2)}MB)`;
                document.getElementById('fileInfo').style.display = 'block';
                document.getElementById('uploadBtn').disabled = false;
            }
        });
    }
    
    uploadForm.addEventListener('submit', function(e) {
        const file = fileInput.files[0];
        if (file && file.size > MAX_FILE_SIZE) {
            e.preventDefault();
            alert('File is too large for serverless deployment. Please use a file smaller than 4MB.');
            return false;
        }
        
        const progressBar = document.getElementById('progressBar');
        if (!progressBar) return;
        
        let progress = 0;
        const interval = setInterval(function() {
            progress += Math.random() * 15;
            if (progress > 90) {
                progress = 90;
                clearInterval(interval);
            }
            progressBar.style.width = progress + '%';
            progressBar.setAttribute('aria-valuenow', progress);
        }, 500);
    });
}

function initializeSmoothScrolling() {
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(function(link) {
        link.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                e.preventDefault();
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

function initializeCharts() {
    // Color distribution chart
    createColorDistributionChart();
    
    // Content type chart
    createContentTypeChart();
    
    // Quality scores chart
    createQualityScoresChart();
}

function createColorDistributionChart() {
    const ctx = document.getElementById('colorDistributionChart');
    if (!ctx) return;
    
    // Get color data from the page (this would be passed from the backend)
    const colorData = getColorDataFromPage();
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: colorData.labels,
            datasets: [{
                data: colorData.values,
                backgroundColor: colorData.colors,
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                title: {
                    display: true,
                    text: 'Color Distribution'
                }
            }
        }
    });
}

function createContentTypeChart() {
    const ctx = document.getElementById('contentTypeChart');
    if (!ctx) return;
    
    const contentData = getContentDataFromPage();
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Text Elements', 'Images', 'Shapes', 'Charts'],
            datasets: [{
                label: 'Count',
                data: contentData,
                backgroundColor: [
                    'rgba(54, 162, 235, 0.8)',
                    'rgba(255, 99, 132, 0.8)',
                    'rgba(255, 205, 86, 0.8)',
                    'rgba(75, 192, 192, 0.8)'
                ],
                borderColor: [
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 99, 132, 1)',
                    'rgba(255, 205, 86, 1)',
                    'rgba(75, 192, 192, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Content Distribution'
                }
            }
        }
    });
}

function createQualityScoresChart() {
    const ctx = document.getElementById('qualityScoresChart');
    if (!ctx) return;
    
    const scores = getQualityScoresFromPage();
    
    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Design', 'Content', 'Professional', 'Accessibility', 'Consistency'],
            datasets: [{
                label: 'Quality Scores',
                data: scores,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                pointBorderColor: '#fff',
                pointBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 10,
                    ticks: {
                        stepSize: 2
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Quality Assessment'
                }
            }
        }
    });
}

// Helper functions to extract data from the page
function getColorDataFromPage() {
    // This would extract color data from the DOM
    // For now, return sample data
    return {
        labels: ['Primary', 'Secondary', 'Accent', 'Background'],
        values: [30, 25, 20, 25],
        colors: ['#0d6efd', '#6c757d', '#28a745', '#f8f9fa']
    };
}

function getContentDataFromPage() {
    // Extract content statistics from the DOM
    const textElements = document.querySelectorAll('[data-text-count]').length || 0;
    const images = document.querySelectorAll('[data-image-count]').length || 0;
    const shapes = document.querySelectorAll('[data-shape-count]').length || 0;
    const charts = 0; // Would need to be detected
    
    return [textElements, images, shapes, charts];
}

function getQualityScoresFromPage() {
    // Extract quality scores from the DOM
    const designScore = parseFloat(document.querySelector('[data-design-score]')?.textContent) || 0;
    const contentScore = parseFloat(document.querySelector('[data-content-score]')?.textContent) || 0;
    const professionalScore = parseFloat(document.querySelector('[data-professional-score]')?.textContent) || 0;
    
    return [designScore, contentScore, professionalScore, 7, 8]; // Last two are placeholders
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    }
}

// Export functions for global use
window.PPTAnalyzer = {
    copyToClipboard,
    showCopyFeedback,
    initializeCharts
};
