// API utility functions for connecting to Choreo backend
const API_BASE_URL = "/choreo-apis/adptxmvp/backend/v1/api";

// Get API key from environment or config
const getApiKey = () => {
    // You can set this in your Choreo frontend environment variables
    return process.env.REACT_APP_CHOREO_API_KEY || "your-api-key-here";
};

// Generic request method with authentication
const apiRequest = async (endpoint, options = {}) => {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
        headers: {
            'Content-Type': 'application/json',
            'apikey': getApiKey(), // Add API key header
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

// File upload (for PDFs)
export const apiUploadFile = async (endpoint, file, options = {}) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
        method: 'POST',
        headers: {
            'apikey': getApiKey(), // Add API key header
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

// Export API_BASE_URL for direct use
export { API_BASE_URL };
