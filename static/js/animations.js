// === ANIMATION UTILITIES ===
class AnimationManager {
    static fadeIn(element, duration = 300) {
        element.style.opacity = '0';
        element.style.display = 'block';
        
        let opacity = 0;
        const increment = 16 / duration;
        
        const fade = () => {
            opacity += increment;
            element.style.opacity = opacity;
            
            if (opacity < 1) {
                requestAnimationFrame(fade);
            }
        };
        
        requestAnimationFrame(fade);
    }

    static slideIn(element, direction = 'right', duration = 300) {
        const transform = direction === 'right' ? 'translateX(100%)' : 'translateX(-100%)';
        
        element.style.transform = transform;
        element.style.transition = `transform ${duration}ms ease`;
        
        setTimeout(() => {
            element.style.transform = 'translateX(0)';
        }, 10);
    }

    static bounce(element, scale = 1.1) {
        element.style.transition = 'transform 0.2s ease';
        element.style.transform = `scale(${scale})`;
        
        setTimeout(() => {
            element.style.transform = 'scale(1)';
        }, 200);
    }

    static shake(element) {
        element.style.animation = 'shake 0.5s ease';
        setTimeout(() => {
            element.style.animation = '';
        }, 500);
    }
}

// Add shake animation to CSS
const shakeCSS = `
@keyframes shake {
    0%, 20%, 40%, 60%, 80% { transform: translateX(0); }
    10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
}
`;

const style = document.createElement('style');
style.textContent = shakeCSS;
document.head.appendChild(style);

// === CARD STACK EFFECT ===
class CardStack {
    static updateStack() {
        const cards = document.querySelectorAll('.swipe-card');
        cards.forEach((card, index) => {
            if (index > 0) {
                card.style.transform = `scale(${1 - index * 0.05}) translateY(${index * 10}px)`;
                card.style.zIndex = 100 - index;
                card.style.opacity = 1 - index * 0.2;
            }
        });
    }
}

// === CONFETTI ANIMATION FOR MATCHES ===
class Confetti {
    static create() {
        const colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#2ed573'];
        const container = document.createElement('div');
        container.className = 'confetti-container';
        container.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            pointer-events: none;
            z-index: 9998;
        `;

        for (let i = 0; i < 50; i++) {
            const confetti = document.createElement('div');
            confetti.style.cssText = `
                position: absolute;
                width: 10px;
                height: 10px;
                background: ${colors[Math.floor(Math.random() * colors.length)]};
                left: ${Math.random() * 100}vw;
                animation: confettiFall ${Math.random() * 3 + 2}s linear forwards;
                opacity: ${Math.random()};
            `;
            container.appendChild(confetti);
        }

        document.body.appendChild(container);
        setTimeout(() => container.remove(), 5000);
    }
}

// Add confetti CSS
const confettiCSS = `
@keyframes confettiFall {
    to {
        transform: translateY(100vh) rotate(360deg);
    }
}
`;

const confettiStyle = document.createElement('style');
confettiStyle.textContent = confettiCSS;
document.head.appendChild(confettiStyle);
