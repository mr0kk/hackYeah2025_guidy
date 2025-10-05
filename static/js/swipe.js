// === SWIPE LOGIC ===
class SwipeManager {
    constructor() {
        this.currentProfiles = [];
        this.currentIndex = 0;
        this.isDragging = false;
        this.startX = 0;
        this.startY = 0;
        this.currentX = 0;
        this.currentY = 0;
        this.container = null;
        
        this.init();
    }

    async init() {
        this.container = document.querySelector('.swipe-container');
        if (!this.container) return;

        await this.loadProfiles();
        this.setupEventListeners();
        this.renderCurrentCard();
    }

    async loadProfiles() {
        try {
            showLoading(true);
            const response = await api.getProfiles();
            this.currentProfiles = response.profiles || [];
            this.currentIndex = 0;
            showLoading(false);
        } catch (error) {
            console.error('Failed to load profiles:', error);
            showLoading(false);
            showError('Nie udało się załadować profili');
        }
    }

    setupEventListeners() {
        // Mouse events
        this.container.addEventListener('mousedown', this.handleStart.bind(this));
        document.addEventListener('mousemove', this.handleMove.bind(this));
        document.addEventListener('mouseup', this.handleEnd.bind(this));

        // Touch events for mobile
        this.container.addEventListener('touchstart', this.handleStart.bind(this));
        document.addEventListener('touchmove', this.handleMove.bind(this));
        document.addEventListener('touchend', this.handleEnd.bind(this));

        // Action buttons
        document.addEventListener('click', (e) => {
            if (e.target.closest('.btn-dislike')) {
                this.swipeCard('left');
            } else if (e.target.closest('.btn-like')) {
                this.swipeCard('right');
            } else if (e.target.closest('.btn-superlike')) {
                this.swipeCard('up');
            }
        });
    }

    handleStart(e) {
        if (!e.target.closest('.swipe-card')) return;
        
        this.isDragging = true;
        const point = e.touches ? e.touches[0] : e;
        this.startX = point.clientX;
        this.startY = point.clientY;
        
        const card = e.target.closest('.swipe-card');
        card.classList.add('dragging');
    }

    handleMove(e) {
        if (!this.isDragging) return;
        
        e.preventDefault();
        const point = e.touches ? e.touches[0] : e;
        this.currentX = point.clientX - this.startX;
        this.currentY = point.clientY - this.startY;
        
        const card = this.container.querySelector('.swipe-card');
        if (!card) return;

        const rotation = this.currentX * 0.1;
        const opacity = Math.max(0.7, 1 - Math.abs(this.currentX) / 300);
        
        card.style.transform = `translate(${this.currentX}px, ${this.currentY}px) rotate(${rotation}deg)`;
        card.style.opacity = opacity;

        // Show direction indicators
        this.updateDirectionIndicators();
    }

    handleEnd(e) {
        if (!this.isDragging) return;
        
        this.isDragging = false;
        const card = this.container.querySelector('.swipe-card');
        if (!card) return;

        card.classList.remove('dragging');
        
        const threshold = 100;
        const absX = Math.abs(this.currentX);
        const absY = Math.abs(this.currentY);

        if (absX > threshold && absX > absY) {
            // Horizontal swipe
            const direction = this.currentX > 0 ? 'right' : 'left';
            this.swipeCard(direction);
        } else if (this.currentY < -threshold && absY > absX) {
            // Vertical swipe up
            this.swipeCard('up');
        } else {
            // Return to center
            this.resetCard();
        }
    }

    async swipeCard(direction) {
        const card = this.container.querySelector('.swipe-card');
        if (!card || this.currentIndex >= this.currentProfiles.length) return;

        const currentProfile = this.currentProfiles[this.currentIndex];
        
        // Animate card out
        card.classList.add(`swipe-${direction}`);
        
        try {
            // Send swipe to backend
            const response = await api.swipeProfile(currentProfile.id, direction);
            
            // Check for match
            if (response.match) {
                setTimeout(() => this.showMatchPopup(response.match_data), 300);
            }
            
        } catch (error) {
            console.error('Swipe failed:', error);
        }

        // Move to next card
        this.currentIndex++;
        setTimeout(() => {
            card.remove();
            this.renderCurrentCard();
        }, 300);
    }

