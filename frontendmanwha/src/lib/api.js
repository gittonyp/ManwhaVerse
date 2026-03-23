import { API_BASE_URL, STATIC_BASE_URL } from '../config.js';

export const api = {
    // Helper to construct full image URLs
    getImageUrl(path) {
        if (!path) return '';
        if (path.startsWith('http')) return path;
        // Ensure path starts with /
        const cleanPath = path.startsWith('/') ? path : '/' + path;
        return `${STATIC_BASE_URL}${cleanPath}`;
    },

    // Helper to get the URL slug from a manwha object
    // The API uses 'url' field as the unique identifier (e.g., "solo-leveling")
    getId(manwha) {
        if (!manwha) return '';
        return manwha.url || manwha.id || '';
    },

    async get(endpoint) {
        const fullUrl = `${API_BASE_URL}${endpoint}`;
        console.log(`[API] Requesting: ${fullUrl}`);
        try {
            const response = await fetch(fullUrl);
            console.log(`[API] Response ${response.status} for ${endpoint}`);
            if (!response.ok) {
                throw new Error(`API Error ${response.status}: ${response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`[API] Fetch failed for ${endpoint}:`, error);
            throw error;
        }
    },

    manwhas: {
        // Get featured manwha
        getFeatured: () => api.get('/manwhas/featured'),

        // Get list of popular manwhas
        getPopular: () => api.get('/manwhas/popular'),

        // Get manwha details by URL slug - using query param because IDs contain slashes
        getById: (id) => api.get(`/manwhas/details?id=${encodeURIComponent(id)}`),

        // Get chapters for a manwha by URL slug - using query param because IDs contain slashes
        getChapters: (id) => api.get(`/manwhas/chapters?id=${encodeURIComponent(id)}`),

        //search using the manwha name in the navbar
        getSearch: (searchTitle) => api.get(`/manwhas/search/${(searchTitle)}`),
    },

    chapters: {
        // Get a single chapter by numeric ID
        getById: (id) => api.get(`/chapters/${id}`),
    },

    bookmarks: {
        getAll: (userId) => api.get(`/bookmarks?userId=${userId}`),

        check: (userId, mangaUrl) => api.get(`/bookmarks/check?userId=${userId}&mangaUrl=${encodeURIComponent(mangaUrl)}`),

        toggle: async (userId, mangaUrl) => {
            const fullUrl = `${API_BASE_URL}/bookmarks/toggle`;
            const response = await fetch(fullUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ userId, mangaUrl })
            });
            if (!response.ok) throw new Error('Failed to toggle bookmark');
            return await response.json();
        }
    },

    comments: {
        getAll: (mangaUrl, chapterId) => {
            let url = `/comments?mangaUrl=${encodeURIComponent(mangaUrl)}`;
            if (chapterId) url += `&chapterId=${chapterId}`;
            return api.get(url);
        },

        add: async (userId, mangaUrl, content, chapterId) => {
            const fullUrl = `${API_BASE_URL}/comments`;
            const body = { userId, mangaUrl, content };
            if (chapterId) body.chapterId = chapterId;

            const response = await fetch(fullUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(body)
            });
            if (!response.ok) throw new Error('Failed to post comment');
            return await response.json();
        }
    }
};
