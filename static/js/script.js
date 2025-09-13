document.addEventListener('DOMContentLoaded', () => {
    // Display error/warning messages in a styled div
    const showMessage = (message, element, type = 'error') => {
        const messageDiv = document.createElement('div');
        messageDiv.className = `error-message bg-${type === 'error' ? 'red' : 'yellow'}-600 text-white p-3 rounded-md mb-4 text-sm`;
        messageDiv.textContent = message;
        element.closest('form')?.prepend(messageDiv) || document.body.prepend(messageDiv);
        setTimeout(() => messageDiv.remove(), 7000);
        console[type === 'error' ? 'error' : 'warn'](`Validation ${type}: ${message}`);
    };

    // Validation for new user form (user.html)
    const newUserForm = document.querySelector('form[action*="/user"]');
    if (newUserForm) {
        newUserForm.addEventListener('submit', async (e) => {
            newUserForm.querySelectorAll('.error-message').forEach(el => el.remove());

            const userId = document.getElementById('user_id');
            if (userId && !userId.value.trim()) {
                e.preventDefault();
                showMessage('Please enter a valid User ID.', userId);
                return;
            }

            const genres = document.getElementById('genres');
            const actors = document.getElementById('actors');
            const directors = document.getElementById('directors');
            const selections = [
                genres ? genres.selectedOptions.length : 0,
                actors ? actors.selectedOptions.length : 0,
                directors ? directors.selectedOptions.length : 0
            ].reduce((sum, count) => sum + count, 0);

            if (selections === 0) {
                e.preventDefault();
                showMessage('Please select at least one genre, actor, or director for better recommendations.', genres || actors || directors);
                return;
            }

            console.log('New user form submission:', {
                userId: userId.value,
                genres: genres ? Array.from(genres.selectedOptions).map(opt => opt.value) : [],
                actors: actors ? Array.from(actors.selectedOptions).map(opt => opt.value) : [],
                directors: directors ? Array.from(directors.selectedOptions).map(opt => opt.value) : []
            });
        });
    }

    // Validation for existing user form (index.html)
    const existingUserForm = document.querySelector('form[action*="/search_user"]');
    if (existingUserForm) {
        existingUserForm.addEventListener('submit', async (e) => {
            existingUserForm.querySelectorAll('.error-message').forEach(el => el.remove());

            const userId = existingUserForm.querySelector('input[name="user_id"]');
            if (userId && !userId.value.trim()) {
                e.preventDefault();
                showMessage('Please enter a valid User ID.', userId);
                return;
            }

            console.log('Existing user form submission:', { userId: userId.value });
        });
    }

    // Monitor strategy selection (recommendations.html)
    const strategySelect = document.querySelector('select[name="strategy"]');
    if (strategySelect) {
        strategySelect.addEventListener('change', () => {
            const strategy = strategySelect.value;
            console.log(`Strategy selected: ${strategy}`);
            showMessage(`Selected strategy: ${strategy.replace('_', ' ').toUpperCase()}.`, strategySelect, 'warning');
        });
    }

    // Log selections for debugging
    const selects = document.querySelectorAll('select[multiple]');
    selects.forEach(select => {
        select.addEventListener('change', () => {
            const selectedOptions = Array.from(select.selectedOptions).map(option => option.value);
            console.log(`Selected ${select.id}:`, selectedOptions);
        });
    });

    // Check server connectivity and recommendations
    const checkServer = async () => {
        try {
            const response = await fetch('/ping', { method: 'GET', cache: 'no-store' });
            if (response.ok) {
                console.log('Server is reachable');
            } else {
                console.error('Server ping failed:', response.status);
                showMessage(`Warning: Server returned status ${response.status}. Check server logs.`, document.body, 'warning');
            }

            // Check recommendations for current user (if on recommendations page)
            const userIdMatch = window.location.pathname.match(/\/recommendations\/(\d+)/);
            if (userIdMatch) {
                const userId = userIdMatch[1];
                const strategy = new URLSearchParams(window.location.search).get('strategy') || 'hybrid';
                const recResponse = await fetch(`/recommendations/${userId}?strategy=${strategy}`, { method: 'GET' });
                const data = await recResponse.json().catch(() => ({}));
                console.log(`Recommendations for user ${userId} (strategy: ${strategy}):`, data);
                if (!data.recommendations?.length) {
                    showMessage(`No recommendations found for User ${userId} with ${strategy} strategy. Try a different strategy or check server logs.`, document.body, 'warning');
                }
            }
        } catch (error) {
            console.error('Server connectivity error:', error.message);
            showMessage('Error: Cannot connect to server. Ensure Flask is running on http://192.168.1.11:5000 or try http://localhost:5000.', document.body);
        }
    };

    // Run server check on page load
    checkServer();
});