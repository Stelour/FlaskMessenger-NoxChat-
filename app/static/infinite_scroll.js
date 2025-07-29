function initInfiniteScroll() {
    const container = document.querySelector('.results-container');
    if (!container) return;

    let page = 1;
    const url = container.dataset.url;
    const query = container.dataset.query || '';
    const view = container.dataset.view || '';
    let loading = false;
    let hasMore = container.dataset.hasMore === 'true';

    const sentinel = document.createElement('div');
    sentinel.className = 'scroll-sentinel';
    container.after(sentinel);

    async function loadMore() {
        if (loading || !hasMore) return;
        loading = true;
        page += 1;
        const params = new URLSearchParams({ page });
        if (query) params.append('q', query);
        if (view) params.append('view', view);
        const resp = await fetch(`${url}?${params.toString()}`, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        if (resp.ok) {
            const data = await resp.json();
            container.insertAdjacentHTML('beforeend', data.html);
            hasMore = data.has_more;
            if (!hasMore) {
                observer.disconnect();
            }
        }
        loading = false;
        checkFill();
    }

    function checkFill() {
        if (hasMore && sentinel.getBoundingClientRect().top <= window.innerHeight) {
            loadMore();
        }
    }

    const observer = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting) {
            loadMore();
        }
    });

    observer.observe(sentinel);

    checkFill();
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initInfiniteScroll);
} else {
    initInfiniteScroll();
}