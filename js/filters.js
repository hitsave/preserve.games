(function () {
    document.querySelectorAll('[data-filterable]').forEach(section => {
        const chipAttr = section.dataset.chipAttr || 'category';
        const chips = section.querySelectorAll('.chip');
        const search = section.querySelector('.filter-search');
        const resultsEl = section.querySelector('.filter-results');
        const showCount = section.dataset.showCount === 'true';
        const page = section.closest('.page');
        const cards = Array.from(page.querySelectorAll('.cards-grid .card'));

        if (!cards.length) {
            return;
        }

        function cardSearchText(card) {
            const title = card.querySelector('h3')?.textContent || '';
            const description = card.querySelector('p')?.textContent || '';
            const badge = card.querySelector('.card-badge')?.textContent || '';
            return (title + ' ' + description + ' ' + badge).toLowerCase();
        }

        function matchesFilter(card, filterValue) {
            if (filterValue === 'all') {
                return true;
            }
            if (chipAttr === 'continent' && filterValue === 'visitable') {
                return card.getAttribute('data-visitable') === 'true';
            }
            if (chipAttr === 'section' && filterValue === 'visit-in-person') {
                return card.getAttribute('data-section') === 'organizations'
                    && card.getAttribute('data-visitable') === 'true';
            }
            return filterValue === card.getAttribute(`data-${chipAttr}`);
        }

        function updateResults(visibleCount, filterValue, q) {
            if (!showCount || !resultsEl) {
                return;
            }
            const total = cards.length;
            const filtered = filterValue !== 'all' || q !== '';
            if (!filtered) {
                resultsEl.textContent = `${total} links. Search or pick a category to narrow the list.`;
                return;
            }
            if (visibleCount === 0) {
                resultsEl.textContent = 'No matches. Try a different search or category.';
                return;
            }
            resultsEl.textContent = `Showing ${visibleCount} of ${total}`;
        }

        function applyFilters() {
            const activeChip = section.querySelector('.chip.is-active');
            const filterValue = activeChip ? activeChip.getAttribute(`data-${chipAttr}`) : 'all';
            const q = (search?.value || '').trim().toLowerCase();
            let visibleCount = 0;

            cards.forEach(card => {
                const matchFilter = matchesFilter(card, filterValue);
                const matchText = q === '' || cardSearchText(card).includes(q);
                const visible = matchFilter && matchText;
                card.hidden = !visible;
                if (visible) {
                    visibleCount += 1;
                }
            });

            updateResults(visibleCount, filterValue, q);
        }

        chips.forEach(chip => {
            chip.addEventListener('click', () => {
                chips.forEach(c => c.classList.remove('is-active'));
                chip.classList.add('is-active');
                applyFilters();
            });
        });

        if (search) {
            search.addEventListener('input', applyFilters);
        }

        applyFilters();
    });
})();