    resetCard() {
        const card = this.container.querySelector('.swipe-card');
        if (!card) return;

        card.style.transform = 'translate(0, 0) rotate(0deg)';
        card.style.opacity = '1';
        this.currentX = 0;
        this.currentY = 0;
    }

    renderCurrentCard() {
        if (this.currentIndex >= this.currentProfiles.length) {
            this.showNoMoreProfiles();
            return;
        }

        const profile = this.currentProfiles[this.currentIndex];
        const cardHTML = this.createCardHTML(profile);
        
        this.container.innerHTML = cardHTML;
    }

    createCardHTML(profile) {
        return `
            <div class="swipe-card" data-profile-id="${profile.id}">
                <img src="${profile.photo_url || '/static/img/profile-placeholder.jpg'}" 
                     alt="${profile.name}" class="card-image">
                <div class="card-content">
                    <div class="card-header">
                        <div>
                            <div class="card-name">${profile.name}</div>
                            <div class="card-location">${profile.location}</div>
                        </div>
                        <div class="card-age">${profile.age}</div>
                    </div>
                    <div class="card-bio">${profile.bio}</div>
                    <div class="card-footer">
                        <div class="card-rating">
                            ⭐ ${profile.average_rating || profile.rating}
                        </div>
                        <div class="card-price">${profile.hourly_rate || profile.price} pts</div>
                    </div>
                </div>
            </div>
        `;
    }

    showMatchPopup(matchData) {
        const popup = document.createElement('div');
        popup.className = 'match-overlay';
        popup.innerHTML = `
            <div class="match-popup">
                <div class="match-title">IT'S A MATCH! 🎉</div>
                <div class="match-profiles">
                    <img src="${matchData.user_photo || '/static/img/profile-placeholder.jpg'}" class="match-avatar" alt="You">
                    <img src="${matchData.guide_photo || '/static/img/profile-placeholder.jpg'}" class="match-avatar" alt="${matchData.guide_name}">
                </div>
                <div class="match-message">
                    Możesz teraz porozmawiać z ${matchData.guide_name}!
                </div>
                <div class="match-actions">
                    <button class="match-btn btn-chat" onclick="goToChat(${matchData.match_id})">
                        Napisz wiadomość
                    </button>
                    <button class="match-btn btn-continue" onclick="closeMatch()">
                        Kontynuuj swipowanie
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(popup);
        popup.style.display = 'block';
        
        // Auto close after 5 seconds
        setTimeout(() => {
            if (popup.parentNode) {
                closeMatch();
            }
        }, 5000);
    }

    showNoMoreProfiles() {
        this.container.innerHTML = `
            <div class="no-profiles">
                <h3>Brak nowych profili</h3>
                <p>Sprawdź później lub rozszerz swoje preferencje</p>
                <button onclick="location.reload()" class="reload-btn">
                    Odśwież
                </button>
            </div>
        `;
    }

    updateDirectionIndicators() {
        // Visual feedback during drag
        const absX = Math.abs(this.currentX);
        const absY = Math.abs(this.currentY);
        
        // You can add visual indicators here
        // like colored overlays showing like/dislike
    }
}

// === UTILITY FUNCTIONS ===
function showLoading(show) {
    const existing = document.querySelector('.loading');
    if (existing) existing.remove();
    
    if (show) {
        const loading = document.createElement('div');
        loading.className = 'loading';
        loading.innerHTML = '<div class="spinner"></div>';
        document.querySelector('.swipe-container').appendChild(loading);
    }
}

function showError(message) {
    const toast = document.createElement('div');
    toast.className = 'error-toast';
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #ff6b6b;
        color: white;
        padding: 15px 20px;
        border-radius: 10px;
        z-index: 10000;
    `;
    
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

function closeMatch() {
    const overlay = document.querySelector('.match-overlay');
    if (overlay) overlay.remove();
}

function goToChat(matchId) {
    window.location.href = `/chat/${matchId}`;
}

// === INITIALIZE WHEN DOM IS READY ===
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.swipe-container')) {
        window.swipeManager = new SwipeManager();
    }
});
