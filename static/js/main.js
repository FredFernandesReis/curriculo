// Main JavaScript — navegação mobile e âncoras
document.addEventListener('DOMContentLoaded', function () {
    const HEADER_OFFSET = 80;

    function closeMobileMenu() {
        const el = document.getElementById('mobileMenu');
        if (!el) return;
        const instance = bootstrap.Offcanvas.getInstance(el);
        if (instance) instance.hide();
    }

    function scrollToHash(hash, smooth) {
        if (!hash || hash === '#') return false;
        const target = document.querySelector(hash);
        if (!target) return false;
        const top = target.getBoundingClientRect().top + window.pageYOffset - HEADER_OFFSET;
        window.scrollTo({ top, behavior: smooth ? 'smooth' : 'auto' });
        return true;
    }

    // Ao carregar com #ancora na URL
    if (window.location.hash) {
        setTimeout(() => scrollToHash(window.location.hash, true), 120);
    }

    // Links com âncora (menu, bottom nav, footer, desktop)
    document.querySelectorAll('a[href*="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href') || '';
            if (href.startsWith('http') || this.target === '_blank') return;

            const hashIndex = href.indexOf('#');
            if (hashIndex === -1) return;

            const path = href.substring(0, hashIndex) || window.location.pathname;
            const hash = href.substring(hashIndex);
            if (!hash || hash === '#') return;

            const currentPath = window.location.pathname.replace(/\/$/, '') || '/';
            const linkPath = path.replace(/\/$/, '') || '/';
            const samePage = !path || linkPath === currentPath || path === '' || href.startsWith('#');

            if (samePage && document.querySelector(hash)) {
                e.preventDefault();
                closeMobileMenu();
                history.pushState(null, '', hash);
                scrollToHash(hash, true);
            } else {
                // Outra página: fecha menu e deixa navegar (hash será aplicado no load)
                closeMobileMenu();
            }
        });
    });

    // Links do offcanvas sem âncora (Início, Criar) — fecha menu sem travar navegação
    document.querySelectorAll('.js-menu-link').forEach(link => {
        link.addEventListener('click', function () {
            const href = this.getAttribute('href') || '';
            if (href.includes('#')) return; // já tratado acima
            closeMobileMenu();
        });
    });

    // Bottom nav: destaque ao rolar nas seções da landing
    const bottomNav = document.querySelector('.mobile-bottom-nav');
    if (bottomNav && document.getElementById('como-funciona')) {
        const map = {
            'como-funciona': 'como',
            'vantagens': 'como',
            'avaliacoes': 'faq',
            'faq': 'faq',
        };

        const setActive = (key) => {
            bottomNav.querySelectorAll('.bottom-nav-item[data-nav]').forEach(el => {
                el.classList.toggle('active', el.dataset.nav === key);
            });
        };

        const observer = new IntersectionObserver(entries => {
            entries.forEach(entry => {
                if (!entry.isIntersecting) return;
                const key = map[entry.target.id];
                if (key) setActive(key);
            });
        }, { rootMargin: '-40% 0px -45% 0px', threshold: 0 });

        Object.keys(map).forEach(id => {
            const el = document.getElementById(id);
            if (el) observer.observe(el);
        });
    }
});

function showAutosave() {
    const indicator = document.getElementById('autosaveIndicator');
    if (indicator) {
        indicator.classList.add('show');
        setTimeout(() => indicator.classList.remove('show'), 2000);
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
