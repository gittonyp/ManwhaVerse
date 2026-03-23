<script>
    let { imgsrc, name, latestChapterNo } = $props();
</script>

<div class="card">
    <img src={imgsrc} alt="{name} Logo" />
    <h2>{name}</h2>
    <h3>Latest Chapter: {latestChapterNo}</h3>
</div>

<style>
    .card {
        background: var(--bg-secondary);
        border-radius: var(--radius-md);
        padding: var(--spacing-md);
    }

    img {
        width: 100%;
        border-radius: var(--radius-sm);
    }

    h2 {
        margin-top: var(--spacing-sm);
        font-size: 1rem;
    }

    h3 {
        color: var(--text-secondary);
        font-size: 0.85rem;
    }
</style>
