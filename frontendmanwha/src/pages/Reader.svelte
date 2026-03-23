<script>
  import { onMount } from "svelte";
  import {
    ArrowLeft,
    ArrowRight,
    ChevronUp,
    MessageSquare,
    Home,
    List,
  } from "lucide-svelte";
  import { link, navigate, push } from "../lib/router.svelte.js";
  import { api } from "../lib/api";

  let { id } = $props(); // Chapter ID (numeric)

  let chapter = $state(null);
  let allChapters = $state([]);
  let prevChapter = $state(null);
  let nextChapter = $state(null);

  let loading = $state(true);
  let error = $state(null);
  let showScrollTop = $state(false);

  // Comments
  let comments = $state([]);
  let newComment = $state("");
  let submittingComment = $state(false);
  let isLoggedIn = $state(false);
  let userId = $state(null);

  // Load data when ID changes
  async function loadChapter(currentId) {
    if (!currentId) return;
    console.log("[Reader] Loading chapter ID:", currentId);

    loading = true;
    error = null;
    // Don't clear chapter immediately to avoid flash if possible, but for correctness let's clear or handle UI
    // chapter = null;

    try {
      // 1. Fetch current chapter details
      const chapData = await api.chapters.getById(currentId);
      chapter = chapData;
      console.log("[Reader] Chapter loaded:", chapter);

      // 2. Fetch comments for this chapter (using mangaUrl and chapterId)
      if (chapter.manwhaUrl) {
        // Fetch comments in parallel with chapter list
        const [commentsRes, chaptersRes] = await Promise.all([
          api.comments.getAll(chapter.manwhaUrl, currentId),
          api.manwhas.getChapters(chapter.manwhaUrl),
        ]);

        comments = commentsRes || [];
        allChapters = chaptersRes || [];

        // Calculate Prev/Next
        const idx = allChapters.findIndex((c) => c.id == currentId);
        prevChapter = null;
        nextChapter = null;

        if (idx !== -1) {
          // Next chapter (chronologically) -> index - 1
          if (idx > 0) nextChapter = allChapters[idx - 1];
          // Prev chapter (chronologically) -> index + 1
          if (idx < allChapters.length - 1) prevChapter = allChapters[idx + 1];
        }
      }
    } catch (e) {
      console.error("[Reader] API Error:", e);
      error = "Failed to load chapter.";
    } finally {
      loading = false;
    }
  }

  $effect(() => {
    loadChapter(id);
  });

  onMount(() => {
    // Check auth
    const storedUser = localStorage.getItem("user");
    if (storedUser) {
      try {
        const user = JSON.parse(storedUser);
        isLoggedIn = true;
        userId = user.id;
      } catch (e) {}
    }

    // Scroll to top listener
    const handleScroll = () => {
      showScrollTop = window.scrollY > 500;
    };
    window.addEventListener("scroll", handleScroll);

    return () => window.removeEventListener("scroll", handleScroll);
  });

  function goBack() {
    window.history.back();
  }

  function scrollToTop() {
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function handleChapterChange(event) {
    const selectedId = event.target.value;
    if (selectedId && selectedId != id) {
      push(`/read/${selectedId}`);
    }
  }

  async function handlePostComment() {
    if (!newComment.trim()) return;

    submittingComment = true;
    try {
      const comment = await api.comments.add(
        userId,
        chapter.manwhaUrl,
        newComment,
        id,
      );
      comments = [comment, ...comments];
      newComment = "";
    } catch (e) {
      console.error("Failed to post comment", e);
      alert("Failed to post comment. Please try again.");
    } finally {
      submittingComment = false;
    }
  }
</script>

<div class="reader">
  {#if loading}
    <div class="loading">
      <div class="spinner"></div>
      <p>Loading Chapter...</p>
    </div>
  {:else if error}
    <div class="error">{error}</div>
  {:else if chapter}
    <div class="controls top">
      <div class="nav-left">
        <button onclick={goBack} class="icon-btn" title="Back">
          <ArrowLeft size={20} />
        </button>
        {#if chapter.manwhaUrl}
          <a
            href={`#/details/${encodeURIComponent(chapter.manwhaUrl)}`}
            class="manga-link"
          >
            {chapter.manwhaTitle || "Manga Details"}
          </a>
        {/if}
      </div>

      <div class="chapter-info-center">
        {#if allChapters.length > 0}
          <select
            value={chapter.id}
            onchange={handleChapterChange}
            class="chapter-select"
          >
            {#each allChapters as ch}
              <option value={ch.id}>{ch.title}</option>
            {/each}
          </select>
        {:else}
          <span class="chapter-curr-title">{chapter.title}</span>
        {/if}
      </div>

      <div class="nav-right">
        {#if prevChapter}
          <a
            href={`#/read/${prevChapter.id}`}
            class="icon-btn"
            title="Previous Chapter"
          >
            <ChevronUp size={20} style="transform: rotate(-90deg)" />
          </a>
        {:else}
          <div class="spacer-btn"></div>
        {/if}

        {#if nextChapter}
          <a
            href={`#/read/${nextChapter.id}`}
            class="icon-btn"
            title="Next Chapter"
          >
            <ChevronUp size={20} style="transform: rotate(90deg)" />
          </a>
        {:else}
          <div class="spacer-btn"></div>
        {/if}
      </div>
    </div>

    <div class="pages">
      {#each chapter.images || [] as image, index}
        <img
          src={api.getImageUrl(image.imagePath)}
          alt={`Page ${image.pageNumber}`}
          loading={index < 3 ? "eager" : "lazy"}
        />
      {/each}

      {#if !chapter.images || chapter.images.length === 0}
        <div class="no-pages">
          <p>No pages available for this chapter.</p>
        </div>
      {/if}
    </div>

    <!-- Chapter Comments -->
    <div class="reader-comments">
      <div class="section-header">
        <h3><MessageSquare size={20} /> Chapter Discussion</h3>
      </div>

      <div class="comments-content">
        {#if isLoggedIn}
          <div class="comment-input-area">
            <textarea
              bind:value={newComment}
              placeholder="Discuss this chapter..."
              rows="3"
              disabled={submittingComment}
            ></textarea>
            <div class="comment-actions">
              <button
                class="btn-primary"
                onclick={handlePostComment}
                disabled={submittingComment || !newComment.trim()}
              >
                {submittingComment ? "Posting..." : "Post"}
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
            <p class="no-comments">No comments yet.</p>
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
    </div>

    <div class="controls bottom">
      <div class="nav-buttons">
        {#if prevChapter}
          <a href={`#/read/${prevChapter.id}`} class="btn-secondary">
            Prev Chapter
          </a>
        {/if}
        {#if nextChapter}
          <a href={`#/read/${nextChapter.id}`} class="btn-primary">
            Next Chapter
          </a>
        {/if}
      </div>
    </div>

    {#if showScrollTop}
      <button class="scroll-top" onclick={scrollToTop}>
        <ChevronUp size={24} />
      </button>
    {/if}
  {/if}
</div>

<style>
  .reader {
    background: #000;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  .controls {
    width: 100%;
    padding: var(--spacing-sm) var(--spacing-lg);
    background: rgba(20, 20, 20, 0.95);
    backdrop-filter: blur(10px);
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: relative;
    z-index: 50;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }

  .controls.top {
    top: 0;
    height: 60px;
  }

  .nav-left,
  .nav-right {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    flex: 1;
  }

  .nav-right {
    justify-content: flex-end;
  }

  .icon-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: transparent;
    border: none;
    color: var(--text-secondary);
    cursor: pointer;
    transition: all 0.2s;
  }

  .icon-btn:hover {
    background: rgba(255, 255, 255, 0.1);
    color: white;
  }

  .manga-link {
    color: white;
    font-weight: 600;
    text-decoration: none;
    font-size: 0.95rem;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 200px;
  }

  .manga-link:hover {
    color: var(--accent-primary);
  }

  .chapter-info-center {
    flex: 2;
    text-align: center;
    overflow: hidden;
    display: flex;
    justify-content: center;
  }

  .chapter-curr-title {
    font-size: 0.9rem;
    color: var(--text-secondary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    display: block;
  }

  .chapter-select {
    background: transparent;
    color: var(--text-secondary);
    border: none;
    font-size: 0.95rem;
    font-weight: 600;
    text-align: center;
    cursor: pointer;
    outline: none;
    max-width: 100%;
    padding: 6px 12px;
    border-radius: 4px;
    font-family: inherit;
    transition: all 0.2s;
  }

  .chapter-select:hover {
    background: rgba(255, 255, 255, 0.1);
    color: white;
  }

  .chapter-select option {
    background: #222;
    color: white;
    text-align: left;
  }

  .pages {
    max-width: 800px;
    width: 100%;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    background: #111;
    min-height: 80vh;
  }

  .pages img {
    width: 100%;
    display: block;
  }

  .no-pages {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 50vh;
    color: var(--text-secondary);
  }

  /* Comments */
  .reader-comments {
    max-width: 800px;
    margin: 0 auto;
    width: 100%;
    padding: var(--spacing-2xl) var(--spacing-lg);
    background: #0a0a0a;
  }

  .section-header {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    margin-bottom: var(--spacing-lg);
    color: var(--text-primary);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    padding-bottom: var(--spacing-sm);
  }

  .comments-content {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-lg);
  }

  .comment-input-area {
    background: rgba(255, 255, 255, 0.05);
    padding: var(--spacing-md);
    border-radius: var(--radius-md);
  }

  .comment-input-area textarea {
    width: 100%;
    background: transparent;
    border: none;
    color: white;
    resize: vertical;
    outline: none;
    min-height: 80px;
    font-family: inherit;
  }

  .comment-actions {
    display: flex;
    justify-content: flex-end;
    margin-top: var(--spacing-sm);
  }

  .comment-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
  }

  .comment-item {
    background: rgba(255, 255, 255, 0.03);
    padding: var(--spacing-md);
    border-radius: var(--radius-md);
  }

  .comment-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 4px;
    font-size: 0.85rem;
  }

  .comment-user {
    font-weight: 600;
    color: var(--accent-primary);
  }

  .comment-date {
    color: var(--text-secondary);
  }

  .comment-content {
    line-height: 1.5;
    color: #ddd;
    font-size: 0.95rem;
  }

  .controls.bottom {
    justify-content: center;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    padding: var(--spacing-lg);
    background: #000;
    position: relative; /* Not sticky */
  }

  .nav-buttons {
    display: flex;
    gap: var(--spacing-lg);
  }

  .btn-primary,
  .btn-secondary {
    padding: 10px 20px;
    border-radius: var(--radius-full);
    font-weight: 600;
    text-decoration: none;
    transition: all 0.2s;
  }

  .btn-primary {
    background: var(--accent-primary);
    color: white;
  }

  .btn-primary:hover {
    background: var(--accent-secondary);
  }

  .btn-secondary {
    background: rgba(255, 255, 255, 0.1);
    color: white;
  }

  .btn-secondary:hover {
    background: rgba(255, 255, 255, 0.2);
  }

  .guest-comment-prompt {
    text-align: center;
    padding: var(--spacing-lg);
    background: rgba(255, 255, 255, 0.05);
    border-radius: var(--radius-md);
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--spacing-md);
  }

  .scroll-top {
    position: fixed;
    bottom: 80px;
    right: 20px;
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: var(--accent-primary);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: var(--shadow-lg);
    transition: all var(--transition-fast);
    z-index: 100;
    border: none;
    cursor: pointer;
  }

  .scroll-top:hover {
    background: var(--accent-secondary);
    transform: translateY(-2px);
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

  .spacer-btn {
    width: 36px;
  }
</style>
