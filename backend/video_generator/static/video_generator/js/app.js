// LYRA Application JavaScript

document.addEventListener('DOMContentLoaded', function () {
    console.log('LYRA app loaded');
    
    // Initialize theme
    initializeTheme();

    // Initialize search suggestions
    initializeSearchSuggestions();
});

// Search Suggestions
function initializeSearchSuggestions() {
    const input = document.getElementById('song-input');
    const suggestionsBox = document.getElementById('search-suggestions');
    
    if (!input || !suggestionsBox) return;
    
    let debounceTimer;
    
    input.addEventListener('input', function() {
        const query = this.value.trim();
        
        clearTimeout(debounceTimer);
        
        if (query.length < 2) {
            suggestionsBox.style.display = 'none';
            return;
        }
        
        debounceTimer = setTimeout(() => {
            fetchSuggestions(query, suggestionsBox, input);
        }, 300);
    });
    
    // Hide suggestions when clicking outside
    document.addEventListener('click', function(e) {
        if (e.target !== input && e.target !== suggestionsBox && !suggestionsBox.contains(e.target)) {
            suggestionsBox.style.display = 'none';
        }
    });
}

function fetchSuggestions(query, suggestionsBox, input) {
    fetch(`/search-suggestions/?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            if (data.length > 0) {
                renderSuggestions(data, suggestionsBox, input);
            } else {
                suggestionsBox.style.display = 'none';
            }
        })
        .catch(error => {
            console.error('Error fetching suggestions:', error);
            suggestionsBox.style.display = 'none';
        });
}

function renderSuggestions(suggestions, suggestionsBox, input) {
    suggestionsBox.innerHTML = '';
    
    suggestions.forEach(song => {
        const div = document.createElement('div');
        div.className = 'suggestion-item';
        
        // Format duration (seconds to mm:ss)
        const minutes = Math.floor(song.duration / 60);
        const seconds = Math.floor(song.duration % 60);
        const duration = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        
        const syncedBadge = song.synced ? '<span class="synced-badge">Synced</span>' : '';
        
        div.innerHTML = `
            <div class="suggestion-info">
                <div class="suggestion-title">${song.title}</div>
                <div class="suggestion-artist">${song.artist} • ${song.album}</div>
            </div>
            <div class="suggestion-meta">
                ${syncedBadge}
                <span class="suggestion-duration">${duration}</span>
            </div>
        `;
        
        div.addEventListener('click', function() {
            input.value = `${song.title} ${song.artist}`;
            suggestionsBox.style.display = 'none';
        });
        
        suggestionsBox.appendChild(div);
    });
    
    suggestionsBox.style.display = 'block';
}

// Theme Management
function initializeTheme() {
    const themeToggle = document.getElementById('theme-toggle');
    if (!themeToggle) return;
    
    const themeIcon = themeToggle.querySelector('.theme-icon');
    
    // Check for saved theme preference or default to light mode
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
    
    // Theme toggle click handler
    themeToggle.addEventListener('click', function () {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
        
        // Add rotation animation
        themeIcon.style.transform = 'rotate(360deg)';
        setTimeout(() => {
            themeIcon.style.transform = 'rotate(0deg)';
        }, 300);
    });
}

function setTheme(theme) {
    const themeIcon = document.querySelector('.theme-icon');
    if (!themeIcon) return;
    
    // Set theme attribute
    document.documentElement.setAttribute('data-theme', theme);
    
    // Save preference
    localStorage.setItem('theme', theme);
    
    // Update icon
    if (theme === 'dark') {
        themeIcon.textContent = '☀️';
    } else {
        themeIcon.textContent = '🌙';
    }
}
