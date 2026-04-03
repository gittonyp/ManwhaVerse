<script>
  import { onMount } from "svelte";
  import { link,push } from "../lib/router.svelte.js";
  import { Search, Menu, User, BookOpen, LogIn, LogOut } from "lucide-svelte";

  let isMobileMenuOpen = $state(false);
  let searchTerm = $state("");  
  // Auth state - passed as props or managed internally
  let { isLoggedIn = false, userId = null } = $props();
  
  function toggleMobileMenu() {
    isMobileMenuOpen = !isMobileMenuOpen;
  }
  
  onMount(async () => {
        // Check auth
        const storedUser = localStorage.getItem("user");
        if (storedUser) {
            try {
                const user = JSON.parse(storedUser);
                isLoggedIn = true;
                userId = user.id;
            } catch (e) {
                console.error("Auth error", e);
            }
        }
    });
    
  function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    window.location.href = "/";
  }

  // let searchterm=$state("")
  function handleSearch() {
    if (searchTerm.trim()) {
      // encodeURIComponent handles special characters like '?' or '#' in titles
     push(`/search/${encodeURIComponent(searchTerm)}`);
     searchTerm = "";
    }
  }
</script>

<nav class="navbar">
  <div class="container">
    <div class="logo">
      <a href="/" use:link>
        <BookOpen color="#8b5cf6" size={28} />
        <span>Manwha<span class="highlight">Verse</span></span>
      </a>
    </div>

    <!-- Desktop Menu -->
    <div class="desktop-menu">
      <a href="/" use:link>Home</a>
      <a href="#/bookmarks" use:link>Bookmarks</a>
    </div>

    <div class="actions">
      <div class="search-bar">
  <Search size={18} class="search-icon" />
  <input
  type="text"
  placeholder="Search..."
  bind:value={searchTerm}
  onkeydown={(e) => e.key === 'Enter' && handleSearch()}
/>
</div>

      {#if isLoggedIn && userId}
        <div class="user-menu">
          <button class="icon-btn user-btn" aria-label="Profile">
            <User size={20} />
            <span class="username">{userId.username}</span>
          </button>
          <button
            class="icon-btn"
            onclick={logout}
            aria-label="Logout"
            title="Logout"
          >
            <LogOut size={20} />
          </button>
        </div>
      {:else}
        <a href="#/login" use:link class="login-btn">
          <LogIn size={18} />
          <span>Login</span>
        </a>
      {/if}

      <button
        class="mobile-toggle"
        onclick={toggleMobileMenu}
        aria-label="Menu"
      >
        <Menu size={24} />
      </button>
    </div>
  </div>
</nav>

{#if isMobileMenuOpen}
  <div class="mobile-menu">
    <a href="/" use:link onclick={toggleMobileMenu}>Home</a>
    <a href="#/bookmarks" use:link onclick={toggleMobileMenu}>Bookmarks</a>
    {#if !isLoggedIn}
      <a
        href="#/login"
        use:link
        onclick={toggleMobileMenu}
        class="mobile-login"
      >
        <LogIn size={18} />
        Login
      </a>
    {:else}
      <a href="#/profile" use:link onclick={toggleMobileMenu}>
        <User size={18} />
        Profile
      </a>
      <a
        href="#"
        onclick={(e) => {
          e.preventDefault();
          logout();
        }}
        class="mobile-logout"
      >
        <LogOut size={18} />
        Logout
      </a>
    {/if}
  </div>
{/if}

<style>
  .navbar {
    position: relative;
    top: 0;
    z-index: 100;
    background: rgba(10, 10, 10, 0.8);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    padding: var(--spacing-md) 0;
    transition: background var(--transition-normal);
  }

  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 var(--spacing-lg);
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  /* Logo */
  .logo a {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-primary);
    text-decoration: none;
  }

  .highlight {
    color: var(--accent-primary);
  }

  /* Desktop Menu */
  .desktop-menu {
    display: none;
    gap: var(--spacing-xl);
  }

  @media (min-width: 768px) {
    .desktop-menu {
      display: flex;
    }
  }

  .desktop-menu :global(a) {
    font-size: 0.95rem;
    font-weight: 500;
    color: var(--text-secondary);
  }

  .desktop-menu :global(a:hover),
  .desktop-menu :global(a[aria-current="page"]) {
    color: var(--text-primary);
  }

  /* Actions */
  .actions {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
  }

  .search-bar {
    display: none;
    align-items: center;
    background: var(--bg-secondary);
    border-radius: var(--radius-full);
    padding: 0.5rem 1rem;
    border: 1px solid transparent;
    transition: all var(--transition-fast);
  }

  @media (min-width: 640px) {
    .search-bar {
      display: flex;
    }
  }

  .search-bar:focus-within {
    border-color: var(--accent-primary);
    box-shadow: 0 0 0 2px var(--accent-glow);
  }

  .search-bar input {
    background: transparent;
    border: none;
    color: var(--text-primary);
    margin-left: var(--spacing-sm);
    outline: none;
    width: 200px;
    font-size: 0.9rem;
  }

  .search-bar :global(.search-icon) {
    color: var(--text-secondary);
  }

  .icon-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-primary);
    padding: var(--spacing-sm);
    border-radius: var(--radius-full);
    transition: background var(--transition-fast);
  }

  .icon-btn:hover {
    background: var(--bg-tertiary);
    color: var(--accent-primary);
  }

  /* Login Button */
  .login-btn {
    display: none;
    align-items: center;
    gap: var(--spacing-xs);
    padding: 0.5rem 1rem;
    background: var(--accent-primary);
    color: white;
    border-radius: var(--radius-full);
    font-weight: 600;
    font-size: 0.9rem;
    text-decoration: none;
    transition: all var(--transition-fast);
  }

  @media (min-width: 640px) {
    .login-btn {
      display: flex;
    }
  }

  .login-btn:hover {
    background: var(--accent-secondary);
    transform: translateY(-1px);
    box-shadow: 0 4px 15px var(--accent-glow);
  }

  .user-menu {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
  }

  .user-btn {
    gap: var(--spacing-xs);
  }

  .username {
    font-size: 0.9rem;
    font-weight: 500;
    display: none;
  }

  @media (min-width: 640px) {
    .username {
      display: inline;
    }
  }

  .mobile-toggle {
    display: block;
    color: var(--text-primary);
  }

  @media (min-width: 768px) {
    .mobile-toggle {
      display: none;
    }
  }

  /* Mobile Menu */
  .mobile-menu {
    position: fixed;
    top: 73px; /* approximate height of navbar */
    left: 0;
    right: 0;
    background: var(--bg-primary);
    padding: var(--spacing-lg);
    border-bottom: 1px solid var(--border-color);
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
    z-index: 99;
  }

  .mobile-menu :global(a) {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    font-size: 1.1rem;
    padding: var(--spacing-sm);
    border-radius: var(--radius-md);
  }

  .mobile-menu :global(a:hover) {
    background: var(--bg-secondary);
    color: var(--accent-primary);
  }

  .mobile-login {
    color: var(--accent-primary);
    font-weight: 600;
  }
</style>
