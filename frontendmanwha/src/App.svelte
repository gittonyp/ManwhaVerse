<script>
  import { currentRoute } from "./lib/router.svelte.js";
  import Navbar from "./components/Navbar.svelte";
  import Footer from "./components/Footer.svelte";
  import Home from "./pages/Home.svelte";
  import Details from "./pages/Details.svelte";
  import Reader from "./pages/Reader.svelte";
  import Login from "./pages/Login.svelte";
  import Bookmarks from "./pages/Bookmarks.svelte";
  import { onMount } from "svelte";
  import Search from "./pages/Search.svelte";

  console.log("[App] Initializing App component");

  let isLoggedIn = $state(false);
  let user = $state(null);

  onMount(() => {
    const token = localStorage.getItem("token");
    const storedUser = localStorage.getItem("user");

    if (token && storedUser) {
      try {
        user = JSON.parse(storedUser);
        isLoggedIn = true;
      } catch (e) {
        console.error("Failed to parse user data", e);
        localStorage.removeItem("token");
        localStorage.removeItem("user");
      }
    }
  });
</script>

<div class="app-container">
  {#if $currentRoute.path === "/login"}
    <Login />
  {:else}
    <Navbar {isLoggedIn} {user} />

    <main>
      {#if $currentRoute.path === "/" || $currentRoute.path === ""}
        <Home />
      {:else if $currentRoute.path === "/bookmarks"}
        <Bookmarks />
      {:else if $currentRoute.path === "/details/:id"}
        <Details id={$currentRoute.params.id} />
      {:else if $currentRoute.path === "/read/:id"}
        <Reader id={$currentRoute.params.id} />
      {:else if $currentRoute.path === "/search/:searchTitle"}
        <Search title={$currentRoute.params.searchTitle} />
      {:else}
        <div class="not-found">
          <h2>404</h2>
          <p>Page not found</p>
        </div>
      {/if}
    </main>

    <Footer />
  {/if}
</div>

<style>
  .app-container {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
  }

  main {
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  .not-found {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 50vh;
  }

  .not-found h2 {
    font-size: 4rem;
    color: var(--accent-primary);
    margin-bottom: var(--spacing-md);
  }
</style>
