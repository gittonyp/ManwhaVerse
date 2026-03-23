// Simple hash-based router for Svelte 5
import { writable } from 'svelte/store';

// Current route store
export const currentRoute = writable(parseHash(window.location.hash));

// Parse hash into route object
function parseHash(hash) {
    const cleanHash = hash.replace(/^#/, '') || '/';
    const [path, queryString] = cleanHash.split('?');
    const params = {};

    // Parse path segments
    const segments = path.split('/').filter(Boolean);

        // console.log(segments)
    // Check for route patterns
    if (segments[0] === 'details' && segments[1]) {
        return {
            path: '/details/:id',
            params: { id: decodeURIComponent(segments[1]) },
            fullPath: path
        };
    }
     if (segments[0] === 'search' && segments[1]) {
        return {
            path: '/search/:searchTitle',
            params: {searchTitle : decodeURIComponent(segments[1])},
            fullPath: path
        };
    }

    if (segments[0] === 'read' && segments[1]) {
        return {
            path: '/read/:id',
            params: { id: decodeURIComponent(segments[1]) },
            fullPath: path
        };
    }
    if (segments[0] === 'login') {
        return {
            path: '/login',
            params: {},
            fullPath: path
        };
    }

    if (segments[0] === 'bookmarks') {
        return {
            path: '/bookmarks',
            params: {},
            fullPath: path
        };
    }

   

    return { path: '/' + segments.join('/') || '/', params: {}, fullPath: path };
}

// Navigate to a new route
export function navigate(path) {
    window.location.hash = path;
}

// Alias for navigate (for compatibility)
export function push(path) {
    navigate(path.startsWith('#') ? path : '#' + path);
}

// Link action for Svelte 5
export function link(node) {
    function handleClick(event) {
        event.preventDefault();
        const href = node.getAttribute('href');
        navigate(href);
    }

    node.addEventListener('click', handleClick);

    return {
        destroy() {
            node.removeEventListener('click', handleClick);
        }
    };
}

// Listen for hash changes
if (typeof window !== 'undefined') {
    window.addEventListener('hashchange', () => {
        currentRoute.set(parseHash(window.location.hash));
        window.scrollTo(0, 0);
    });
}
