// Activity Tracker JavaScript
// Handles badge taps, AJAX requests, and visual feedback

// Prevent multiple initializations
if (window.activityTrackerInitialized) {
    console.warn('Activity tracker already initialized');
} else {
    window.activityTrackerInitialized = true;

    document.addEventListener('DOMContentLoaded', function() {
    // Get CSRF token from meta tag or cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // Try to get CSRF token from hidden input (Django's {% csrf_token %}) or cookie
    let csrftoken = null;
    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfInput) {
        csrftoken = csrfInput.value;
    } else {
        csrftoken = getCookie('csrftoken');
    }
    
    // Get all activity badges
    const badges = document.querySelectorAll('.activity-badge');
    
    // Remove any existing listeners first by cloning and replacing
    badges.forEach(function(badge) {
        if (badge.dataset.listenerAttached === 'true') {
            // Already has listener, skip
            return;
        }
        badge.dataset.listenerAttached = 'true';
    });
    
    // Attach listeners to badges
    badges.forEach(function(badge) {
        if (badge.dataset.listenerAttached !== 'true') {
            return;
        }
        
        badge.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            e.stopImmediatePropagation();
            
            // Prevent double-clicks and multiple simultaneous requests
            if (this.dataset.processing === 'true') {
                console.log('Already processing, ignoring click');
                return;
            }
            this.dataset.processing = 'true';
            const activityType = this.getAttribute('data-activity-type');
            const countElement = this.querySelector('.badge-count');
            const originalCount = parseInt(countElement.textContent) || 0;
            
            // Disable badge temporarily to prevent rapid clicks
            this.style.pointerEvents = 'none';
            this.style.opacity = '0.7';
            
            // Make AJAX request
            fetch('/api/activity/tap/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({
                    'activity_type': activityType
                })
            })
            .then(response => {
                console.log('Response status:', response.status);
                return response.json();
            })
            .then(data => {
                console.log('Response data:', data);
                // Re-enable badge
                this.style.pointerEvents = 'auto';
                this.dataset.processing = 'false';
                
                if (data.success) {
                    console.log('Success! Updating count and triggering animation');
                    // Update count - use the count from server response (server is source of truth)
                    if (data.counts) {
                        const countKey = activityType.toLowerCase();
                        const newCount = data.counts[countKey] || 0;
                        // Add visual feedback to count update
                        countElement.classList.add('updating');
                        countElement.textContent = newCount;
                        setTimeout(() => {
                            countElement.classList.remove('updating');
                        }, 300);
                    } else {
                        // Fallback: increment by 1 (shouldn't happen if server responds correctly)
                        const currentCount = parseInt(countElement.textContent) || 0;
                        countElement.textContent = currentCount + 1;
                    }
                    
                    // Visual feedback based on activity type - trigger immediately
                    console.log('Triggering animation for:', activityType, 'on badge:', this);
                    // Use requestAnimationFrame to ensure DOM is ready
                    requestAnimationFrame(() => {
                        if (activityType === 'RESIST') {
                            // Confetti effect (simple CSS animation)
                            triggerConfetti(this);
                        } else if (activityType === 'SMOKED') {
                            // Dull grey-out effect
                            triggerGreyOut(this);
                        } else if (activityType === 'SPORT') {
                            // Success glow effect
                            triggerSuccessGlow(this);
                        } else {
                            console.warn('Unknown activity type:', activityType);
                        }
                    });
                } else {
                    console.log('Request failed:', data);
                    // Handle error (rate limiting, etc.)
                    if (data.rate_limited) {
                        showToast(data.error || 'Слишком часто. Попробуйте через 3 секунды.');
                    } else {
                        showToast(data.error || 'Ошибка при сохранении.');
                    }
                }
            })
            .catch(error => {
                // Re-enable badge
                this.style.pointerEvents = 'auto';
                this.style.opacity = '1';
                this.dataset.processing = 'false';
                
                console.error('Error:', error);
                showToast('Ошибка соединения.');
            });
        });
    });
    
    // Visual feedback functions - using direct JavaScript animation for reliability
    function triggerConfetti(badge) {
        console.log('triggerConfetti called', badge);
        // Remove any existing animation classes
        badge.classList.remove('confetti-burst', 'success-glow');
        
        // Clear inline styles
        badge.style.transform = '';
        badge.style.boxShadow = '';
        badge.style.transition = 'none';
        
        // Force reflow
        void badge.offsetWidth;
        
        // Add class for CSS animation
        badge.classList.add('confetti-burst');
        
        // Also apply direct animation as fallback
        const startTime = Date.now();
        const duration = 2000; // 2 seconds
        
        function animate() {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            if (progress < 1) {
                // Easing function
                const easeOut = 1 - Math.pow(1 - progress, 3);
                
                // Scale animation
                const scale = 1 + (0.25 * Math.sin(progress * Math.PI * 2));
                badge.style.transform = `scale(${scale})`;
                
                // Box shadow animation
                const shadowSize = 20 + (20 * Math.sin(progress * Math.PI));
                const shadowOpacity = 0.7 + (0.3 * Math.sin(progress * Math.PI));
                badge.style.boxShadow = `0 0 ${shadowSize}px ${shadowSize/2}px rgba(58, 191, 131, ${shadowOpacity})`;
                
                requestAnimationFrame(animate);
            } else {
                // Reset to original state
                badge.style.transform = '';
                badge.style.boxShadow = '';
                badge.style.transition = '';
                badge.classList.remove('confetti-burst');
            }
        }
        
        requestAnimationFrame(animate);
    }
    
    function triggerGreyOut(badge) {
        console.log('triggerGreyOut called', badge);
        // Remove any existing animation classes first
        badge.classList.remove('confetti-burst', 'success-glow');
        badge.style.transform = '';
        badge.style.boxShadow = '';
        // Dull grey-out effect - more visible
        badge.style.transition = 'filter 0.5s ease, opacity 0.5s ease';
        badge.style.filter = 'grayscale(80%) brightness(0.7)';
        badge.style.opacity = '0.6';
        console.log('Grey-out styles applied');
        setTimeout(() => {
            badge.style.filter = '';
            badge.style.opacity = '1'; // Explicitly set back to 1
            badge.style.transition = '';
        }, 1200);
    }
    
    function triggerSuccessGlow(badge) {
        console.log('triggerSuccessGlow called', badge);
        // Remove any existing animation classes
        badge.classList.remove('confetti-burst', 'success-glow');
        
        // Clear inline styles
        badge.style.transform = '';
        badge.style.boxShadow = '';
        badge.style.transition = 'none';
        
        // Force reflow
        void badge.offsetWidth;
        
        // Add class for CSS animation
        badge.classList.add('success-glow');
        
        // Also apply direct animation as fallback
        const startTime = Date.now();
        const duration = 1500; // 1.5 seconds
        
        function animate() {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            if (progress < 1) {
                // Easing function
                const easeOut = 1 - Math.pow(1 - progress, 2);
                
                // Scale animation
                const scale = 1 + (0.12 * Math.sin(progress * Math.PI));
                badge.style.transform = `scale(${scale})`;
                
                // Box shadow animation
                const shadowSize = 15 + (25 * Math.sin(progress * Math.PI));
                const shadowOpacity = 0.7 + (0.3 * Math.sin(progress * Math.PI));
                badge.style.boxShadow = `0 0 ${shadowSize}px ${shadowSize/2}px rgba(0, 123, 255, ${shadowOpacity})`;
                
                requestAnimationFrame(animate);
            } else {
                // Reset to original state
                badge.style.transform = '';
                badge.style.boxShadow = '';
                badge.style.transition = '';
                badge.classList.remove('success-glow');
            }
        }
        
        requestAnimationFrame(animate);
    }
    
    // Toast notification function
    function showToast(message) {
        // Create toast element
        const toast = document.createElement('div');
        toast.className = 'toast-message';
        toast.textContent = message;
        document.body.appendChild(toast);
        
        // Show toast
        setTimeout(() => {
            toast.classList.add('show');
        }, 10);
        
        // Hide and remove toast after 3 seconds
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 3000);
    }
    });
} // End of initialization check
