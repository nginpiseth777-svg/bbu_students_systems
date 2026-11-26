(() => {
    const form = document.querySelector('[data-student-autocomplete]');
    if (!form) {
        return;
    }

    const input = form.querySelector('input[type="search"]');
    const suggestions = document.getElementById('student-search-suggestions');
    const endpoint = form.dataset.suggestionsUrl;
    if (!input || !suggestions || !endpoint) {
        return;
    }

    let debounceTimer;
    let requestController;
    let requestSequence = 0;
    let options = [];
    let activeIndex = -1;

    const closeSuggestions = () => {
        suggestions.hidden = true;
        suggestions.replaceChildren();
        input.setAttribute('aria-expanded', 'false');
        input.removeAttribute('aria-activedescendant');
        activeIndex = -1;
        options = [];
    };

    const showMessage = (message) => {
        suggestions.replaceChildren();
        const status = document.createElement('div');
        status.className = 'student-search-empty';
        status.setAttribute('role', 'status');
        status.textContent = message;
        suggestions.append(status);
        suggestions.hidden = false;
        input.setAttribute('aria-expanded', 'true');
    };

    const setActiveOption = (index) => {
        if (!options.length) {
            return;
        }

        activeIndex = (index + options.length) % options.length;
        options.forEach((option, optionIndex) => {
            const isActive = optionIndex === activeIndex;
            option.setAttribute('aria-selected', String(isActive));
            if (isActive) {
                input.setAttribute('aria-activedescendant', option.id);
                option.scrollIntoView({ block: 'nearest' });
            }
        });
    };

    const renderSuggestions = (results) => {
        suggestions.replaceChildren();
        options = [];
        activeIndex = -1;

        if (!results.length) {
            showMessage('រកមិនឃើញឈ្មោះដែលត្រូវគ្នា');
            return;
        }

        results.forEach((student, index) => {
            const option = document.createElement('a');
            option.id = `student-search-option-${index}`;
            option.className = 'student-search-option';
            option.href = student.url;
            option.textContent = student.name;
            option.setAttribute('role', 'option');
            option.setAttribute('aria-selected', 'false');
            option.tabIndex = -1;
            suggestions.append(option);
            options.push(option);
        });

        suggestions.hidden = false;
        input.setAttribute('aria-expanded', 'true');
    };

    const requestSuggestions = async (query) => {
        requestController?.abort();
        requestController = new AbortController();
        const sequence = ++requestSequence;
        const url = new URL(endpoint, window.location.origin);
        url.searchParams.set('q', query);

        try {
            const response = await fetch(url, {
                headers: { Accept: 'application/json' },
                signal: requestController.signal,
            });
            if (!response.ok) {
                throw new Error(`Suggestion request failed: ${response.status}`);
            }

            const data = await response.json();
            if (sequence !== requestSequence) {
                return;
            }
            renderSuggestions(data.results);
        } catch (error) {
            if (error.name === 'AbortError' || sequence !== requestSequence) {
                return;
            }
            showMessage('មិនអាចស្វែងរកបានទេ សូមសាកល្បងម្ដងទៀត');
        }
    };

    input.addEventListener('input', () => {
        window.clearTimeout(debounceTimer);
        const query = input.value.trim();
        requestSequence += 1;
        requestController?.abort();

        if (Array.from(query).length < 2) {
            closeSuggestions();
            return;
        }

        debounceTimer = window.setTimeout(
            () => requestSuggestions(query),
            180,
        );
    });

    input.addEventListener('keydown', (event) => {
        if (suggestions.hidden) {
            return;
        }

        if (event.key === 'ArrowDown' && options.length) {
            event.preventDefault();
            setActiveOption(activeIndex + 1);
        } else if (event.key === 'ArrowUp' && options.length) {
            event.preventDefault();
            setActiveOption(activeIndex - 1);
        } else if (event.key === 'Enter' && activeIndex >= 0) {
            event.preventDefault();
            options[activeIndex].click();
        } else if (event.key === 'Escape') {
            closeSuggestions();
        }
    });

    document.addEventListener('pointerdown', (event) => {
        if (
            !form.contains(event.target) &&
            !suggestions.contains(event.target)
        ) {
            closeSuggestions();
        }
    });
})();
