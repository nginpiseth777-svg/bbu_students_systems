document.addEventListener('DOMContentLoaded', () => {
    const input = document.querySelector('input[name="profile_picture"]');
    const previews = document.querySelectorAll('[data-profile-photo-preview]');

    if (!input || previews.length === 0) {
        return;
    }

    let previewUrl;
    input.addEventListener('change', () => {
        const file = input.files && input.files[0];
        if (!file || !file.type.startsWith('image/')) {
            return;
        }

        if (previewUrl) {
            URL.revokeObjectURL(previewUrl);
        }
        previewUrl = URL.createObjectURL(file);

        previews.forEach((preview) => {
            const image = document.createElement('img');
            image.src = previewUrl;
            image.alt = 'រូបថតប្រវត្តិរូប';
            preview.replaceChildren(image);
        });
    });

    window.addEventListener('pagehide', () => {
        if (previewUrl) {
            URL.revokeObjectURL(previewUrl);
        }
    }, { once: true });
});
