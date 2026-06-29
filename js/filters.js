(function () {
    const chips = document.querySelectorAll('.chip');
    const search = document.querySelector('.filter-search');
    const cards = Array.from(document.querySelectorAll('.organizations .cards-grid .card'));

    if (!cards.length) {
        return;
    }

    function cardSearchText(card) {
        const title = card.querySelector('h3')?.textContent || '';
        const description = card.querySelector('p')?.textContent || '';
        return (title + ' ' + description).toLowerCase();
    }

    function applyFilters() {
        const activeChip = document.querySelector('.chip.is-active');
        const continent = activeChip ? activeChip.getAttribute('data-continent') : 'all';
        const q = (search?.value || '').trim().toLowerCase();

        cards.forEach(card => {
            const cardCont = card.getAttribute('data-continent') || '';
            let matchCont;
            if (continent === 'all') {
                matchCont = true;
            } else if (continent === 'visitable') {
                matchCont = card.getAttribute('data-visitable') === 'true';
            } else {
                matchCont = continent === cardCont;
            }
            const matchText = q === '' || cardSearchText(card).includes(q);
            card.hidden = !(matchCont && matchText);
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
})();
