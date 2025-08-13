// API utility functions for connecting to Choreo backend
const getApiUrl = () => {
    return window?.configs?.apiUrl || "/";
};

// Base API client
const apiClient = {
    baseURL: getApiUrl(),
    
    // Generic request method
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        };

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
    },

    // GET request
    async get(endpoint, options = {}) {
        return this.request(endpoint, { ...options, method: 'GET' });
    },

    // POST request
    async post(endpoint, data, options = {}) {
        return this.request(endpoint, {
            ...options,
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    // File upload (for PDFs)
    async uploadFile(endpoint, file, options = {}) {
        const formData = new FormData();
        formData.append('file', file);
        
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            method: 'POST',
            headers: {
                ...options.headers,
            },
            body: formData,
        };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('File upload failed:', error);
            throw error;
        }
    },
};

// Specific API endpoints
export const api = {
    // Health check
    health: () => apiClient.get('/api/health'),
    
    // Chat endpoint
    chat: (message) => apiClient.post('/api/chat', { message }),
    
    // PDF analysis
    analyzePdf: (file) => apiClient.uploadFile('/api/analyze-pdf', file),
    
    // File upload
    uploadFile: (file) => apiClient.uploadFile('/upload', file),
};

export default apiClient;
