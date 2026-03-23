<script>
  import { onMount } from "svelte";
  import {
    Star,
    List,
    Play,
    User,
    Eye,
    BookOpen,
    Heart,
    MessageSquare,
  } from "lucide-svelte";
  import { link, push } from "../lib/router.svelte.js";
  import { api } from "../lib/api";

  let { id } = $props(); // Route param

  let data = $state(null);
  let chapters = $state([]);
  let loading = $state(true);
  let error = $state(null);

  let isBookmarked = $state(false);
  let isLoggedIn = $state(false);
  let userId = $state(null);

  // Comments state
  let comments = $state([]);
  let newComment = $state("");
  let submittingComment = $state(false);

  // Split genres string into array
  let genresList = $derived(
    data?.genres ? data.genres.split(",").map((g) => g.trim()) : [],
  );

  onMount(async () => {
    console.log("[Details] Fetching details for ID:", id);

    // Check auth
    const storedUser = localStorage.getItem("user");
    if (storedUser) {
      try {
        const user = JSON.parse(storedUser);
        isLoggedIn = true;
        userId = user.id;

        // Check bookmark status
        try {
          const res = await api.bookmarks.check(userId, id);
          isBookmarked = res.bookmarked;
        } catch (e) {
          console.error("Failed to check bookmark", e);
        }
      } catch (e) {}
    }

    try {
      const [detailsRes, chaptersRes, commentsRes] = await Promise.all([
        api.manwhas.getById(id),
        api.manwhas.getChapters(id),
        api.comments.getAll(id),
      ]);
      console.log("[Details] API success:", { detailsRes, chaptersRes });
      data = detailsRes;
      chapters = chaptersRes || [];
      comments = commentsRes || [];
    } catch (e) {
      console.error("[Details] API Error:", e);
      error = "Failed to load details.";
    } finally {
      loading = false;
    }
  });

  async function handleBookmarkToggle() {
    if (!isLoggedIn) {
      push("/login");
      return;
    }

    // Optimistic toggle
    isBookmarked = !isBookmarked;

    try {
      const res = await api.bookmarks.toggle(userId, id);
      isBookmarked = res.bookmarked;
    } catch (e) {
      console.error("Failed to toggle bookmark", e);
      // Revert on error
      isBookmarked = !isBookmarked;
    }
  }

  async function handlePostComment() {
    if (!newComment.trim()) return;

    submittingComment = true;
    try {
      const comment = await api.comments.add(userId, id, newComment);
      comments = [comment, ...comments]; // Prepend
      newComment = "";
    } catch (e) {
      console.error("Failed to post comment", e);
      alert("Failed to post comment. Please try again.");
    } finally {
      submittingComment = false;
    }
  }
</script>

