// CinemaAI Pro - JavaScript Implementation

class CinemaAIApp {
    constructor() {
        this.currentPage = 1;
        this.moviesPerPage = 20;
        this.allMovies = [];
        this.filteredMovies = [];
        this.isLoading = false;
        
        this.init();
    }

    async init() {
        this.setupEventListeners();
        await this.loadMovies();
        this.hideLoading();
    }

    setupEventListeners() {
        // Search functionality
        const searchInput = document.getElementById('searchInput');
        const searchBtn = document.getElementById('searchBtn');
        
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.handleSearch();
            }
        });
        
        searchBtn.addEventListener('click', () => {
            this.handleSearch();
        });

        // Quick action buttons
        document.querySelectorAll('.quick-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const genre = e.currentTarget.dataset.genre;
                this.handleGenreFilter(genre);
            });
        });

        // Load more button
        const loadMoreBtn = document.getElementById('loadMoreBtn');
        loadMoreBtn.addEventListener('click', () => {
            this.loadMoreMovies();
        });

        // Modal functionality
        const modal = document.getElementById('movieModal');
        const closeModal = document.querySelector('.modal-close');
        
        closeModal.addEventListener('click', () => {
            modal.style.display = 'none';
        });
        
        window.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
    }

    async loadMovies() {
        this.showLoading();
        
        try {
            const response = await fetch(`/api/movies?page=${this.currentPage}&per_page=${this.moviesPerPage}`);
            const data = await response.json();
            
            if (response.ok) {
                this.allMovies = data.movies;
                this.filteredMovies = [...this.allMovies];
                this.renderMovies();
            } else {
                throw new Error(data.error || 'Failed to load movies');
            }
        } catch (error) {
            console.error('Error loading movies:', error);
            this.showError('Failed to load movies. Please try again.');
        }
    }

    generateSampleMovies() {
        // Sample movie data - replace with actual API data
        const sampleMovies = [
            {
                id: 1,
                title: "Inception",
                year: "2010",
                rating: 8.8,
                genres: ["Sci-Fi", "Thriller"],
                poster: "https://via.placeholder.com/280x420/1a1a1a/ffffff?text=Inception",
                overview: "A mind-bending thriller about dream manipulation and reality layers."
            },
            {
                id: 2,
                title: "The Matrix",
                year: "1999",
                rating: 8.7,
                genres: ["Action", "Sci-Fi"],
                poster: "https://via.placeholder.com/280x420/1a1a1a/ffffff?text=The+Matrix",
                overview: "A hacker discovers reality is a computer simulation."
            },
            {
                id: 3,
                title: "Spirited Away",
                year: "2001",
                rating: 9.2,
                genres: ["Animation", "Family"],
                poster: "https://via.placeholder.com/280x420/1a1a1a/ffffff?text=Spirited+Away",
                overview: "A girl enters a world ruled by gods and witches."
            },
            {
                id: 4,
                title: "Parasite",
                year: "2019",
                rating: 8.6,
                genres: ["Thriller", "Drama"],
                poster: "https://via.placeholder.com/280x420/1a1a1a/ffffff?text=Parasite",
                overview: "A poor family infiltrates a wealthy household."
            },
            {
                id: 5,
                title: "The Dark Knight",
                year: "2008",
                rating: 9.0,
                genres: ["Action", "Crime"],
                poster: "https://via.placeholder.com/280x420/1a1a1a/ffffff?text=The+Dark+Knight",
                overview: "Batman faces the Joker in this dark superhero epic."
            },
            {
                id: 6,
                title: "Pulp Fiction",
                year: "1994",
                rating: 8.9,
                genres: ["Crime", "Drama"],
                poster: "https://via.placeholder.com/280x420/1a1a1a/ffffff?text=Pulp+Fiction",
                overview: "The lives of two mob hitmen and others intertwine."
            },
            {
                id: 7,
                title: "Your Name",
                year: "2016",
                rating: 8.4,
                genres: ["Animation", "Romance"],
                poster: "https://via.placeholder.com/280x420/1a1a1a/ffffff?text=Your+Name",
                overview: "Two teenagers share a magical connection."
            },
            {
                id: 8,
                title: "Joker",
                year: "2019",
                rating: 8.4,
                genres: ["Drama", "Thriller"],
                poster: "https://via.placeholder.com/280x420/1a1a1a/ffffff?text=Joker",
                overview: "A failed comedian descends into madness."
            },
            {
                id: 9,
                title: "Blade Runner 2049",
                year: "2017",
                rating: 8.0,
                genres: ["Sci-Fi"],
                poster: "https://via.placeholder.com/280x420/1a1a1a/ffffff?text=Blade+Runner+2049",
                overview: "A blade runner discovers a secret that could plunge society into chaos."
            },
            {
                id: 10,
                title: "Interstellar",
                year: "2014",
                rating: 8.6,
                genres: ["Sci-Fi", "Drama"],
                poster: "https://via.placeholder.com/280x420/1a1a1a/ffffff?text=Interstellar",
                overview: "Explorers travel through a wormhole to ensure humanity's survival."
            },
            {
                id: 11,
                title: "La La Land",
                year: "2016",
                rating: 8.0,
                genres: ["Musical", "Romance"],
                poster: "https://via.placeholder.com/280x420/1a1a1a/ffffff?text=La+La+Land",
                overview: "A jazz musician and actress meet and fall in love in Los Angeles."
            },
            {
                id: 12,
                title: "Mad Max: Fury Road",
                year: "2015",
                rating: 8.1,
                genres: ["Action", "Adventure"],
                poster: "https://via.placeholder.com/280x420/1a1a1a/ffffff?text=Mad+Max+Fury+Road",
                overview: "In a post-apocalyptic wasteland, Max teams up with Furiosa."
            }
        ];

        // Generate more movies by duplicating and modifying
        const allMovies = [];
        for (let i = 0; i < 5; i++) {
            sampleMovies.forEach((movie, index) => {
                allMovies.push({
                    ...movie,
                    id: movie.id + (i * sampleMovies.length),
                    title: `${movie.title}${i > 0 ? ` (${i + 1})` : ''}`
                });
            });
        }

        return allMovies;
    }

    renderMovies() {
        const grid = document.getElementById('moviesGrid');
        const moviesToShow = this.filteredMovies.slice(0, this.currentPage * this.moviesPerPage);
        
        grid.innerHTML = '';
        
        moviesToShow.forEach((movie, index) => {
            const movieCard = this.createMovieCard(movie, index);
            grid.appendChild(movieCard);
        });

        // Update load more button visibility
        const loadMoreBtn = document.getElementById('loadMoreBtn');
        if (moviesToShow.length >= this.filteredMovies.length) {
            loadMoreBtn.style.display = 'none';
        } else {
            loadMoreBtn.style.display = 'block';
        }
    }

    createMovieCard(movie, index) {
        const card = document.createElement('div');
        card.className = 'movie-card';
        card.style.animationDelay = `${index * 0.1}s`;
        
        card.innerHTML = `
            <img src="${movie.poster}" alt="${movie.title}" class="movie-poster" loading="lazy">
            <div class="movie-overlay">
                <h3 class="movie-title">${movie.title}</h3>
                <div class="movie-meta">
                    <span class="movie-year">${movie.year}</span>
                    <div class="movie-rating">
                        <i class="fas fa-star"></i>
                        <span>${movie.rating}</span>
                    </div>
                </div>
                <div class="movie-genres">
                    ${movie.genres.slice(0, 2).join(' • ')}
                </div>
                <div class="movie-actions">
                    <button class="action-btn favorite-btn" data-movie-id="${movie.id}">
                        <i class="far fa-heart"></i> Like
                    </button>
                    <button class="action-btn watchlist-btn" data-movie-id="${movie.id}">
                        <i class="far fa-bookmark"></i> Save
                    </button>
                    <button class="action-btn info-btn" data-movie-id="${movie.id}">
                        <i class="fas fa-info-circle"></i> Info
                    </button>
                </div>
            </div>
        `;

        // Add event listeners
        card.addEventListener('click', (e) => {
            if (!e.target.closest('.action-btn')) {
                this.showMovieModal(movie);
            }
        });

        // Action button event listeners
        const favoriteBtn = card.querySelector('.favorite-btn');
        const watchlistBtn = card.querySelector('.watchlist-btn');
        const infoBtn = card.querySelector('.info-btn');

        favoriteBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleFavorite(movie.id, favoriteBtn);
        });

        watchlistBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleWatchlist(movie.id, watchlistBtn);
        });

        infoBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.showMovieModal(movie);
        });

        return card;
    }

    async handleSearch() {
        const query = document.getElementById('searchInput').value.trim();
        
        if (query === '') {
            await this.loadMovies();
            return;
        }

        this.showLoading();
        
        try {
            const response = await fetch(`/api/search?query=${encodeURIComponent(query)}&ai=true`);
            const data = await response.json();
            
            if (response.ok) {
                this.filteredMovies = data.movies;
                this.currentPage = 1;
                this.renderMovies();
                
                // Show AI insights if available
                if (data.ai_response) {
                    this.showAIInsights(data.ai_response);
                }
            } else {
                throw new Error(data.error || 'Search failed');
            }
        } catch (error) {
            console.error('Error searching movies:', error);
            this.showError('Search failed. Please try again.');
        }
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    async handleGenreFilter(genre) {
        this.showLoading();
        
        try {
            const response = await fetch(`/api/movies?genre=${encodeURIComponent(genre)}&per_page=20`);
            const data = await response.json();
            
            if (response.ok) {
                this.filteredMovies = data.movies;
                this.currentPage = 1;
                this.renderMovies();
                
                // Update search input
                document.getElementById('searchInput').value = genre;
            } else {
                throw new Error(data.error || 'Filter failed');
            }
        } catch (error) {
            console.error('Error filtering movies:', error);
            this.showError('Filter failed. Please try again.');
        }
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    loadMoreMovies() {
        if (!this.isLoading) {
            this.currentPage++;
            this.renderMovies();
        }
    }

    toggleFavorite(movieId, button) {
        const icon = button.querySelector('i');
        const text = button.querySelector('span') || button.lastChild;
        
        if (icon.classList.contains('far')) {
            icon.classList.remove('far');
            icon.classList.add('fas');
            button.innerHTML = '<i class="fas fa-heart"></i> Liked';
            button.style.background = '#dc3545';
        } else {
            icon.classList.remove('fas');
            icon.classList.add('far');
            button.innerHTML = '<i class="far fa-heart"></i> Like';
            button.style.background = '#333333';
        }
    }

    toggleWatchlist(movieId, button) {
        const icon = button.querySelector('i');
        
        if (icon.classList.contains('far')) {
            icon.classList.remove('far');
            icon.classList.add('fas');
            button.innerHTML = '<i class="fas fa-bookmark"></i> Saved';
            button.style.background = '#28a745';
        } else {
            icon.classList.remove('fas');
            icon.classList.add('far');
            button.innerHTML = '<i class="far fa-bookmark"></i> Save';
            button.style.background = '#333333';
        }
    }

    showMovieModal(movie) {
        const modal = document.getElementById('movieModal');
        const modalBody = document.getElementById('modalBody');
        
        modalBody.innerHTML = `
            <div style="display: flex; gap: 30px; flex-wrap: wrap;">
                <div style="flex: 0 0 300px;">
                    <img src="${movie.poster}" alt="${movie.title}" style="width: 100%; border-radius: 10px;">
                </div>
                <div style="flex: 1; min-width: 300px;">
                    <h2 style="margin-bottom: 10px; font-size: 2rem;">${movie.title}</h2>
                    <div style="display: flex; gap: 20px; margin-bottom: 15px; color: #888;">
                        <span>${movie.year}</span>
                        <div style="display: flex; align-items: center; gap: 5px;">
                            <i class="fas fa-star" style="color: #ffd700;"></i>
                            <span>${movie.rating}/10</span>
                        </div>
                    </div>
                    <div style="margin-bottom: 20px;">
                        ${movie.genres.map(genre => `<span style="background: #333; padding: 4px 12px; border-radius: 15px; font-size: 0.9rem; margin-right: 8px;">${genre}</span>`).join('')}
                    </div>
                    <p style="line-height: 1.6; margin-bottom: 25px; font-size: 1.1rem;">${movie.overview}</p>
                    <div style="display: flex; gap: 15px;">
                        <button class="action-btn" style="padding: 10px 20px; font-size: 1rem;">
                            <i class="fas fa-play"></i> Watch Trailer
                        </button>
                        <button class="action-btn" style="padding: 10px 20px; font-size: 1rem;">
                            <i class="fas fa-heart"></i> Add to Favorites
                        </button>
                        <button class="action-btn" style="padding: 10px 20px; font-size: 1rem;">
                            <i class="fas fa-bookmark"></i> Add to Watchlist
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        modal.style.display = 'block';
    }

    showAIInsights(aiResponse) {
        // Create and show AI insights banner
        const insightsDiv = document.createElement('div');
        insightsDiv.className = 'ai-insights-banner';
        insightsDiv.innerHTML = `
            <div class="ai-insights-content">
                <h3><i class="fas fa-brain"></i> AI Insights</h3>
                <p>${aiResponse}</p>
                <button class="close-insights" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        // Insert before movies grid
        const grid = document.getElementById('moviesGrid');
        grid.parentNode.insertBefore(insightsDiv, grid);
        
        // Add CSS for insights banner
        if (!document.getElementById('insights-styles')) {
            const style = document.createElement('style');
            style.id = 'insights-styles';
            style.textContent = `
                .ai-insights-banner {
                    background: linear-gradient(135deg, #1a1a1a, #2a2a2a);
                    border: 1px solid #333;
                    border-radius: 12px;
                    margin: 20px 0;
                    overflow: hidden;
                }
                
                .ai-insights-content {
                    padding: 20px;
                    position: relative;
                }
                
                .ai-insights-content h3 {
                    color: white;
                    margin-bottom: 15px;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }
                
                .ai-insights-content p {
                    color: #ccc;
                    line-height: 1.6;
                    margin: 0;
                }
                
                .close-insights {
                    position: absolute;
                    top: 15px;
                    right: 15px;
                    background: none;
                    border: none;
                    color: #888;
                    cursor: pointer;
                    font-size: 1.2rem;
                    transition: color 0.3s ease;
                }
                
                .close-insights:hover {
                    color: white;
                }
            `;
            document.head.appendChild(style);
        }
    }

    showLoading() {
        document.getElementById('loading').style.display = 'block';
        document.getElementById('moviesGrid').style.display = 'none';
    }

    hideLoading() {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('moviesGrid').style.display = 'grid';
    }

    showError(message) {
        const grid = document.getElementById('moviesGrid');
        grid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 60px 20px; color: #888;">
                <i class="fas fa-exclamation-triangle" style="font-size: 3rem; margin-bottom: 20px;"></i>
                <h3 style="margin-bottom: 10px;">Oops! Something went wrong</h3>
                <p>${message}</p>
                <button onclick="location.reload()" style="margin-top: 20px; padding: 10px 20px; background: #333; border: 1px solid #555; color: white; border-radius: 5px; cursor: pointer;">
                    Try Again
                </button>
            </div>
        `;
        this.hideLoading();
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new CinemaAIApp();
});

// Add some utility functions
function formatNumber(num) {
    return new Intl.NumberFormat().format(num);
}

function truncateText(text, maxLength) {
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
}
