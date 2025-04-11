/**
 * animations.js - Animation functions for the AI Recruitment System
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize compatibility meters
    initCompatibilityMeters();
    
    // Initialize stat card animations
    initStatCards();
    
    // Initialize match indicator animations
    initMatchIndicators();
    
    // Initialize skill level animations
    initSkillLevels();
    
    // Initialize ripple effect for buttons
    initRippleEffect();
    
    // Initialize staggered animations
    initStaggeredAnimations();
    
    // Initialize on-scroll animations
    initScrollAnimations();
});

/**
 * Initialize compatibility meters
 */
function initCompatibilityMeters() {
    const meters = document.querySelectorAll('.compatibility-meter');
    
    meters.forEach(meter => {
        const score = parseFloat(meter.getAttribute('data-score')) || 0;
        const fill = meter.querySelector('.compatibility-meter-fill');
        const marker = meter.querySelector('.compatibility-meter-marker');
        const label = meter.querySelector('.compatibility-meter-label');
        
        // Score is between 0 and 1
        const percentage = Math.min(Math.max(score * 100, 0), 100);
        
        // Animate after a small delay
        setTimeout(() => {
            if (fill) fill.style.width = `${percentage}%`;
            if (marker) marker.style.left = `${percentage}%`;
            if (label) {
                label.style.left = `${percentage}%`;
                label.textContent = `${Math.round(percentage)}%`;
                
                // Add color classes based on score
                if (percentage >= 80) {
                    label.classList.add('text-success');
                } else if (percentage >= 60) {
                    label.classList.add('text-info');
                } else if (percentage >= 40) {
                    label.classList.add('text-warning');
                } else {
                    label.classList.add('text-danger');
                }
            }
        }, 300);
    });
}

/**
 * Initialize stat card animations
 */
function initStatCards() {
    const cards = document.querySelectorAll('.stat-card');
    
    cards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            const icon = card.querySelector('.stat-icon');
            if (icon) {
                icon.style.transform = 'translateY(-50%) scale(1.1) rotate(5deg)';
                icon.style.opacity = '0.25';
            }
        });
        
        card.addEventListener('mouseleave', () => {
            const icon = card.querySelector('.stat-icon');
            if (icon) {
                icon.style.transform = 'translateY(-50%)';
                icon.style.opacity = '0.15';
            }
        });
    });
}

/**
 * Initialize match indicator animations
 */
function initMatchIndicators() {
    const indicators = document.querySelectorAll('.match-indicator');
    
    indicators.forEach(indicator => {
        const score = parseFloat(indicator.getAttribute('data-score')) || 0;
        
        // Set class based on score
        if (score >= 0.75) {
            indicator.classList.add('match-high');
        } else if (score >= 0.5) {
            indicator.classList.add('match-medium');
        } else {
            indicator.classList.add('match-low');
        }
        
        // Add pulse animation on hover
        indicator.addEventListener('mouseenter', () => {
            indicator.classList.add('pulse');
        });
        
        indicator.addEventListener('mouseleave', () => {
            indicator.classList.remove('pulse');
        });
    });
}

/**
 * Initialize skill level animations
 */
function initSkillLevels() {
    const skillLevels = document.querySelectorAll('.skill-level');
    
    if (skillLevels.length > 0 && 'IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const fills = entry.target.querySelectorAll('.level-fill');
                    fills.forEach(fill => {
                        const level = fill.getAttribute('data-level');
                        let width = '25%';
                        
                        if (level === 'intermediate') width = '50%';
                        if (level === 'advanced') width = '75%';
                        if (level === 'expert') width = '100%';
                        
                        fill.style.width = width;
                    });
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.2 });
        
        skillLevels.forEach(level => {
            observer.observe(level);
        });
    }
}

/**
 * Initialize ripple effect for buttons
 */
function initRippleEffect() {
    const buttons = document.querySelectorAll('.btn-ripple');
    
    buttons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            const rect = e.target.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const circle = document.createElement('span');
            circle.style.width = circle.style.height = '1px';
            circle.style.position = 'absolute';
            circle.style.borderRadius = '50%';
            circle.style.left = x + 'px';
            circle.style.top = y + 'px';
            circle.style.backgroundColor = 'rgba(255, 255, 255, 0.4)';
            
            this.appendChild(circle);
            
            const ripple = document.createElement('style');
            ripple.textContent = `
                @keyframes ripple-effect {
                    to {
                        transform: scale(100);
                        opacity: 0;
                    }
                }
            `;
            
            document.head.appendChild(ripple);
            
            circle.style.animation = 'ripple-effect 0.8s linear';
            
            setTimeout(() => {
                circle.remove();
                ripple.remove();
            }, 800);
        });
    });
}

