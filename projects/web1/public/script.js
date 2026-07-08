// Client-side animations for SynthLang Portfolio

// Counter animation
function animateCounter() {
    const counter = document.getElementById('counter');
    if (counter) {
        let count = 0;
        const target = 10000;
        const increment = target / 100;
        
        const timer = setInterval(() => {
            count += increment;
            counter.textContent = Math.floor(count);
            if (count >= target) {
                counter.textContent = target.toLocaleString();
                clearInterval(timer);
            }
        }, 20);
    }
}

// Form submission handler
function handleFormSubmit() {
    const form = document.getElementById('contactForm');
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const response = document.getElementById('response');
            response.textContent = 'Submitting...';
            response.style.background = '#e3f2fd';
            
            // Simulate submission
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            response.textContent = 'Message sent successfully!';
            response.style.background = '#e8f5e9';
            form.reset();
        });
    }
}

// Initialize animations when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    animateCounter();
    handleFormSubmit();
});