<script>
  import { api } from "../lib/api.js";
    import { link } from "../lib/router.svelte.js";
    import { Star, Eye, User, BookOpen } from "lucide-svelte";
    import { API_BASE_URL } from "../config.js";

    let { id, title, author = "", status = "", views = "", image ,lastChapter} = $props();
</script>

<a href={`#/details/${encodeURIComponent(id)}`} use:link class="card">
    <div class="image-container">
        <img src={`${API_BASE_URL}/manwhas/banner?id=${id}`} alt={title} loading="lazy" />  <div class="overlay">
            <span class="view-btn">View Details</span>
        </div>
        {#if status}
            <span
                class="status-badge"
                class:ongoing={status === "Ongoing"}
                class:completed={status === "Completed"}
            >
                {status}
            </span>
        {/if}
    </div>

    <div class="info">
        <h3 class="title">{title}</h3>
        <div class="meta">
            {#if lastChapter}
                <div  class="lastChapter">
                    <BookOpen size={12} />
                    <span>{lastChapter}</span>
                </div>
            {/if}
            {#if views}
                <div class="views">
                    <Eye size={12} />
                    <span>{views}</span>
                </div>
            {/if}
        </div>
    </div>
</a>

<style>
    .card {
        display: block;
        border-radius: var(--radius-lg);
        overflow: hidden;
        background: var(--bg-secondary);
        transition:
            transform var(--transition-fast),
            box-shadow var(--transition-fast);
    }

    .card:hover {
        transform: translateY(-8px);
        box-shadow: var(--shadow-glow);
    }

    .image-container {
        position: relative;
        aspect-ratio: 2/3;
        overflow: hidden;
    }

    .image-container img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform var(--transition-normal);
    }

    .card:hover .image-container img {
        transform: scale(1.05);
    }

    .status-badge {
        position: absolute;
        top: 8px;
        left: 8px;
        padding: 4px 8px;
        border-radius: var(--radius-sm);
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .status-badge.ongoing {
        background: rgba(34, 197, 94, 0.9);
        color: white;
    }

    .status-badge.completed {
        background: rgba(59, 130, 246, 0.9);
        color: white;
    }

    .overlay {
        position: absolute;
        inset: 0;
        background: linear-gradient(
            to top,
            rgba(0, 0, 0, 0.9) 0%,
            transparent 60%
        );
        display: flex;
        align-items: flex-end;
        justify-content: center;
        padding-bottom: var(--spacing-lg);
        opacity: 0;
        transition: opacity var(--transition-fast);
    }

    .card:hover .overlay {
        opacity: 1;
    }

    .view-btn {
        background: var(--accent-primary);
        color: white;
        padding: 8px 16px;
        border-radius: var(--radius-full);
        font-size: 0.85rem;
        font-weight: 600;
        transition: background var(--transition-fast);
    }

    .card:hover .view-btn {
        background: var(--accent-secondary);
    }

    .info {
        padding: var(--spacing-md);
    }

    .title {
        font-size: 0.95rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: var(--spacing-sm);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .meta {
        display: flex;
        align-items: center;
        gap: var(--spacing-md);
        font-size: 0.8rem;
        color: var(--text-secondary);
    }

    .lastChapter,
    .views {
        display: flex;
        align-items: center;
        gap: 4px;
    }
</style>
