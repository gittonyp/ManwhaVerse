<script>
  import { onMount } from "svelte";
  import { ArrowRight } from "lucide-svelte";
  import { link } from "../lib/router.svelte.js";
  import ManwhaCard from "../components/ManwhaCard.svelte";
  import { api } from "../lib/api";

  let featured = $state(null);
  let allManwhas = $state([]);
  let loading = $state(true);
  let error = $state(null);

  // Derived value for featured ID (the 'url' field is the slug)
  let featuredId = $derived(featured ? api.getId(featured) : "");

  onMount(async () => {
    console.log("[Home] Mounted, starting API fetch...");
    try {
      const [featuredRes, popularRes] = await Promise.all([
        api.manwhas.getFeatured(),
        api.manwhas.getPopular(),
      ]);
      console.log("[Home] API success:", { featuredRes, popularRes });
      featured = featuredRes;
      allManwhas = popularRes;
    } catch (e) {
      console.error("[Home] API Error:", e);
      error =
        "Failed to load content. Please ensure backend is running on port 8081.";
    } finally {
      loading = false;
    }
  });
</script>

<div class="home">
  {#if loading}
    <div class="loading-state">
      <div class="spinner"></div>
      <p>Loading ManwhaVerse...</p>
    </div>
  {:else if error}
    <div class="error-state">
      <p>{error}</p>
      <button onclick={() => window.location.reload()}>Retry</button>
    </div>
  {:else if featured}
    <!-- Hero Section -->
    <!-- <section class="hero">
      <div
        class="hero-bg"
        style="background-image: url({api.getImageUrl(featured.bannerImage)})"
      ></div>
      <div class="overlay"></div>

      <div class="container hero-content">
        <div class="badge">Featured Series</div>
        <h1>{featured.title}</h1>
        <p class="description">{featured.description}</p>

        <div class="meta-info">
          <span class="author">By {featured.author}</span>
          <span class="status">{featured.status}</span>
          <span class="views">{featured.views} views</span>
        </div>

        <div class="actions">
          <a
            href={`#/details/${encodeURIComponent(featuredId)}`}
            use:link
            class="btn btn-primary"
          >
            Read Now <ArrowRight size={20} />
          </a>
          <a
            href={`#/details/${encodeURIComponent(featuredId)}`}
            use:link
            class="btn btn-secondary"
          >
            More Info
          </a>
        </div>
      </div>
    </section> -->

    <!-- All Manwhas Section -->
    <section class="section">
      <div class="container">
        <div class="section-header">
          <h2>Browse All Manwhas</h2>
          <span class="manwha-count">{allManwhas.length} titles</span>
        </div>
        <div class="grid">
          {#each allManwhas as item}
            <ManwhaCard
              id={api.getId(item)}
              title={item.title}
              author={item.author}
              status={item.status}
              views={item.views}
              image={api.getImageUrl(item.bannerImage)}
              lastChapter={item.lastChapter}
            />
          {/each}
        </div>
      </div>
    </section>
  {/if}
</div>

<style>
  .hero {
    position: relative;
    height: 80vh;
    min-height: 600px;
    display: flex;
    align-items: center;
    overflow: hidden;
  }

  .hero-bg {
    position: absolute;
    inset: 0;
    background-size: cover;
    background-position: center;
    z-index: 0;
    animation: zoom 20s infinite alternate;
  }

  @keyframes zoom {
    from {
      transform: scale(1);
    }
    to {
      transform: scale(1.1);
    }
  }

  .overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(
      to right,
      rgba(10, 10, 10, 0.95) 0%,
      rgba(10, 10, 10, 0.7) 50%,
      transparent 100%
    );
    z-index: 1;
  }

  /* Add bottom fade */
  .overlay::after {
    content: "";
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 150px;
    background: linear-gradient(to top, var(--bg-primary), transparent);
  }

  .hero-content {
    position: relative;
    z-index: 2;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 var(--spacing-lg);
    width: 100%;
  }

  .badge {
    display: inline-block;
    background: var(--accent-secondary);
    color: white;
    padding: 4px 12px;
    border-radius: var(--radius-full);
    font-size: 0.85rem;
    font-weight: 600;
    margin-bottom: var(--spacing-md);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  h1 {
    font-size: 3.5rem;
    font-weight: 800;
    margin-bottom: var(--spacing-md);
    line-height: 1.1;
    max-width: 800px;
    background: linear-gradient(to right, #fff, #aaa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .description {
    font-size: 1.1rem;
    color: var(--text-secondary);
    max-width: 600px;
    margin-bottom: var(--spacing-md);
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  .meta-info {
    display: flex;
    gap: var(--spacing-lg);
    margin-bottom: var(--spacing-xl);
    font-size: 0.9rem;
    color: var(--text-secondary);
  }

  .meta-info .status {
    color: var(--accent-primary);
  }

  .actions {
    display: flex;
    gap: var(--spacing-md);
  }

  .btn {
    display: inline-flex;
    align-items: center;
    gap: var(--spacing-sm);
    padding: 0.8rem 1.5rem;
    border-radius: var(--radius-full);
    font-weight: 600;
    transition: all var(--transition-fast);
    text-decoration: none;
  }

  .btn-primary {
    background: var(--accent-primary);
    color: white;
  }

  .btn-primary:hover {
    background: var(--accent-secondary);
    transform: translateY(-2px);
    box-shadow: 0 4px 15px var(--accent-glow);
  }

  .btn-secondary {
    background: rgba(255, 255, 255, 0.1);
    color: white;
    backdrop-filter: blur(10px);
  }

  .btn-secondary:hover {
    background: rgba(255, 255, 255, 0.2);
  }

  .section {
    padding: var(--spacing-2xl) 0;
  }

  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 var(--spacing-lg);
  }

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-xl);
  }

  .section-header h2 {
    font-size: 1.5rem;
    font-weight: 700;
  }

  .manwha-count {
    color: var(--text-secondary);
    font-size: 0.9rem;
  }

  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: var(--spacing-lg);
  }

  /* Loading & Error States */
  .loading-state,
  .error-state {
    height: 80vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: var(--spacing-md);
    color: var(--text-secondary);
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

  .error-state button {
    padding: 8px 16px;
    background: var(--accent-primary);
    color: white;
    border-radius: var(--radius-md);
    cursor: pointer;
  }

  .error-state button:hover {
    background: var(--accent-secondary);
  }
</style>
