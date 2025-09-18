/**
 * Authentication Manager for SECRIMPO KeyAuth Integration
 */
class AuthManager {
    constructor() {
        this.licenseKey = localStorage.getItem('secrimpo_license');
        this.isAuthenticated = false;
        this.userPermissions = {};
        this.userInfo = {};
        this.apiBase = 'http://127.0.0.1:8000';
    }
    
    /**
     * Authenticate user with license key
     */
    async authenticate(licenseKey) {
        try {
            const response = await fetch(`${this.apiBase}/auth/validate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${licenseKey}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.licenseKey = licenseKey;
                this.isAuthenticated = true;
                this.userPermissions = data.permissions;
                this.userInfo = data.user;
                
                localStorage.setItem('secrimpo_license', licenseKey);
                
                console.log('✅ Authentication successful:', data.user);
                return { success: true, data };
            } else {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Invalid license key');
            }
        } catch (error) {
            console.error('❌ Authentication failed:', error);
            return { success: false, error: error.message };
        }
    }
    
    /**
     * Get authorization headers for API requests
     */
    getAuthHeaders() {
        return {
            'Authorization': `Bearer ${this.licenseKey}`,
            'Content-Type': 'application/json'
        };
    }
    
    /**
     * Check if user has specific permission
     */
    hasPermission(permission) {
        return this.userPermissions[permission] || false;
    }
    
    /**
     * Get user information
     */
    getUserInfo() {
        return this.userInfo;
    }
    
    /**
     * Check if user is admin
     */
    isAdmin() {
        return this.userInfo.subscription === 'admin';
    }
    
    /**
     * Check if user is agent or higher
     */
    isAgent() {
        return ['admin', 'agent'].includes(this.userInfo.subscription);
    }
    
    /**
     * Logout user
     */
    logout() {
        this.licenseKey = null;
        this.isAuthenticated = false;
        this.userPermissions = {};
        this.userInfo = {};
        localStorage.removeItem('secrimpo_license');
        console.log('👋 User logged out');
    }
    
    /**
     * Check current authentication status
     */
    async checkAuthStatus() {
        if (!this.licenseKey) {
            return false;
        }
        
        try {
            const response = await fetch(`${this.apiBase}/auth/validate`, {
                method: 'POST',
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const data = await response.json();
                this.isAuthenticated = true;
                this.userPermissions = data.permissions;
                this.userInfo = data.user;
                return true;
            } else {
                this.logout();
                return false;
            }
        } catch (error) {
            console.error('Auth check failed:', error);
            this.logout();
            return false;
        }
    }
    
    /**
     * Auto-refresh token if needed
     */
    async refreshAuth() {
        if (this.licenseKey) {
            return await this.checkAuthStatus();
        }
        return false;
    }
    
    /**
     * Get formatted user display
     */
    getUserDisplay() {
        if (!this.isAuthenticated) {
            return 'Not authenticated';
        }
        
        const subscriptionLabels = {
            'admin': '👑 Administrator',
            'agent': '🎖️ Agent',
            'viewer': '👁️ Viewer',
            'restricted': '🔒 Restricted'
        };
        
        return `${subscriptionLabels[this.userInfo.subscription] || this.userInfo.subscription} - ${this.userInfo.username}`;
    }
}

// Global instance
window.authManager = new AuthManager();

// Auto-setup axios interceptors when available
if (typeof axios !== 'undefined') {
    // Request interceptor to add auth headers
    axios.interceptors.request.use(
        config => {
            if (authManager.isAuthenticated) {
                config.headers = { ...config.headers, ...authManager.getAuthHeaders() };
            }
            return config;
        },
        error => Promise.reject(error)
    );
    
    // Response interceptor to handle auth errors
    axios.interceptors.response.use(
        response => response,
        error => {
            if (error.response && error.response.status === 401) {
                console.log('🔒 Authentication expired, redirecting to login');
                authManager.logout();
                window.location.href = 'login.html';
            }
            return Promise.reject(error);
        }
    );
}