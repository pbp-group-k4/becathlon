/**
 * Dynamic Hero Animation System
 * Creates abstract particle system with sports-themed motion
 */

class HeroAnimation {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) {
            console.error('Canvas element not found');
            return;
        }
        
        this.ctx = this.canvas.getContext('2d');
        this.particles = [];
        this.connections = [];
        
        this.init();
    }

    init() {
        this.resize();
        this.createParticles();
        this.setupEventListeners();
        this.animate();
    }

    resize() {
        const container = this.canvas.parentElement;
        this.canvas.width = container.offsetWidth;
        this.canvas.height = container.offsetHeight;
        this.width = this.canvas.width;
        this.height = this.canvas.height;
    }

    setupEventListeners() {
        window.addEventListener('resize', () => this.resize());
    }

    createParticles() {
        const particleCount = Math.floor((this.width * this.height) / 25000);
        this.particles = [];

        for (let i = 0; i < particleCount; i++) {
            this.particles.push(new Particle(this.width, this.height));
        }
    }

    drawConnections() {
        const maxDistance = 150;
        
        for (let i = 0; i < this.particles.length; i++) {
            for (let j = i + 1; j < this.particles.length; j++) {
                const dx = this.particles[i].x - this.particles[j].x;
                const dy = this.particles[i].y - this.particles[j].y;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < maxDistance) {
                    const opacity = (1 - distance / maxDistance) * 0.15;
                    
                    this.ctx.beginPath();
                    this.ctx.strokeStyle = `rgba(255, 255, 255, ${opacity})`;
                    this.ctx.lineWidth = 0.5;
                    this.ctx.moveTo(this.particles[i].x, this.particles[i].y);
                    this.ctx.lineTo(this.particles[j].x, this.particles[j].y);
                    this.ctx.stroke();
                }
            }
        }
    }

    drawParticles() {
        this.particles.forEach(particle => {
            particle.update(this.width, this.height);
            particle.draw(this.ctx);
        });
    }

    animate() {
        this.ctx.clearRect(0, 0, this.width, this.height);
        
        // Draw connections first (behind particles)
        this.drawConnections();
        
        // Draw particles
        this.drawParticles();
        
        requestAnimationFrame(() => this.animate());
    }
}

class Particle {
    constructor(canvasWidth, canvasHeight) {
        this.x = Math.random() * canvasWidth;
        this.y = Math.random() * canvasHeight;
        this.vx = (Math.random() - 0.5) * 0.5;
        this.vy = (Math.random() - 0.5) * 0.5;
        this.radius = Math.random() * 2 + 1;
        this.originalRadius = this.radius;
        
        // Greyscale colors only
        const colors = [
            'rgba(200, 200, 200, 0.8)',    // Light grey
            'rgba(150, 150, 150, 0.8)',    // Medium grey
            'rgba(180, 180, 180, 0.8)'     // Light-medium grey
        ];
        this.color = colors[Math.floor(Math.random() * colors.length)];
        
        // Pulsing animation
        this.pulseSpeed = Math.random() * 0.02 + 0.01;
        this.pulsePhase = Math.random() * Math.PI * 2;
    }

    update(canvasWidth, canvasHeight) {
        // Update position
        this.x += this.vx;
        this.y += this.vy;

        // Boundary collision with bounce
        if (this.x < 0 || this.x > canvasWidth) {
            this.vx *= -1;
            this.x = Math.max(0, Math.min(canvasWidth, this.x));
        }
        if (this.y < 0 || this.y > canvasHeight) {
            this.vy *= -1;
            this.y = Math.max(0, Math.min(canvasHeight, this.y));
        }

        // Apply velocity damping
        this.vx *= 0.99;
        this.vy *= 0.99;

        // Ensure minimum velocity for constant motion
        const minSpeed = 0.1;
        const speed = Math.sqrt(this.vx * this.vx + this.vy * this.vy);
        if (speed < minSpeed) {
            const angle = Math.atan2(this.vy, this.vx);
            this.vx = Math.cos(angle) * minSpeed;
            this.vy = Math.sin(angle) * minSpeed;
        }

        // Pulsing effect
        this.pulsePhase += this.pulseSpeed;
        this.radius = this.originalRadius + Math.sin(this.pulsePhase) * 0.5;
    }

    draw(ctx) {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
        ctx.fillStyle = this.color;
        ctx.fill();
        
        // Glow effect
        ctx.shadowBlur = 10;
        ctx.shadowColor = this.color;
        ctx.fill();
        ctx.shadowBlur = 0;
    }
}

