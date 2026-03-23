<script>
    import { BookOpen, Mail, Lock, Eye, EyeOff } from "lucide-svelte";
    import { link, push } from "../lib/router.svelte.js";
    import { API_BASE_URL } from "../config.js";

    let isLogin = $state(true);
    let showPassword = $state(false);
    let loading = $state(false);
    let error = $state(null);
    let success = $state(null);

    let formData = $state({
        username: "",
        email: "",
        password: "",
        confirmPassword: "",
    });

    function toggleMode() {
        isLogin = !isLogin;
        error = null;
        success = null;
    }

    async function handleSubmit(e) {
        e.preventDefault();
        error = null;
        loading = true;

        try {
            if (!isLogin) {
                // Registration
                if (formData.password !== formData.confirmPassword) {
                    throw new Error("Passwords do not match");
                }

                const res = await fetch(`${API_BASE_URL}/auth/register`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        username: formData.username,
                        email: formData.email,
                        password: formData.password,
                    }),
                });

                const data = await res.json();

                if (!res.ok) {
                    throw new Error(data.message || "Registration failed");
                }

                success = "Account created! Please login.";
                isLogin = true;
                formData = {
                    username: "",
                    email: "",
                    password: "",
                    confirmPassword: "",
                };
            } else {
                // Login
                const res = await fetch(`${API_BASE_URL}/auth/login`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        username: formData.username,
                        password: formData.password,
                    }),
                });

                const data = await res.json();

                if (!res.ok) {
                    throw new Error(data.message || "Login failed");
                }

                // Store token and user info
                localStorage.setItem("token", data.token);
                localStorage.setItem("user", JSON.stringify(data.user));

                // Redirect to home
                push("/");
            }
        } catch (e) {
            error = e.message;
        } finally {
            loading = false;
        }
    }
</script>

