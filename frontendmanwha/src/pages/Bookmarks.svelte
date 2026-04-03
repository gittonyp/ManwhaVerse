<script>
    import { onMount } from "svelte";
    import { push } from "../lib/router.svelte.js";
    import { api } from "../lib/api";
    import { LogIn } from "lucide-svelte";
    import ManwhaCard from "../components/ManwhaCard.svelte";

    // Auth state
    let isLoggedIn = $state(false);
    let userId = $state(null);

    // Data state
    let bookmarks = $state([]);
    let loading = $state(true);

    onMount(async () => {
        // Check auth
        const storedUser = localStorage.getItem("user");
        if (storedUser) {
            try {
                const user = JSON.parse(storedUser);
                isLoggedIn = true;
                userId = user.id;

                await fetchBookmarks();
            } catch (e) {
                console.error("Auth error", e);
            }
        }
        loading = false;
    });

    async function fetchBookmarks() {
        try {
            bookmarks = await api.bookmarks.getAll(userId);
        } catch (e) {
            console.error("Failed to load bookmarks", e);
        }
    }

    function goToLogin() {
        push("/login");
    }
</script>

<div class="bookmarks-page">
    <div class="container">
        <header class="page-header">
            <h1>My Bookmarks</h1>
            <p>Keep track of your favorite series</p>
        </header>

        {#if loading}
            <div class="loading">
                <div class="spinner"></div>
            </div>
        {:else if !isLoggedIn}
            <div class="guest-state">
                <div class="guest-content">
                    <LogIn size={48} />
                    <h2>Manage Your Reading List</h2>
                    <p>
                        Join ManwhaVerse to save your favorite manwhas and track
                        your progress.
                    </p>
                    <button class="btn-primary" onclick={goToLogin}>
                        Sign In to View Bookmarks
                    </button>
                </div>
            </div>
        {:else if bookmarks.length === 0}
            <div class="empty-state">
                <p>You haven't bookmarked any manwhas yet.</p>
                <button class="btn-secondary" onclick={() => push("/")}>
                    Browse Manwhas
                </button>
            </div>
        {:else}
            <div class="grid">
                {#each bookmarks as item}
                    <ManwhaCard
                        id={api.getId(item)}
                        title={item.title}
                        author={item.author}
                        status={item.status}
                        views={item.views}
                        image={item.imageshow}
                    />
                {/each}
            </div>
        {/if}
    </div>
</div>

<style>
    .bookmarks-page {
        min-height: 80vh;
        padding: var(--spacing-2xl) 0;
    }

    .container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 var(--spacing-lg);
    }

    .page-header {
        margin-bottom: var(--spacing-2xl);
        text-align: center;
    }

    .page-header h1 {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: var(--spacing-xs);
        background: linear-gradient(to right, #fff, #ccc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .page-header p {
        color: var(--text-secondary);
        font-size: 1.1rem;
    }

    /* Guest State */
    .guest-state {
        display: flex;
        justify-content: center;
        padding: var(--spacing-2xl) 0;
    }

    .guest-content {
        background: var(--bg-secondary);
        padding: var(--spacing-2xl);
        border-radius: var(--radius-lg);
        text-align: center;
        max-width: 500px;
        border: 1px solid var(--border-color);
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: var(--spacing-md);
    }

    .guest-content :global(svg) {
        color: var(--accent-primary);
        margin-bottom: var(--spacing-sm);
    }

    .guest-content h2 {
        font-size: 1.5rem;
        font-weight: 700;
    }

    .guest-content p {
        color: var(--text-secondary);
        line-height: 1.6;
        margin-bottom: var(--spacing-sm);
    }

    /* Empty State */
    .empty-state {
        text-align: center;
        padding: var(--spacing-2xl);
        color: var(--text-secondary);
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: var(--spacing-md);
    }

    .grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: var(--spacing-lg);
    }

    .btn-primary {
        background: var(--accent-primary);
        color: white;
        padding: 0.8rem 1.5rem;
        border-radius: var(--radius-full);
        font-weight: 600;
        cursor: pointer;
        transition: all var(--transition-fast);
    }

    .btn-primary:hover {
        background: var(--accent-secondary);
        transform: translateY(-2px);
        box-shadow: 0 4px 15px var(--accent-glow);
    }

    .btn-secondary {
        background: rgba(255, 255, 255, 0.1);
        color: white;
        padding: 0.8rem 1.5rem;
        border-radius: var(--radius-full);
        font-weight: 600;
        cursor: pointer;
        transition: all var(--transition-fast);
    }

    .btn-secondary:hover {
        background: rgba(255, 255, 255, 0.2);
    }

    .loading {
        display: flex;
        justify-content: center;
        padding: var(--spacing-2xl);
    }

    .spinner {
        width: 40px;
        height: 40px;
        border: 3px solid rgba(255, 255, 255, 0.1);
        border-radius: 50%;
        border-top-color: var(--accent-primary);
        animation: spin 1s linear infinite;
    }

    @keyframes spin {
        to {
            transform: rotate(360deg);
        }
    }
</style>
