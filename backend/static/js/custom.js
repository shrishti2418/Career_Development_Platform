// Custom JavaScript for AI Resume Detection
console.log('AI Resume Detection loaded');

// DOM Content Loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all functionality
    initSmoothScrolling();
    initScrollAnimations();
    initFileUpload();
    initFormValidation();
    initNavbarEffects();
});

// Smooth Scrolling for Navigation Links
function initSmoothScrolling() {
    const links = document.querySelectorAll('a[href^="#"]');

    links.forEach(link => {
        link.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);

            if (targetElement) {
                e.preventDefault();

                const headerOffset = 80;
                const elementPosition = targetElement.offsetTop;
                const offsetPosition = elementPosition - headerOffset;

                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Scroll Animations using Intersection Observer
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate__animated');

                // Add specific animation classes based on element
                if (entry.target.classList.contains('feature-card')) {
                    entry.target.classList.add('animate__fadeInUp');
                } else if (entry.target.classList.contains('stat-card')) {
                    entry.target.classList.add('animate__fadeInUp');
                }
            }
        });
    }, observerOptions);

    // Observe elements for animation
    const animateElements = document.querySelectorAll('.feature-card, .stat-card');
    animateElements.forEach(el => observer.observe(el));
}

// Enhanced File Upload with Drag & Drop
function initFileUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('resumeInput');
    const uploadLink = document.querySelector('.upload-link');

    if (!uploadArea || !fileInput) return;

    // Click to browse files
    uploadLink.addEventListener('click', () => {
        fileInput.click();
    });

    // Drag and drop functionality
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, unhighlight, false);
    });

    function highlight(e) {
        uploadArea.classList.add('dragover');
    }

    function unhighlight(e) {
        uploadArea.classList.remove('dragover');
    }

    uploadArea.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;

        if (files.length > 0) {
            fileInput.files = files;
            updateUploadArea(files[0]);
        }
    }

    // File input change
    fileInput.addEventListener('change', function(e) {
        if (this.files.length > 0) {
            updateUploadArea(this.files[0]);
        }
    });

    function updateUploadArea(file) {
        const fileName = file.name;
        const fileSize = (file.size / 1024 / 1024).toFixed(2); // MB

        uploadArea.innerHTML = `
            <i class="fas fa-file-alt upload-icon" style="color: #667eea;"></i>
            <p class="upload-text">Selected: <strong>${fileName}</strong></p>
            <p class="upload-text">Size: ${fileSize} MB</p>
        `;
    }
}

// Form Validation and Enhancement
function initFormValidation() {
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');

            if (submitBtn) {
                submitBtn.innerHTML = '<span class="spinner"></span> Processing...';
                submitBtn.classList.add('loading');
            }
        });
    });
}

// Navbar Effects
function initNavbarEffects() {
    const navbar = document.querySelector('.navbar');

    if (!navbar) return;

    // Add background on scroll
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('navbar-scrolled');
        } else {
            navbar.classList.remove('navbar-scrolled');
        }
    });

    // Mobile menu toggle
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');

    if (navbarToggler && navbarCollapse) {
        navbarToggler.addEventListener('click', () => {
            navbarCollapse.classList.toggle('show');
        });
    }
}

// Utility Functions
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

// Performance optimization: Lazy load images
function initLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');

    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });

        images.forEach(img => imageObserver.observe(img));
    } else {
        // Fallback for browsers without IntersectionObserver
        images.forEach(img => {
            img.src = img.dataset.src;
        });
    }
}

// Initialize lazy loading
initLazyLoading();

// Add loading states for better UX
function showLoading(element) {
    element.classList.add('loading');
}

function hideLoading(element) {
    element.classList.remove('loading');
}

// Error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
});

// Service Worker registration (if needed for PWA features)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // Register service worker for caching and offline functionality
        // navigator.serviceWorker.register('/sw.js');
    });
}