// Sports Motion Trails (Abstract representation of athletic movement)
class MotionTrail {
    constructor(canvasElement) {
        this.canvas = canvasElement;
        this.ctx = this.canvas.getContext('2d');
        this.trails = [];
        this.maxTrails = 3;
        
        this.initTrails();
        this.animateTrails();
    }

    initTrails() {
        for (let i = 0; i < this.maxTrails; i++) {
            this.trails.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                angle: Math.random() * Math.PI * 2,
                speed: Math.random() * 2 + 1,
                length: Math.random() * 200 + 100,
                width: Math.random() * 3 + 1,
                opacity: Math.random() * 0.3 + 0.1,
                hue: Math.random() * 60 + 200 // Blue to cyan range
            });
        }
    }

    animateTrails() {
        this.trails.forEach(trail => {
            const endX = trail.x + Math.cos(trail.angle) * trail.length;
            const endY = trail.y + Math.sin(trail.angle) * trail.length;

            // Create gradient for motion blur effect
            const gradient = this.ctx.createLinearGradient(trail.x, trail.y, endX, endY);
            gradient.addColorStop(0, `hsla(${trail.hue}, 80%, 60%, ${trail.opacity})`);
            gradient.addColorStop(1, `hsla(${trail.hue}, 80%, 60%, 0)`);

            this.ctx.beginPath();
            this.ctx.strokeStyle = gradient;
            this.ctx.lineWidth = trail.width;
            this.ctx.lineCap = 'round';
            this.ctx.moveTo(trail.x, trail.y);
            this.ctx.lineTo(endX, endY);
            this.ctx.stroke();

            // Update trail position
            trail.x += Math.cos(trail.angle) * trail.speed;
            trail.y += Math.sin(trail.angle) * trail.speed;

            // Wrap around canvas
            if (trail.x < -trail.length) trail.x = this.canvas.width + trail.length;
            if (trail.x > this.canvas.width + trail.length) trail.x = -trail.length;
            if (trail.y < -trail.length) trail.y = this.canvas.height + trail.length;
            if (trail.y > this.canvas.height + trail.length) trail.y = -trail.length;

            // Randomly change direction occasionally
            if (Math.random() < 0.01) {
                trail.angle += (Math.random() - 0.5) * 0.5;
            }
        });

        requestAnimationFrame(() => this.animateTrails());
    }
}

// Stats Counter Animation
function animateCounter(element, target, duration = 2000) {
    const start = 0;
    const startTime = performance.now();
    
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function (easeOutExpo)
        const easeProgress = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
        const current = Math.floor(start + (target - start) * easeProgress);
        
        element.textContent = current.toLocaleString();
        
        if (progress < 1) {
            requestAnimationFrame(update);
        } else {
            element.textContent = target.toLocaleString();
        }
    }
    
    requestAnimationFrame(update);
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Initialize hero animation
    const heroCanvas = document.getElementById('heroCanvas');
    if (heroCanvas) {
        new HeroAnimation('heroCanvas');
    }

    // Animate stats counters if they exist
    const statElements = document.querySelectorAll('.hero-stat-value[data-target]');
    
    // Use Intersection Observer to trigger animation when visible
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !entry.target.dataset.animated) {
                const target = parseInt(entry.target.dataset.target);
                animateCounter(entry.target, target);
                entry.target.dataset.animated = 'true';
            }
        });
    }, { threshold: 0.5 });

    statElements.forEach(element => observer.observe(element));

    // Smooth scroll for scroll indicator
    const scrollIndicator = document.querySelector('.hero-scroll-indicator');
    if (scrollIndicator) {
        scrollIndicator.style.cursor = 'pointer';
        scrollIndicator.addEventListener('click', () => {
            const hero = document.querySelector('.hero');
            if (hero) {
                const heroHeight = hero.offsetHeight;
                window.scrollTo({
                    top: heroHeight,
                    behavior: 'smooth'
                });
            }
        });
    }

    // Parallax effect on scroll
    let ticking = false;
    window.addEventListener('scroll', () => {
        if (!ticking) {
            window.requestAnimationFrame(() => {
                const scrolled = window.pageYOffset;
                const heroContent = document.querySelector('.hero-content');
                const heroOrbs = document.querySelectorAll('.hero-orb');
                
                if (heroContent) {
                    heroContent.style.transform = `translateY(${scrolled * 0.5}px)`;
                    heroContent.style.opacity = 1 - (scrolled / 800);
                }
                
                heroOrbs.forEach((orb, index) => {
                    const speed = 0.3 + (index * 0.1);
                    orb.style.transform = `translate(${scrolled * speed}px, ${scrolled * speed * 0.5}px)`;
                });
                
                ticking = false;
            });
            ticking = true;
        }
    });
});

// Export for potential module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { HeroAnimation, MotionTrail, animateCounter };
}