<div class="auth-page">
    <div class="auth-container">
        <div class="auth-card">
            <!-- Logo -->
            <a href="/" use:link class="logo">
                <BookOpen color="#8b5cf6" size={32} />
                <span>Manwha<span class="highlight">Verse</span></span>
            </a>

            <h1>{isLogin ? "Welcome Back" : "Create Account"}</h1>
            <p class="subtitle">
                {isLogin
                    ? "Sign in to continue reading"
                    : "Join our community of readers"}
            </p>

            {#if error}
                <div class="alert alert-error">{error}</div>
            {/if}

            {#if success}
                <div class="alert alert-success">{success}</div>
            {/if}

            <form onsubmit={handleSubmit}>
                <div class="form-group">
                    <label for="username">Username</label>
                    <div class="input-wrapper">
                        <Mail size={18} />
                        <input
                            type="text"
                            id="username"
                            placeholder="Enter your username"
                            bind:value={formData.username}
                            required
                        />
                    </div>
                </div>

                {#if !isLogin}
                    <div class="form-group">
                        <label for="email">Email</label>
                        <div class="input-wrapper">
                            <Mail size={18} />
                            <input
                                type="email"
                                id="email"
                                placeholder="Enter your email"
                                bind:value={formData.email}
                                required
                            />
                        </div>
                    </div>
                {/if}

                <div class="form-group">
                    <label for="password">Password</label>
                    <div class="input-wrapper">
                        <Lock size={18} />
                        <input
                            type={showPassword ? "text" : "password"}
                            id="password"
                            placeholder="Enter your password"
                            bind:value={formData.password}
                            required
                        />
                        <button
                            type="button"
                            class="toggle-password"
                            onclick={() => (showPassword = !showPassword)}
                        >
                            {#if showPassword}
                                <EyeOff size={18} />
                            {:else}
                                <Eye size={18} />
                            {/if}
                        </button>
                    </div>
                </div>

                {#if !isLogin}
                    <div class="form-group">
                        <label for="confirmPassword">Confirm Password</label>
                        <div class="input-wrapper">
                            <Lock size={18} />
                            <input
                                type={showPassword ? "text" : "password"}
                                id="confirmPassword"
                                placeholder="Confirm your password"
                                bind:value={formData.confirmPassword}
                                required
                            />
                        </div>
                    </div>
                {/if}

                <button type="submit" class="submit-btn" disabled={loading}>
                    {#if loading}
                        <span class="spinner"></span>
                    {:else}
                        {isLogin ? "Sign In" : "Create Account"}
                    {/if}
                </button>
            </form>

            <p class="toggle-text">
                {isLogin
                    ? "Don't have an account?"
                    : "Already have an account?"}
                <button type="button" class="toggle-btn" onclick={toggleMode}>
                    {isLogin ? "Sign Up" : "Sign In"}
                </button>
            </p>
        </div>
    </div>
</div>

<style>
    .auth-page {
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: var(--spacing-lg);
        background: linear-gradient(135deg, var(--bg-primary) 0%, #1a1a2e 100%);
    }

    .auth-container {
        width: 100%;
        max-width: 420px;
    }

    .auth-card {
        background: var(--bg-secondary);
        border-radius: var(--radius-lg);
        padding: var(--spacing-2xl);
        border: 1px solid var(--border-color);
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    }

    .logo {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: var(--spacing-sm);
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--text-primary);
        text-decoration: none;
        margin-bottom: var(--spacing-xl);
    }

    .highlight {
        color: var(--accent-primary);
    }

    h1 {
        text-align: center;
        font-size: 1.75rem;
        font-weight: 700;
        margin-bottom: var(--spacing-xs);
    }

    .subtitle {
        text-align: center;
        color: var(--text-secondary);
        margin-bottom: var(--spacing-xl);
    }

    .alert {
        padding: var(--spacing-md);
        border-radius: var(--radius-md);
        margin-bottom: var(--spacing-md);
        font-size: 0.9rem;
    }

    .alert-error {
        background: rgba(239, 68, 68, 0.1);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }

    .alert-success {
        background: rgba(34, 197, 94, 0.1);
        color: #22c55e;
        border: 1px solid rgba(34, 197, 94, 0.3);
    }

    .form-group {
        margin-bottom: var(--spacing-md);
    }

    .form-group label {
        display: block;
        font-size: 0.9rem;
        font-weight: 500;
        margin-bottom: var(--spacing-xs);
        color: var(--text-secondary);
    }

    .input-wrapper {
        display: flex;
        align-items: center;
        background: var(--bg-tertiary);
        border-radius: var(--radius-md);
        padding: 0 var(--spacing-md);
        border: 1px solid transparent;
        transition: all var(--transition-fast);
    }

    .input-wrapper:focus-within {
        border-color: var(--accent-primary);
        box-shadow: 0 0 0 3px var(--accent-glow);
    }

    .input-wrapper :global(svg) {
        color: var(--text-secondary);
        flex-shrink: 0;
    }

    .input-wrapper input {
        flex: 1;
        background: transparent;
        border: none;
        padding: var(--spacing-md);
        color: var(--text-primary);
        font-size: 1rem;
        outline: none;
    }

    .toggle-password {
        color: var(--text-secondary);
        padding: var(--spacing-xs);
        cursor: pointer;
    }

    .toggle-password:hover {
        color: var(--text-primary);
    }

    .submit-btn {
        width: 100%;
        padding: var(--spacing-md);
        background: var(--accent-primary);
        color: white;
        border-radius: var(--radius-md);
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all var(--transition-fast);
        display: flex;
        align-items: center;
        justify-content: center;
        gap: var(--spacing-sm);
        margin-top: var(--spacing-lg);
    }

    .submit-btn:hover:not(:disabled) {
        background: var(--accent-secondary);
        transform: translateY(-1px);
        box-shadow: 0 4px 15px var(--accent-glow);
    }

    .submit-btn:disabled {
        opacity: 0.7;
        cursor: not-allowed;
    }

    .spinner {
        width: 20px;
        height: 20px;
        border: 2px solid rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        border-top-color: white;
        animation: spin 1s linear infinite;
    }

    @keyframes spin {
        to {
            transform: rotate(360deg);
        }
    }

    .toggle-text {
        text-align: center;
        margin-top: var(--spacing-xl);
        color: var(--text-secondary);
    }

    .toggle-btn {
        color: var(--accent-primary);
        font-weight: 600;
        cursor: pointer;
        margin-left: var(--spacing-xs);
    }

    .toggle-btn:hover {
        text-decoration: underline;
    }
</style>
