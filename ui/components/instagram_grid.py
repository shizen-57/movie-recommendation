"""
Instagram-Style Movie Grid Component
Clean square grid layout with hover overlays and bottom search bar
"""
import streamlit as st
import pandas as pd
from typing import Optional, List, Dict, Any

class InstagramMovieGrid:
    def __init__(self):
        """Initialize the Instagram-style movie grid component"""
        self.apply_grid_styles()
    
    def apply_grid_styles(self):
        """Apply Instagram-style grid CSS"""
        st.markdown("""
        <style>
        /* Instagram Grid Container */
        .instagram-grid-container {
            width: 100%;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: black;
        }
        
        /* Grid Layout */
        .instagram-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            padding: 0;
        }
        
        @media (max-width: 768px) {
            .instagram-grid {
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 15px;
            }
        }
        
        /* Movie Card */
        .instagram-movie-card {
            position: relative;
            background: #111;
            border-radius: 12px;
            overflow: hidden;
            aspect-ratio: 2/3;
            cursor: pointer;
            transition: all 0.3s ease;
            border: 1px solid #333;
        }
        
        .instagram-movie-card:hover {
            transform: translateY(-8px);
            border-color: #666;
            box-shadow: 0 20px 40px rgba(0,0,0,0.5);
        }
        
        /* Poster Image */
        .movie-poster {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: all 0.3s ease;
        }
        
        .instagram-movie-card:hover .movie-poster {
            filter: brightness(0.7);
        }
        
        /* Overlay */
        .movie-overlay {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(
                to bottom,
                transparent 0%,
                transparent 50%,
                rgba(0,0,0,0.8) 100%
            );
            opacity: 0;
            transition: all 0.3s ease;
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            padding: 20px;
        }
        
        .instagram-movie-card:hover .movie-overlay {
            opacity: 1;
        }
        
        /* Movie Info */
        .movie-title {
            color: white;
            font-family: 'Roboto', sans-serif;
            font-size: 1.1rem;
            font-weight: 500;
            margin: 0 0 8px 0;
            line-height: 1.3;
        }
        
        .movie-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .movie-year {
            color: #ccc;
            font-family: 'Roboto', sans-serif;
            font-size: 0.9rem;
            font-weight: 300;
        }
        
        .movie-rating {
            color: #ffd700;
            font-family: 'Roboto', sans-serif;
            font-size: 0.9rem;
            font-weight: 400;
        }
        
        .movie-genres {
            color: #999;
            font-family: 'Roboto', sans-serif;
            font-size: 0.8rem;
            font-weight: 300;
            margin-bottom: 8px;
        }
        
        .movie-overview {
            color: #bbb;
            font-family: 'Roboto', sans-serif;
            font-size: 0.8rem;
            font-weight: 300;
            line-height: 1.4;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        
        /* Action Buttons */
        .movie-actions {
            position: absolute;
            top: 15px;
            right: 15px;
            display: flex;
            gap: 8px;
            opacity: 0;
            transition: all 0.3s ease;
        }
        
        .instagram-movie-card:hover .movie-actions {
            opacity: 1;
        }
        
        .action-btn {
            width: 32px;
            height: 32px;
            background: rgba(0,0,0,0.8);
            border: none;
            border-radius: 50%;
            color: white;
            font-size: 14px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
        }
        
        .action-btn:hover {
            background: rgba(255,255,255,0.2);
            transform: scale(1.1);
        }
        </style>
        """, unsafe_allow_html=True)
    
    def render(self, movies, title=None):
        """
        Render movies in Instagram-style grid
        
        Args:
            movies: List of movie dictionaries or DataFrame containing movie data
            title: Optional section title
        """
        # Handle both list and DataFrame inputs
        if isinstance(movies, list):
            if not movies:
                st.markdown("""
                <div class="instagram-grid-container">
                    <div style="text-align: center; color: rgba(255,255,255,0.7); padding: 60px; font-family: 'Roboto', sans-serif;">
                        <h2>🎬 No movies found</h2>
                        <p>Try searching for something else</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                return
            movies_list = movies
        else:
            # DataFrame case
            if movies.empty:
                st.markdown("""
                <div class="instagram-grid-container">
                    <div style="text-align: center; color: rgba(255,255,255,0.7); padding: 60px; font-family: 'Roboto', sans-serif;">
                        <h2>🎬 No movies found</h2>
                        <p>Try searching for something else</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                return
            
            # Convert DataFrame to list
            movies_list = []
            for _, movie in movies.iterrows():
                movie_data = {
                    'title': movie.get('title', 'Unknown Title'),
                    'year': self._extract_year(movie.get('release_date', movie.get('year', ''))),
                    'rating': movie.get('vote_average', movie.get('imdb_rating', 0)),
                    'genres': movie.get('genres', 'Unknown'),
                    'overview': movie.get('overview', 'No description available'),
                    'poster_url': self._get_poster_url(movie.get('title', 'Unknown Title'))
                }
                movies_list.append(movie_data)
        
        # Title section
        if title:
            st.markdown(f"""
            <div style="text-align: center; margin-bottom: 30px;">
                <h2 style="color: white; font-family: 'Roboto', sans-serif; font-weight: 300;">{title}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        # Container start
        st.markdown('<div class="instagram-grid-container">', unsafe_allow_html=True)
        st.markdown('<div class="instagram-grid">', unsafe_allow_html=True)
        
        # Render each movie card
        for movie in movies_list:
            self._render_movie_card(movie)
        
        # Container end
        st.markdown('</div>', unsafe_allow_html=True)  # Close grid
        st.markdown('</div>', unsafe_allow_html=True)  # Close container
    
    def _render_movie_card(self, movie: Dict[str, Any]):
        """Render a single movie card"""
        title = movie.get('title', 'Unknown Title')
        year = movie.get('year', '')
        rating = movie.get('rating', 0)
        genres = movie.get('genres', '')
        overview = movie.get('overview', '')
        poster_url = movie.get('poster_url', '')
        
        # Clean title for HTML
        safe_title = title.replace('"', '&quot;').replace("'", "&#39;")
        safe_overview = overview.replace('"', '&quot;').replace("'", "&#39;")
        
        # Format genres
        if genres and genres != 'Unknown':
            genre_list = genres.split('|')[:2]  # Show max 2 genres
            genre_text = ' • '.join(genre_list)
        else:
            genre_text = 'Genre Unknown'
        
        # Format rating
        rating_display = f"★ {rating:.1f}" if rating > 0 else "★ N/A"
        
        # Truncate overview
        if len(overview) > 120:
            overview = overview[:120] + "..."
        
        movie_card_html = f"""
        <div class="instagram-movie-card">
            <img src="{poster_url}" alt="{safe_title}" class="movie-poster" 
                 onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
            <div class="movie-poster-placeholder" style="display: none;">
                🎬<br>{safe_title}
            </div>
            
            <div class="movie-overlay">
                <div class="movie-title">{safe_title}</div>
                <div class="movie-meta">
                    <span class="movie-year">{year}</span>
                    <span class="movie-rating">{rating_display}</span>
                </div>
                <div class="movie-genres">{genre_text}</div>
                <div class="movie-overview">{safe_overview}</div>
            </div>
            
            <div class="movie-actions">
                <button class="action-btn" title="Add to Favorites">❤️</button>
                <button class="action-btn" title="Add to Watchlist">📋</button>
            </div>
        </div>
        """
        
        st.markdown(movie_card_html, unsafe_allow_html=True)
    
    def _extract_year(self, date_str):
        """Extract year from date string"""
        if isinstance(date_str, str) and len(date_str) >= 4:
            return date_str[:4]
        return str(date_str) if date_str else ''
    
    def _get_poster_url(self, title):
        """Generate poster URL (placeholder for now)"""
        # Create a more movie-like placeholder
        return f"https://via.placeholder.com/400x600/1a1a1a/ffffff?text={title.replace(' ', '+')}"