/**
 * Initialize staggered animations
 */
function initStaggeredAnimations() {
    const containers = document.querySelectorAll('.stagger-fade-in');
    
    if (containers.length > 0 && 'IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const children = entry.target.children;
                    Array.from(children).forEach((child, index) => {
                        setTimeout(() => {
                            child.style.opacity = '1';
                        }, index * 100);
                    });
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });
        
        containers.forEach(container => {
            observer.observe(container);
        });
    }
}

/**
 * Initialize on-scroll animations
 */
function initScrollAnimations() {
    const elements = document.querySelectorAll('.animate-on-scroll');
    
    if (elements.length > 0 && 'IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });
        
        elements.forEach(element => {
            observer.observe(element);
        });
    }
}

/**
 * Create compatibility meter element
 * @param {number} score - Compatibility score (0-1)
 * @returns {HTMLElement} - Compatibility meter element
 */
function createCompatibilityMeter(score) {
    const percentage = Math.min(Math.max(score * 100, 0), 100);
    
    const meter = document.createElement('div');
    meter.className = 'compatibility-meter';
    meter.setAttribute('data-score', score);
    
    const fill = document.createElement('div');
    fill.className = 'compatibility-meter-fill';
    fill.style.width = '0%'; // Will be animated to the actual percentage
    
    const marker = document.createElement('div');
    marker.className = 'compatibility-meter-marker';
    marker.style.left = '0%'; // Will be animated to the actual percentage
    
    const label = document.createElement('div');
    label.className = 'compatibility-meter-label';
    label.textContent = '0%'; // Will be updated during animation
    
    meter.appendChild(fill);
    meter.appendChild(marker);
    meter.appendChild(label);
    
    // Animate after insertion into DOM
    setTimeout(() => {
        fill.style.width = `${percentage}%`;
        marker.style.left = `${percentage}%`;
        label.style.left = `${percentage}%`;
        label.textContent = `${Math.round(percentage)}%`;
        
        // Add color classes based on score
        if (percentage >= 80) {
            label.classList.add('text-success');
        } else if (percentage >= 60) {
            label.classList.add('text-info');
        } else if (percentage >= 40) {
            label.classList.add('text-warning');
        } else {
            label.classList.add('text-danger');
        }
    }, 300);
    
    return meter;
}

/**
 * Create match indicator element
 * @param {number} score - Match score (0-1)
 * @returns {HTMLElement} - Match indicator element
 */
function createMatchIndicator(score) {
    const indicator = document.createElement('div');
    indicator.className = 'match-indicator';
    indicator.setAttribute('data-score', score);
    
    // Set class based on score
    if (score >= 0.75) {
        indicator.classList.add('match-high');
    } else if (score >= 0.5) {
        indicator.classList.add('match-medium');
    } else {
        indicator.classList.add('match-low');
    }
    
    // Set score text
    indicator.textContent = `${Math.round(score * 100)}%`;
    
    return indicator;
}

/**
 * Add hover effect to element
 * @param {HTMLElement} element - Element to add hover effect to
 * @param {string} effect - Effect type ('glow', 'scale', 'slide', etc.)
 */
function addHoverEffect(element, effect) {
    if (!element) return;
    
    if (effect === 'glow') {
        element.classList.add('hover-glow');
    } else if (effect === 'scale') {
        element.addEventListener('mouseenter', () => {
            element.style.transform = 'scale(1.05)';
        });
        
        element.addEventListener('mouseleave', () => {
            element.style.transform = '';
        });
    } else if (effect === 'slide') {
        element.addEventListener('mouseenter', () => {
            element.style.transform = 'translateX(5px)';
        });
        
        element.addEventListener('mouseleave', () => {
            element.style.transform = '';
        });
    }
}

/**
 * Create a skill tag element
 * @param {string} skill - Skill text 
 * @param {string} level - Skill level ('beginner', 'intermediate', 'advanced', 'expert')
 * @returns {HTMLElement} - Skill tag element
 */
function createSkillTag(skill, level) {
    const tag = document.createElement('span');
    tag.className = 'tag';
    tag.textContent = skill;
    
    // Add class based on level
    if (level === 'beginner') {
        tag.classList.add('tag-warning');
    } else if (level === 'intermediate') {
        tag.classList.add('tag-info');
    } else if (level === 'advanced') {
        tag.classList.add('tag-success');
    } else if (level === 'expert') {
        tag.classList.add('tag-primary');
    } else {
        tag.classList.add('tag-purple');
    }
    
    return tag;
}
