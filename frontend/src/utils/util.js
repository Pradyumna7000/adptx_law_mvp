// Simple API utility functions using Choreo connection pattern
const apiUrl = window?.configs?.apiUrl ? window.configs.apiUrl : "http://localhost:8000";

// Generic request method
const apiRequest = async (endpoint, options = {}) => {
    const url = `${apiUrl}${endpoint}`;
    const config = {
        headers: {
            'Content-Type': 'application/json',
            ...options.headers,
        },
        ...options,
        // Add timeout for long-running requests
        signal: AbortSignal.timeout(120000), // 2 minutes timeout
    };

    try {
        const response = await fetch(url, config);
        
        if (!response.ok) {
            if (response.status === 504) {
                throw new Error('Request timed out. The AI is taking too long to process. Please try again with a simpler request.');
            }
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
export const apiUploadFile = async (endpoint, file, fields = {}, options = {}) => {
    const formData = new FormData();
    formData.append('file', file);
    Object.entries(fields || {}).forEach(([k, v]) => formData.append(k, v));
    
    const url = `${apiUrl}${endpoint}`;
    const config = {
        method: 'POST',
        headers: {
            ...options.headers,
        },
        body: formData,
        // Add timeout for long-running requests
        signal: AbortSignal.timeout(180000), // 3 minutes timeout for PDF processing
    };

    try {
        const response = await fetch(url, config);
        
        if (!response.ok) {
            if (response.status === 504) {
                throw new Error('PDF processing timed out. The file might be too large or complex. Please try with a smaller PDF or simpler request.');
            }
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
