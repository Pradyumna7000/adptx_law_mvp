// API utility functions for connecting to backend (works locally and on Choreo)
// Detect environment and build the correct base URL
const isLocal = () => typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');

// Allow overriding via env at build time
const CHOREO_API_BASE = (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_CHOREO_API_BASE)
    || "/choreo-apis/adptxmvp/backend/v1.0"; // default; override in Choreo if needed

// Derive base when hosted under Choreo proxies to handle v1 vs v1.0 automatically
const deriveChoreoBase = () => {
    if (typeof window === 'undefined') return CHOREO_API_BASE;
    const parts = window.location.pathname.split('/').filter(Boolean);
    const apiIdx = parts.indexOf('choreo-apis');
    if (apiIdx === -1) return CHOREO_API_BASE;
    const vIdx = parts.findIndex((seg, i) => i > apiIdx && /^v\d/.test(seg));
    if (vIdx === -1) return CHOREO_API_BASE;
    return '/' + parts.slice(0, vIdx + 1).join('/');
};

const LOCAL_API_BASE = (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_LOCAL_API_BASE)
    || "http://localhost:8000"; // Default local dev port

const API_BASE_URL = isLocal() ? LOCAL_API_BASE : deriveChoreoBase();

const isChoreo = () => typeof window !== 'undefined' && (window.location.pathname.startsWith('/choreo-apis') || window.location.hostname.includes('choreoapps.dev') || window.location.hostname.includes('choreoapis.dev'));

// Get API key from environment or config
const getApiKey = () => {
    const key = (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_CHOREO_API_KEY) || '';
    return key;
};

// Generic request method with API key
const apiRequest = async (endpoint, options = {}) => {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
        headers: {
            'Content-Type': 'application/json',
            ...(isChoreo() ? { 'apikey': getApiKey() } : {}), // Add API key only on Choreo
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
};

// GET request
export const apiGet = async (endpoint, options = {}) => {
    return apiRequest(endpoint, { ...options, method: 'GET' });
};

// POST request
export const apiPost = async (endpoint, data, options = {}) => {
    return apiRequest(endpoint, {
        ...options,
        method: 'POST',
        body: JSON.stringify(data),
    });
};

// File upload (for PDFs) with API key
export const apiUploadFile = async (endpoint, file, fields = {}, options = {}) => {
    const formData = new FormData();
    formData.append('file', file);
    Object.entries(fields || {}).forEach(([k, v]) => formData.append(k, v));
    
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
        method: 'POST',
        headers: {
            ...(isChoreo() ? { 'apikey': getApiKey() } : {}), // Add API key only on Choreo
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
};

// Specific API endpoints
export const api = {
    // Health check
    health: () => apiGet('/api/health'),
    
    // Chat endpoint
    chat: (message) => apiPost('/api/chat', { message, user_id: 'user123' }),
    
    // PDF analysis
    analyzePdf: (file, fields) => apiUploadFile('/api/analyze-pdf', file, fields),
    
    // File upload
    uploadFile: (file) => apiUploadFile('/upload', file),
};

export default api;
