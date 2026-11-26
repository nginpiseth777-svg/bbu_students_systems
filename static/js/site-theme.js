(() => {
    const root = document.documentElement;
    const toggle = document.querySelector('[data-theme-toggle]');
    const storageKey = 'bbu-theme';

    root.dataset.theme = window.localStorage.getItem(storageKey) === 'dark' ? 'dark' : 'light';
    if (!toggle) {
        return;
    }

    const updateToggle = () => {
        const isDark = root.dataset.theme === 'dark';
        toggle.innerHTML = isDark
            ? '<i class="fa-solid fa-sun" aria-hidden="true"></i>'
            : '<i class="fa-solid fa-moon" aria-hidden="true"></i>';
        toggle.setAttribute('aria-label', isDark ? 'បើក light mode' : 'បើក dark mode');
        toggle.setAttribute('aria-pressed', String(isDark));
    };

    updateToggle();
    toggle.addEventListener('click', () => {
        root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
        window.localStorage.setItem(storageKey, root.dataset.theme);
        updateToggle();
    });

    if (window.matchMedia('(pointer: fine)').matches) {
        let frame = 0;
        let pointerEvent;

        document.addEventListener('pointermove', (event) => {
            pointerEvent = event;
            if (frame) {
                return;
            }

            frame = window.requestAnimationFrame(() => {
                root.style.setProperty('--page-pointer-x', `${pointerEvent.clientX}px`);
                root.style.setProperty('--page-pointer-y', `${pointerEvent.clientY}px`);
                frame = 0;
            });
        });
    }
})();
