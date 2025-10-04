// === API CLIENT === 
class APIClient {
    constructor() {
        this.baseURL = '';
    }

    async request(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        const config = { ...defaultOptions, ...options };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    async getProfiles() {
        return this.request('/api/profiles');
    }

    async swipeProfile(profileId, direction) {
        return this.request('/api/swipe', {
            method: 'POST',
            body: JSON.stringify({
                profile_id: profileId,
                direction: direction
            })
        });
    }

    async getMatches() {
        return this.request('/api/matches');
    }

    async getUserPoints() {
        return this.request('/api/user/points');
    }
}

// Global API client instance
const api = new APIClient();
