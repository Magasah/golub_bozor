/**
 * GolubBozor - Main JavaScript
 * Mobile menu, Winter mode with snowfall effect
 */

// ========================================
// 1. MOBILE MENU TOGGLE
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');
    const menuOverlay = document.getElementById('menu-overlay');
    
    if (mobileMenuBtn && mobileMenu) {
        // Toggle menu
        mobileMenuBtn.addEventListener('click', function() {
            const isOpen = mobileMenu.classList.contains('translate-x-0');
            
            if (isOpen) {
                // Close menu
                mobileMenu.classList.remove('translate-x-0');
                mobileMenu.classList.add('-translate-x-full');
                menuOverlay.classList.add('hidden');
                document.body.style.overflow = '';
            } else {
                // Open menu
                mobileMenu.classList.remove('-translate-x-full');
                mobileMenu.classList.add('translate-x-0');
                menuOverlay.classList.remove('hidden');
                document.body.style.overflow = 'hidden';
            }
        });
        
        // Close on overlay click
        if (menuOverlay) {
            menuOverlay.addEventListener('click', function() {
                mobileMenu.classList.remove('translate-x-0');
                mobileMenu.classList.add('-translate-x-full');
                menuOverlay.classList.add('hidden');
                document.body.style.overflow = '';
            });
        }
    }
});


// ========================================
// 2. WINTER MODE (Dec, Jan, Feb)
// ========================================
(function initWinterMode() {
    const currentMonth = new Date().getMonth(); // 0-11 (0=Jan, 11=Dec)
    
    // Check if winter months: December (11), January (0), February (1)
    const isWinter = currentMonth === 11 || currentMonth === 0 || currentMonth === 1;
    
    if (!isWinter) {
        console.log('🌸 Not winter season - no snow effect');
        return;
    }
    
    console.log('❄️ Winter mode activated!');
    
    // Add winter class to body for CSS garland
    document.body.classList.add('winter-mode');
    
    // Initialize snowfall
    initSnowfall();
})();


// ========================================
// 3. SNOWFALL EFFECT (Canvas)
// ========================================
function initSnowfall() {
    const container = document.getElementById('snow-container');
    if (!container) {
        console.warn('Snow container not found');
        return;
    }
    
    const canvas = document.createElement('canvas');
    canvas.style.position = 'fixed';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    canvas.style.pointerEvents = 'none';
    canvas.style.zIndex = '9999';
    
    container.appendChild(canvas);
    
    const ctx = canvas.getContext('2d');
    
    // Set canvas size
    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    
    // Snowflake class
    class Snowflake {
        constructor() {
            this.reset();
        }
        
        reset() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * -canvas.height;
            this.size = Math.random() * 3 + 1; // 1-4px
            this.speedY = Math.random() * 1 + 0.5; // 0.5-1.5px per frame
            this.speedX = Math.random() * 0.5 - 0.25; // slight horizontal drift
            this.opacity = Math.random() * 0.6 + 0.3; // 0.3-0.9
        }
        
        update() {
            this.y += this.speedY;
            this.x += this.speedX;
            
            // Reset if out of bounds
            if (this.y > canvas.height) {
                this.reset();
            }
            
            if (this.x > canvas.width || this.x < 0) {
                this.x = Math.random() * canvas.width;
            }
        }
        
        draw() {
            ctx.fillStyle = `rgba(255, 255, 255, ${this.opacity})`;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
        }
    }
    
    // Create snowflakes (50-100 depending on screen size)
    const snowflakeCount = Math.min(100, Math.floor(canvas.width / 20));
    const snowflakes = [];
    
    for (let i = 0; i < snowflakeCount; i++) {
        snowflakes.push(new Snowflake());
    }
    
    // Animation loop
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        snowflakes.forEach(snowflake => {
            snowflake.update();
            snowflake.draw();
        });
        
        requestAnimationFrame(animate);
    }
    
    animate();
}


// ========================================
// 4. FAVORITE TOGGLE (AJAX)
// ========================================
function toggleFavorite(pigeonId, button) {
    // Check if user is authenticated
    const isAuthenticated = document.body.dataset.userAuthenticated === 'true';
    
    if (!isAuthenticated) {
        window.location.href = '/login/?next=' + window.location.pathname;
        return;
    }
    
    // Get CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    
    if (!csrfToken) {
        console.error('CSRF token not found');
        return;
    }
    
    // Send AJAX request
    fetch(`/pigeon/${pigeonId}/favorite/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update button state
            const heartIcon = button.querySelector('.heart-icon');
            const buttonText = button.querySelector('.favorite-text');
            
            if (data.is_favorited) {
                // Favorited - show filled heart
                heartIcon.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clip-rule="evenodd" />
                    </svg>
                `;
                button.classList.remove('border-gray-700', 'text-gray-300');
                button.classList.add('border-red-500', 'text-red-500', 'bg-red-500/10');
                if (buttonText) buttonText.textContent = 'В избранном';
            } else {
                // Not favorited - show empty heart
                heartIcon.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                    </svg>
                `;
                button.classList.remove('border-red-500', 'text-red-500', 'bg-red-500/10');
                button.classList.add('border-gray-700', 'text-gray-300');
                if (buttonText) buttonText.textContent = 'В избранное';
            }
            
            // Show toast notification
            showToast(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Произошла ошибка', 'error');
    });
}


// ========================================
// 5. SHARE FUNCTIONALITY
// ========================================
function shareProduct(title, url) {
    // Check if Web Share API is supported
    if (navigator.share) {
        navigator.share({
            title: title,
            url: url
        })
        .then(() => console.log('Shared successfully'))
        .catch(err => console.log('Share failed:', err));
    } else {
        // Fallback: Copy to clipboard
        copyToClipboard(url);
        showToast('Ссылка скопирована в буфер обмена');
    }
}

function copyToClipboard(text) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
}


// ========================================
// 6. TOAST NOTIFICATIONS
// ========================================
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `fixed bottom-4 right-4 px-6 py-3 rounded-lg shadow-lg transform transition-all duration-300 translate-y-20 z-50 ${
        type === 'success' ? 'bg-green-600' : 'bg-red-600'
    } text-white font-semibold`;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    // Animate in
    setTimeout(() => {
        toast.classList.remove('translate-y-20');
        toast.classList.add('translate-y-0');
    }, 10);
    
    // Remove after 3 seconds
    setTimeout(() => {
        toast.classList.remove('translate-y-0');
        toast.classList.add('translate-y-20');
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 3000);
}


// ========================================
// 7. EXPOSE GLOBAL FUNCTIONS
// ========================================
window.toggleFavorite = toggleFavorite;
window.shareProduct = shareProduct;
