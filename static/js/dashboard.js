(() => {
    const dashboard = document.querySelector('.student-dashboard');
    const hero = dashboard?.querySelector('.dashboard-hero');
    const glow = dashboard?.querySelector('.dashboard-glow');

    if (
        !dashboard ||
        !hero ||
        !glow ||
        !window.matchMedia('(pointer: fine)').matches
    ) {
        return;
    }

    let frame = 0;
    let pointerEvent;

    dashboard.addEventListener('pointermove', (event) => {
        pointerEvent = event;
        if (frame) {
            return;
        }

        frame = window.requestAnimationFrame(() => {
            const dashboardBounds = dashboard.getBoundingClientRect();
            glow.style.setProperty('--glow-x', `${pointerEvent.clientX - dashboardBounds.left}px`);
            glow.style.setProperty('--glow-y', `${pointerEvent.clientY - dashboardBounds.top}px`);
            dashboard.classList.add('is-pointer-active');

            const heroBounds = hero.getBoundingClientRect();
            if (
                pointerEvent.clientX >= heroBounds.left &&
                pointerEvent.clientX <= heroBounds.right &&
                pointerEvent.clientY >= heroBounds.top &&
                pointerEvent.clientY <= heroBounds.bottom
            ) {
                hero.style.setProperty('--pointer-x', `${pointerEvent.clientX - heroBounds.left}px`);
                hero.style.setProperty('--pointer-y', `${pointerEvent.clientY - heroBounds.top}px`);
            } else {
                hero.style.removeProperty('--pointer-x');
                hero.style.removeProperty('--pointer-y');
            }

            frame = 0;
        });
    });

    dashboard.addEventListener('pointerleave', () => {
        if (frame) {
            window.cancelAnimationFrame(frame);
            frame = 0;
        }
        dashboard.classList.remove('is-pointer-active');
        hero.style.removeProperty('--pointer-x');
        hero.style.removeProperty('--pointer-y');
    });
})();
