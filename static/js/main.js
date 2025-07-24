/**
 * YeuMoney Code Generator Pro - Main JavaScript
 * Professional frontend functionality
 */

class YeuMoneyApp {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeComponents();
        this.checkAPIHealth();
    }

    setupEventListeners() {
        // Global error handler
        window.addEventListener('error', this.handleGlobalError.bind(this));
        
        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', this.handleSmoothScroll.bind(this));
        });

        // Form validation
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', this.handleFormSubmit.bind(this));
        });

        // Auto-dismiss alerts
        this.setupAutoDismissAlerts();
        
        // Keyboard shortcuts
        document.addEventListener('keydown', this.handleKeyboardShortcuts.bind(this));
        
        // Copy to clipboard functionality
        document.addEventListener('click', this.handleCopyClick.bind(this));
    }

    initializeComponents() {
        this.initializeTooltips();
        this.initializeAnimations();
        this.setupThemeToggle();
        this.initializeCounters();
    }

    // API Health Check
    async checkAPIHealth() {
        try {
            const response = await fetch('/api/health');
            const data = await response.json();
            
            this.updateHealthStatus(data.status === 'healthy');
        } catch (error) {
            console.warn('Health check failed:', error);
            this.updateHealthStatus(false);
        }
    }

    updateHealthStatus(isHealthy) {
        const statusElements = document.querySelectorAll('.health-status');
        statusElements.forEach(element => {
            element.className = `health-status ${isHealthy ? 'text-success' : 'text-danger'}`;
            element.innerHTML = isHealthy ? 
                '<i class="fas fa-check-circle"></i> Online' : 
                '<i class="fas fa-exclamation-triangle"></i> Offline';
        });
    }

    // Form Handling
    handleFormSubmit(event) {
        const form = event.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        
        if (submitBtn) {
            this.setButtonLoading(submitBtn, true);
            
            // Reset button after 30 seconds (timeout)
            setTimeout(() => {
                this.setButtonLoading(submitBtn, false);
            }, 30000);
        }
    }

    setButtonLoading(button, isLoading) {
        if (isLoading) {
            button.disabled = true;
            button.dataset.originalText = button.innerHTML;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang xử lý...';
        } else {
            button.disabled = false;
            if (button.dataset.originalText) {
                button.innerHTML = button.dataset.originalText;
            }
        }
    }

    // Alert System
    showAlert(message, type = 'info', duration = 5000) {
        const alertContainer = this.getOrCreateAlertContainer();
        const alertId = 'alert-' + Date.now();
        
        const alertHTML = `
            <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show animate-fadeInDown" role="alert">
                <i class="fas fa-${this.getAlertIcon(type)} me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        alertContainer.insertAdjacentHTML('beforeend', alertHTML);
        
        // Auto dismiss
        if (duration > 0) {
            setTimeout(() => {
                const alert = document.getElementById(alertId);
                if (alert) {
                    alert.remove();
                }
            }, duration);
        }
    }

    getOrCreateAlertContainer() {
        let container = document.getElementById('alert-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'alert-container';
            container.className = 'position-fixed top-0 end-0 p-3';
            container.style.zIndex = '9999';
            container.style.maxWidth = '400px';
            document.body.appendChild(container);
        }
        return container;
    }

    getAlertIcon(type) {
        const icons = {
            'success': 'check-circle',
            'danger': 'exclamation-triangle',
            'warning': 'exclamation-circle',
            'info': 'info-circle',
            'error': 'exclamation-triangle'
        };
        return icons[type] || 'info-circle';
    }

    setupAutoDismissAlerts() {
        document.querySelectorAll('.alert').forEach(alert => {
            if (!alert.querySelector('.btn-close')) {
                setTimeout(() => {
                    if (alert.parentNode) {
                        alert.remove();
                    }
                }, 5000);
            }
        });
    }

    // Smooth Scrolling
    handleSmoothScroll(event) {
        event.preventDefault();
        const target = document.querySelector(event.currentTarget.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    }

    // Tooltips
    initializeTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Animations
    initializeAnimations() {
        // Intersection Observer for animations
        if ('IntersectionObserver' in window) {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('animate-fadeInUp');
                        observer.unobserve(entry.target);
                    }
                });
            }, {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            });

            document.querySelectorAll('.card, .feature-card, .stat-item').forEach(el => {
                observer.observe(el);
            });
        }
    }

    // Counter Animation
    initializeCounters() {
        const counters = document.querySelectorAll('[data-counter]');
        
        if ('IntersectionObserver' in window) {
            const counterObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        this.animateCounter(entry.target);
                        counterObserver.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.5 });

            counters.forEach(counter => {
                counterObserver.observe(counter);
            });
        }
    }

    animateCounter(element) {
        const target = parseInt(element.dataset.counter);
        const duration = parseInt(element.dataset.duration) || 2000;
        const increment = target / (duration / 16);
        let current = 0;

        const updateCounter = () => {
            current += increment;
            if (current < target) {
                element.textContent = Math.floor(current);
                requestAnimationFrame(updateCounter);
            } else {
                element.textContent = target;
            }
        };

        updateCounter();
    }

    // Theme Toggle
    setupThemeToggle() {
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', this.toggleTheme.bind(this));
            
            // Load saved theme
            const savedTheme = localStorage.getItem('theme');
            if (savedTheme) {
                document.documentElement.setAttribute('data-theme', savedTheme);
            }
        }
    }

    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
    }

    // Keyboard Shortcuts
    handleKeyboardShortcuts(event) {
        // Ctrl/Cmd + K: Focus search
        if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
            event.preventDefault();
            const searchInput = document.querySelector('input[type="search"], input[name="search"]');
            if (searchInput) {
                searchInput.focus();
            }
        }

        // Escape: Close modals, clear forms
        if (event.key === 'Escape') {
            const activeModal = document.querySelector('.modal.show');
            if (activeModal) {
                bootstrap.Modal.getInstance(activeModal).hide();
            }
        }

        // Ctrl/Cmd + Enter: Submit form
        if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
            const activeForm = document.activeElement.closest('form');
            if (activeForm) {
                activeForm.submit();
            }
        }
    }

    // Copy to Clipboard
    handleCopyClick(event) {
        if (event.target.classList.contains('copy-btn') || 
            event.target.closest('.copy-btn')) {
            
            const button = event.target.classList.contains('copy-btn') ? 
                         event.target : event.target.closest('.copy-btn');
            
            const target = button.dataset.copyTarget;
            const text = button.dataset.copyText || 
                        (target ? document.querySelector(target)?.value || 
                                 document.querySelector(target)?.textContent : '');
            
            if (text) {
                this.copyToClipboard(text, button);
            }
        }
    }

    async copyToClipboard(text, button) {
        try {
            await navigator.clipboard.writeText(text);
            this.showCopySuccess(button);
        } catch (err) {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            textArea.style.opacity = '0';
            document.body.appendChild(textArea);
            textArea.select();
            
            try {
                document.execCommand('copy');
                this.showCopySuccess(button);
            } catch (fallbackErr) {
                this.showAlert('Không thể copy. Vui lòng copy thủ công.', 'error');
            }
            
            document.body.removeChild(textArea);
        }
    }

    showCopySuccess(button) {
        const originalHTML = button.innerHTML;
        button.innerHTML = '<i class="fas fa-check text-success"></i> Đã copy';
        button.classList.add('btn-success');
        
        setTimeout(() => {
            button.innerHTML = originalHTML;
            button.classList.remove('btn-success');
        }, 2000);
        
        this.showAlert('Đã copy vào clipboard!', 'success', 2000);
    }

    // Error Handling
    handleGlobalError(event) {
        console.error('Global error:', event.error);
        
        // Don't show error alerts for network errors or script loading errors
        if (event.error && event.error.name !== 'NetworkError') {
            this.showAlert('Đã xảy ra lỗi. Vui lòng tải lại trang.', 'error');
        }
    }

    // Utility Functions
    formatNumber(num) {
        return new Intl.NumberFormat('vi-VN').format(num);
    }

    formatCurrency(amount, currency = 'VND') {
        return new Intl.NumberFormat('vi-VN', {
            style: 'currency',
            currency: currency
        }).format(amount);
    }

    formatDate(date, options = {}) {
        const defaultOptions = {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };
        
        return new Intl.DateTimeFormat('vi-VN', { ...defaultOptions, ...options })
                      .format(new Date(date));
    }

    debounce(func, wait, immediate) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                timeout = null;
                if (!immediate) func(...args);
            };
            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func(...args);
        };
    }

    throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    // API Helper
    async apiRequest(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        try {
            const response = await fetch(url, { ...defaultOptions, ...options });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    // Performance Monitoring
    measurePerformance(name, fn) {
        const start = performance.now();
        const result = fn();
        const end = performance.now();
        
        console.log(`${name} took ${end - start} milliseconds`);
        return result;
    }

    // Local Storage Helper
    storage = {
        set(key, value) {
            try {
                localStorage.setItem(key, JSON.stringify(value));
            } catch (error) {
                console.warn('LocalStorage set failed:', error);
            }
        },

        get(key, defaultValue = null) {
            try {
                const item = localStorage.getItem(key);
                return item ? JSON.parse(item) : defaultValue;
            } catch (error) {
                console.warn('LocalStorage get failed:', error);
                return defaultValue;
            }
        },

        remove(key) {
            try {
                localStorage.removeItem(key);
            } catch (error) {
                console.warn('LocalStorage remove failed:', error);
            }
        }
    };
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.YeuMoneyApp = new YeuMoneyApp();
    
    // Add loading states to all forms
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                YeuMoneyApp.setButtonLoading(submitBtn, true);
            }
        });
    });

    // Add copy functionality to code elements
    document.querySelectorAll('code, .code-block').forEach(codeElement => {
        if (!codeElement.closest('.no-copy')) {
            codeElement.style.cursor = 'pointer';
            codeElement.title = 'Click to copy';
            codeElement.addEventListener('click', function() {
                YeuMoneyApp.copyToClipboard(this.textContent, this);
            });
        }
    });
});

// Expose utility functions globally
window.showAlert = function(message, type, duration) {
    if (window.YeuMoneyApp) {
        window.YeuMoneyApp.showAlert(message, type, duration);
    }
};

window.copyToClipboard = function(text) {
    if (window.YeuMoneyApp) {
        return window.YeuMoneyApp.copyToClipboard(text);
    }
};

// Service Worker Registration (if available)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/sw.js')
            .then(function(registration) {
                console.log('SW registered: ', registration);
            })
            .catch(function(registrationError) {
                console.log('SW registration failed: ', registrationError);
            });
    });
}
