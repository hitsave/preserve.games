(function () {
    const pages = document.querySelectorAll('.page');
    const navLinks = document.querySelectorAll('[data-nav]');
    const siteTitle = document.body.dataset.siteTitle || 'preserve.games';
    const routes = new Set(['home', 'organizations', 'visit-in-person', 'guides', 'communities', 'opensource', 'resources', 'browse']);

    const pageTitles = {
        home: siteTitle,
        organizations: 'Organizations | preserve.games',
        'visit-in-person': 'Visit in Person | preserve.games',
        guides: 'Guides | preserve.games',
        communities: 'Communities | preserve.games',
        opensource: 'Open Source | preserve.games',
        resources: 'Resources | preserve.games',
        browse: 'Browse All | preserve.games',
    };

    function initHeroTagline() {
        const taglineEl = document.getElementById('hero-tagline');
        const dataEl = document.getElementById('hero-taglines');
        if (!taglineEl || !dataEl) {
            return;
        }

        let taglines;
        try {
            taglines = JSON.parse(dataEl.textContent || '[]');
        } catch {
            return;
        }

        if (!Array.isArray(taglines) || taglines.length <= 1) {
            return;
        }

        const pick = taglines[Math.floor(Math.random() * taglines.length)];
        const lines = pick?.lines;
        if (!Array.isArray(lines) || !lines.length) {
            return;
        }

        taglineEl.innerHTML = lines
            .map(line => `<span class="hero-tagline-line">${line.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')}</span>`)
            .join('');
    }

    function getRoute() {
        const hash = location.hash.slice(1);
        return routes.has(hash) ? hash : 'home';
    }

    function showPage(route) {
        pages.forEach(page => {
            page.hidden = page.dataset.page !== route;
        });

        navLinks.forEach(link => {
            link.classList.toggle('is-active', link.dataset.nav === route);
        });

        document.title = pageTitles[route] || siteTitle;
        window.scrollTo(0, 0);
    }

    window.addEventListener('hashchange', () => showPage(getRoute()));

    initHeroTagline();

    if (!location.hash || !routes.has(location.hash.slice(1))) {
        location.replace('#home');
    }
    showPage(getRoute());

    const tracks = [...document.querySelectorAll('.logo-marquee-track')];
    const MARQUEE_BASE_DURATION = 100;

    function waitForMarqueeImages(track) {
        const imgs = track.querySelectorAll('img');
        if (!imgs.length) {
            return Promise.resolve();
        }

        return Promise.all([...imgs].map(img => {
            if (img.complete) {
                return Promise.resolve();
            }
            return new Promise(resolve => {
                img.addEventListener('load', resolve, { once: true });
                img.addEventListener('error', resolve, { once: true });
            });
        }));
    }

    Promise.all(tracks.map(waitForMarqueeImages)).then(() => {
        const reference = document.querySelector('.logo-marquee-reverse .logo-marquee-track');
        const refTrack = reference || tracks[0];
        if (refTrack) {
            const speed = (refTrack.scrollWidth / 2) / MARQUEE_BASE_DURATION;
            tracks.forEach(track => {
                const duration = (track.scrollWidth / 2) / speed;
                track.style.setProperty('--marquee-duration', `${duration}s`);
            });
        }
        tracks.forEach(track => track.classList.add('is-ready'));
    });
})();
