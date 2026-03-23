<script>
  import { Github, Twitter, Heart } from "lucide-svelte";
</script>

<footer class="footer">
  <div class="container">
    <div class="content">
      <div class="brand">
        <h3>ManwhaVerse</h3>
        <p>Your premium destination for immersive digital comics.</p>
      </div>

      <div class="links">
        <div class="column">
          <h4>Explore</h4>
          <a href="#/popular">Popular</a>
          <a href="#/new">New Releases</a>
          <a href="#/genres">Genres</a>
        </div>
        <div class="column">
          <h4>Community</h4>
          <a href="#/discord">Discord</a>
          <a href="#/about">About Us</a>
          <a href="#/contact">Contact</a>
        </div>
      </div>
    </div>

    <div class="bottom-bar">
      <p>&copy; {new Date().getFullYear()} ManwhaVerse. All rights reserved.</p>
      <div class="socials">
        <a
          href="https://github.com"
          aria-label="Github"
          target="_blank"
          rel="noopener"><Github size={20} /></a
        >
        <a
          href="https://twitter.com"
          aria-label="Twitter"
          target="_blank"
          rel="noopener"><Twitter size={20} /></a
        >
      </div>
    </div>
  </div>
</footer>

<style>
  .footer {
    background: var(--bg-secondary);
    border-top: 1px solid var(--border-color);
    padding: var(--spacing-2xl) 0 var(--spacing-lg);
    margin-top: auto; /* Ensures footer stays at bottom if content is short */
  }

  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 var(--spacing-lg);
  }

  .content {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xl);
    margin-bottom: var(--spacing-xl);
  }

  @media (min-width: 768px) {
    .content {
      flex-direction: row;
      justify-content: space-between;
    }
  }

  .brand h3 {
    font-size: 1.5rem;
    color: var(--accent-primary);
    margin-bottom: var(--spacing-md);
  }

  .brand p {
    color: var(--text-secondary);
    max-width: 300px;
  }

  .links {
    display: flex;
    gap: var(--spacing-2xl);
  }

  .column h4 {
    color: var(--text-primary);
    margin-bottom: var(--spacing-md);
    font-size: 1rem;
  }

  .column a {
    display: block;
    color: var(--text-secondary);
    margin-bottom: var(--spacing-sm);
    font-size: 0.9rem;
  }

  .column a:hover {
    color: var(--accent-primary);
  }

  .bottom-bar {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--spacing-md);
    padding-top: var(--spacing-lg);
    border-top: 1px solid var(--border-color);
  }

  @media (min-width: 768px) {
    .bottom-bar {
      flex-direction: row;
      justify-content: space-between;
    }
  }

  .bottom-bar p {
    color: var(--text-secondary);
    font-size: 0.85rem;
  }

  .socials {
    display: flex;
    gap: var(--spacing-md);
  }

  .socials a {
    color: var(--text-secondary);
    transition: color var(--transition-fast);
  }

  .socials a:hover {
    color: var(--accent-primary);
  }
</style>
