(function () {
    document.querySelectorAll('[data-filterable]').forEach(section => {
        const chipAttr = section.dataset.chipAttr || 'category';
        const chips = section.querySelectorAll('.chip');
        const search = section.querySelector('.filter-search');
        const page = section.closest('.page');
        const cards = Array.from(page.querySelectorAll('.cards-grid .card'));

        if (!cards.length) {
            return;
        }

        function cardSearchText(card) {
            const title = card.querySelector('h3')?.textContent || '';
            const description = card.querySelector('p')?.textContent || '';
            return (title + ' ' + description).toLowerCase();
        }

        function applyFilters() {
            const activeChip = section.querySelector('.chip.is-active');
            const filterValue = activeChip ? activeChip.getAttribute(`data-${chipAttr}`) : 'all';
            const q = (search?.value || '').trim().toLowerCase();

            cards.forEach(card => {
                const cardValue = card.getAttribute(`data-${chipAttr}`) || '';
                let matchFilter;
                if (filterValue === 'all') {
                    matchFilter = true;
                } else if (chipAttr === 'continent' && filterValue === 'visitable') {
                    matchFilter = card.getAttribute('data-visitable') === 'true';
                } else {
                    matchFilter = filterValue === cardValue;
                }
                const matchText = q === '' || cardSearchText(card).includes(q);
                card.hidden = !(matchFilter && matchText);
            });
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
