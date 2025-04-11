/**
 * Responsive behavior for the AI Recruitment System
 */

document.addEventListener('DOMContentLoaded', function() {
    // Sidebar toggle functionality for mobile
    const sidebarToggleBtn = document.getElementById('sidebarToggleBtn');
    const sidebar = document.getElementById('sidebar');
    
    if (sidebarToggleBtn && sidebar) {
        // Create backdrop element
        const backdrop = document.createElement('div');
        backdrop.classList.add('sidebar-backdrop');
        document.body.appendChild(backdrop);
        
        // Toggle sidebar
        sidebarToggleBtn.addEventListener('click', function() {
            sidebar.classList.toggle('show');
            backdrop.classList.toggle('show');
        });
        
        // Close sidebar when clicking outside
        backdrop.addEventListener('click', function() {
            sidebar.classList.remove('show');
            backdrop.classList.remove('show');
        });
        
        // Close sidebar when clicking a nav link (on mobile)
        const navLinks = sidebar.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                if (window.innerWidth < 768) {
                    sidebar.classList.remove('show');
                    backdrop.classList.remove('show');
                }
            });
        });
        
        // Adjust for screen size changes
        window.addEventListener('resize', function() {
            if (window.innerWidth >= 768) {
                sidebar.classList.remove('show');
                backdrop.classList.remove('show');
            }
        });
    }
    
    // Make tables responsive
    const tables = document.querySelectorAll('table:not(.table-responsive)');
    tables.forEach(table => {
        if (!table.parentElement.classList.contains('table-responsive')) {
            const wrapper = document.createElement('div');
            wrapper.classList.add('table-responsive');
            table.parentNode.insertBefore(wrapper, table);
            wrapper.appendChild(table);
        }
    });
    
    // Responsive buttons
    const actionButtons = document.querySelectorAll('.btn-responsive');
    function adjustButtons() {
        if (window.innerWidth < 576) {
            actionButtons.forEach(btn => {
                btn.classList.add('w-100', 'mb-2');
            });
        } else {
            actionButtons.forEach(btn => {
                btn.classList.remove('w-100', 'mb-2');
            });
        }
    }
    
    adjustButtons();
    window.addEventListener('resize', adjustButtons);
    
    // Touch-friendly adjustments
    if ('ontouchstart' in window || navigator.maxTouchPoints > 0) {
        document.body.classList.add('touch-device');
        
        // Increase target sizes for touch devices
        const smallButtons = document.querySelectorAll('.btn-sm');
        smallButtons.forEach(btn => {
            btn.classList.remove('btn-sm');
        });
        
        // Ensure dropdowns work well on touch
        const dropdowns = document.querySelectorAll('.dropdown-toggle');
        dropdowns.forEach(dropdown => {
            dropdown.setAttribute('data-bs-auto-close', 'outside');
        });
    }
});