<div class="details-page">
  {#if loading}
    <div class="loading">
      <div class="spinner"></div>
      <p>Loading...</p>
    </div>
  {:else if error}
    <div class="error">{error}</div>
  {:else if data}
    <div
      class="banner"
      style="background-image: url({api.getImageUrl(data.bannerImage)})"
    >
      <div class="overlay"></div>
    </div>

    <div class="container content">
      <div class="cover-section">
        <img
          src={api.getImageUrl(data.bannerImage)}
          alt={data.title}
          class="cover"
        />
      </div>

      <div class="info-section">
        <h1>{data.title}</h1>

        <div class="meta">
          <div class="meta-item">
           
            <span></span>
          </div>
          <span
            class="status"
            class:ongoing={data.status === "Ongoing"}
            class:completed={data.status === "Completed"}
          >
            Ongoing
          </span>
          <div class="meta-item">
            <Eye size={16} />
            <span>{data.views} Views</span>
          </div>
          <div class="meta-item">
            <BookOpen size={16} />
            <span>{data.lastChapter} Chapters</span>
          </div>
        </div>

        <div class="genres">
          {#each genresList as genre}
            <span class="tag">{genre}</span>
          {/each}
        </div>

        <p class="description">{data.description}</p>

        <div class="actions">
          {#if chapters.length > 0}
            <a
              href={`#/read/${chapters[0]?.id}`}
              use:link
              class="btn btn-primary"
            >
              <Play size={18} />
              Start Reading
            </a>
          {/if}

          <button
            class="btn btn-secondary bookmark-btn"
            onclick={handleBookmarkToggle}
            class:active={isBookmarked}
          >
            <Heart size={20} fill={isBookmarked ? "currentColor" : "none"} />
            {isBookmarked ? "Bookmarked" : "Bookmark"}
          </button>
        </div>
      </div>
    </div>

    <div class="container chapters-section">
      <div class="section-header">
        <h2><List size={24} /> Chapters ({chapters.length})</h2>
      </div>

      {#if chapters.length === 0}
        <p class="no-chapters">No chapters available yet.</p>
      {:else}
        <div class="chapter-list">
          {#each chapters as chapter}
            <a href={`#/read/${chapter.id}`} use:link class="chapter-item">
              <div class="chapter-info">
                <span class="chapter-title">{chapter.title}</span>
                <span class="chapter-number">Chapter {chapter.number}</span>
              </div>
              <span class="chapter-date">
                {chapter.releaseDate
                  ? new Date(chapter.releaseDate).toLocaleDateString()
                  : ""}
              </span>
            </a>
          {/each}
        </div>
      {/if}
    </div>

    <div class="container comments-section">
      <div class="section-header">
        <h2><MessageSquare size={24} /> Discussion</h2>
      </div>

      {#if isLoggedIn}
        <div class="comment-input-area">
          <textarea
            bind:value={newComment}
            placeholder="Share your thoughts about this manwha..."
            rows="3"
            disabled={submittingComment}
          ></textarea>
          <div class="comment-actions">
            <button
              class="btn-primary"
              onclick={handlePostComment}
              disabled={submittingComment || !newComment.trim()}
            >
              {submittingComment ? "Posting..." : "Post Comment"}
            </button>
          </div>
        </div>
      {:else}
        <div class="guest-comment-prompt">
          <p>Login to join the discussion.</p>
          <button class="btn-secondary" onclick={() => push("/login")}>
            Sign In
          </button>
        </div>
      {/if}

      <div class="comment-list">
        {#if comments.length === 0}
          <p class="no-comments">
            No comments yet. Be the first to start the discussion!
          </p>
        {:else}
          {#each comments as comment}
            <div class="comment-item">
              <div class="comment-header">
                <span class="comment-user">{comment.username}</span>
                <span class="comment-date"
                  >{new Date(comment.createdAt).toLocaleDateString()}</span
                >
              </div>
              <p class="comment-content">{comment.content}</p>
            </div>
          {/each}
        {/if}
      </div>
    </div>
  {/if}
</div>

<style>
  .details-page {
    position: relative;
    padding-bottom: var(--spacing-2xl);
  }

  .banner {
    height: 350px;
    background-size: cover;
    background-position: center top;
    position: relative;
  }

  .overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(
      to bottom,
      rgba(10, 10, 10, 0.3),
      var(--bg-primary)
    );
  }

  .container {
    max-width: 1200px;
    margin: 0 auto;
  }

  .content {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xl);
    position: relative;
    margin-top: -120px;
    z-index: 10;
    padding: 0 var(--spacing-lg);
  }

  @media (min-width: 768px) {
    .content {
      flex-direction: row;
      align-items: flex-start;
    }
  }

  .cover {
    width: 220px;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-lg);
  }

  .info-section {
    flex: 1;
    padding-top: var(--spacing-lg);
  }

  h1 {
    font-size: 2.5rem;
    line-height: 1.1;
    margin-bottom: var(--spacing-md);
    font-weight: 800;
  }

  .meta {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: var(--spacing-lg);
    margin-bottom: var(--spacing-md);
    color: var(--text-secondary);
    font-size: 0.9rem;
  }

  .meta-item {
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .status {
    padding: 4px 12px;
    border-radius: var(--radius-full);
    font-size: 0.85rem;
    font-weight: 600;
  }

  .status.ongoing {
    background: rgba(34, 197, 94, 0.2);
    color: #22c55e;
  }

  .status.completed {
    background: rgba(59, 130, 246, 0.2);
    color: #3b82f6;
  }

  .genres {
    display: flex;
    flex-wrap: wrap;
    gap: var(--spacing-sm);
    margin-bottom: var(--spacing-lg);
  }

  .tag {
    background: var(--bg-tertiary);
    padding: 6px 14px;
    border-radius: var(--radius-full);
    font-size: 0.85rem;
    color: var(--text-secondary);
    transition: all var(--transition-fast);
  }

  .tag:hover {
    background: var(--accent-primary);
    color: white;
  }

  .description {
    color: var(--text-secondary);
    margin-bottom: var(--spacing-xl);
    max-width: 800px;
    line-height: 1.7;
  }

  .btn {
    display: inline-flex;
    align-items: center;
    gap: var(--spacing-sm);
  }

  .btn-primary {
    padding: 14px 28px;
    background: var(--accent-primary);
    color: white;
    border-radius: var(--radius-full);
    font-weight: 600;
    font-size: 1rem;
    transition: all var(--transition-fast);
  }

  .btn-primary:hover {
    background: var(--accent-secondary);
    transform: translateY(-2px);
    box-shadow: 0 4px 15px var(--accent-glow);
  }

  .bookmark-btn {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 14px 20px;
    border-radius: var(--radius-full);
    border: 1px solid rgba(255, 255, 255, 0.1);
    background: rgba(255, 255, 255, 0.05);
    color: white;
    cursor: pointer;
    transition: all 0.2s;
  }

  .bookmark-btn:hover {
    background: rgba(255, 255, 255, 0.1);
  }

  .bookmark-btn.active {
    color: #ef4444; /* Red for heart */
    border-color: rgba(239, 68, 68, 0.3);
    background: rgba(239, 68, 68, 0.1);
  }

  .chapters-section {
    margin-top: var(--spacing-2xl);
    padding: 0 var(--spacing-lg);
  }

  .section-header {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    margin-bottom: var(--spacing-lg);
    padding-bottom: var(--spacing-sm);
    border-bottom: 1px solid var(--border-color);
  }

  .section-header h2 {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    font-size: 1.5rem;
  }

  .no-chapters {
    color: var(--text-secondary);
    text-align: center;
    padding: var(--spacing-xl);
  }

  .chapter-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
  }

  .chapter-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 14px 16px;
    background: var(--bg-secondary);
    border-radius: var(--radius-md);
    color: var(--text-primary);
    transition: all var(--transition-fast);
    border: 1px solid transparent;
  }

  .chapter-item:hover {
    background: var(--bg-tertiary);
    border-color: var(--accent-primary);
    transform: translateX(4px);
  }

  .chapter-info {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .chapter-title {
    font-weight: 500;
  }

  .chapter-number {
    font-size: 0.8rem;
    color: var(--text-secondary);
  }

  .chapter-date {
    color: var(--text-secondary);
    font-size: 0.85rem;
  }

  .loading,
  .error {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 60vh;
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

  /* Comments */
  .comments-section {
    margin-top: var(--spacing-2xl);
    padding: 0 var(--spacing-lg);
  }

  .comment-input-area {
    margin-bottom: var(--spacing-xl);
    background: var(--bg-secondary);
    padding: var(--spacing-md);
    border-radius: var(--radius-md);
    border: 1px solid var(--border-color);
  }

  .comment-input-area textarea {
    width: 100%;
    background: transparent;
    border: none;
    color: var(--text-primary);
    font-size: 1rem;
    resize: vertical;
    outline: none;
    font-family: inherit;
    margin-bottom: var(--spacing-md);
  }

  .comment-actions {
    display: flex;
    justify-content: flex-end;
  }

  .guest-comment-prompt {
    background: var(--bg-secondary);
    padding: var(--spacing-lg);
    border-radius: var(--radius-md);
    text-align: center;
    border: 1px solid var(--border-color);
    margin-bottom: var(--spacing-xl);
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--spacing-sm);
  }

  .comment-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
  }

  .comment-item {
    background: var(--bg-secondary);
    padding: var(--spacing-md);
    border-radius: var(--radius-md);
  }

  .comment-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: var(--spacing-xs);
    font-size: 0.9rem;
  }

  .comment-user {
    font-weight: 600;
    color: var(--accent-primary);
  }

  .comment-date {
    color: var(--text-secondary);
    font-size: 0.8rem;
  }

  .comment-content {
    line-height: 1.5;
    color: var(--text-primary);
  }

  .no-comments {
    color: var(--text-secondary);
    text-align: center;
    padding: var(--spacing-lg);
  }
</style>
