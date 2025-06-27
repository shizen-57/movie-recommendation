"""
🎬 CinemaAI Pro - Advanced Movie Recommendation System
Python-based UI with Streamlit + Gemini AI Integration
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import List, Dict, Any
import requests
from PIL import Image
import io
import os
import sys
import asyncio
from datetime import datetime
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import your existing modules
try:
    from src.data_loader import MovieDataLoader
    from src.ai.gemini import GeminiMovieAI
except ImportError as e:
    st.error(f"Could not import required modules: {e}")
    st.error("Please ensure all dependencies are installed and modules are available.")

# Page configuration
st.set_page_config(
    page_title="🎬 CinemaAI Pro",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo',
        'Report a bug': 'https://github.com/your-repo/issues',
        'About': '# CinemaAI Pro Movie Recommender\nPowered by Machine Learning and Gemini AI'
    }
)

class CinemaAIProApp:
    def __init__(self):
        """Initialize the CinemaAI Pro application"""
        self.setup_session_state()
        self.movies_df, self.gemini_ai = self.load_models_and_data()
        
    def setup_session_state(self):
        """Initialize session state variables"""
        if 'favorites' not in st.session_state:
            st.session_state.favorites = []
        if 'watchlist' not in st.session_state:
            st.session_state.watchlist = []
        if 'search_query' not in st.session_state:
            st.session_state.search_query = ""
        if 'selected_genre' not in st.session_state:
            st.session_state.selected_genre = "All"
        if 'ai_recommendations' not in st.session_state:
            st.session_state.ai_recommendations = []
        if 'ai_recommendations_text' not in st.session_state:
            st.session_state.ai_recommendations_text = ""
        if 'current_page' not in st.session_state:
            st.session_state.current_page = "discover"
        if 'user_preferences' not in st.session_state:
            st.session_state.user_preferences = {
                'preferred_genres': [],
                'min_rating': 0,
                'preferred_years': (1980, 2024)
            }
    
    @st.cache_resource
    def load_models_and_data(_self):
        """Load movie data and AI models with caching"""
        try:
            # Initialize data loader
            data_loader = MovieDataLoader()
            
            # Try to load TMDB data first
            try:
                # Check if TMDB CSV files exist
                tmdb_movies_path = "data/tmdb_5000_movies.csv"
                if os.path.exists(tmdb_movies_path):
                    print(f"📊 Loading TMDB movie data from {tmdb_movies_path}")
                    movies_df = pd.read_csv(tmdb_movies_path)
                    print(f"✅ Loaded {len(movies_df)} movies from TMDB dataset")
                else:
                    # Try to load from data loader CSV files
                    data_loader.load_from_csv()
                    data = data_loader.get_data()
                    movies_df = data["movies"]
                    print(f"✅ Loaded {len(movies_df)} movies from data loader")
            except Exception as e:
                print(f"⚠️ Could not load CSV data: {e}")
                # If CSV loading fails, create sample data
                data = data_loader.create_enhanced_sample_data()
                movies_df = data["movies"]
                print(f"✅ Created {len(movies_df)} sample movies")
            
            # Initialize Gemini AI
            gemini_api_key = os.getenv("GEMINI_API_KEY", "AIzaSyDJ3TY3gZP2g8yiV40sc-3a1gevGuHUXIU")
            if gemini_api_key:
                gemini_ai = GeminiMovieAI(gemini_api_key)
                print("🤖 Gemini AI recommender initialized")
            else:
                gemini_ai = None
                print("ℹ️ Gemini API key not found. AI features disabled.")
            
            return movies_df, gemini_ai
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return _self.get_fallback_data(), None
    
    def get_fallback_data(self):
        """Fallback sample movie data with richer metadata"""
        sample_data = {
            'title': [
                'Inception', 'The Matrix', 'Spirited Away', 'Parasite', 
                'The Dark Knight', 'Pulp Fiction', 'Your Name', 'Joker',
                'Blade Runner 2049', 'Interstellar', 'La La Land', 'Mad Max: Fury Road',
                'The Shawshank Redemption', 'The Godfather', 'Goodfellas', 'Fight Club'
            ],
            'genres': [
                'Sci-Fi|Thriller', 'Action|Sci-Fi', 'Animation|Family', 'Thriller|Drama',
                'Action|Crime', 'Crime|Drama', 'Animation|Romance', 'Drama|Thriller',
                'Sci-Fi', 'Sci-Fi|Drama', 'Musical|Romance', 'Action|Adventure',
                'Drama', 'Crime|Drama', 'Crime|Drama', 'Drama|Thriller'
            ],
            'vote_average': [8.8, 8.7, 9.2, 8.6, 9.0, 8.9, 8.4, 8.4, 8.0, 8.6, 8.0, 8.1, 9.3, 9.2, 8.7, 8.8],
            'release_date': [
                '2010-07-16', '1999-03-31', '2001-07-20', '2019-05-30',
                '2008-07-18', '1994-10-14', '2016-08-26', '2019-10-04',
                '2017-10-06', '2014-11-07', '2016-12-09', '2015-05-15',
                '1994-09-23', '1972-03-24', '1990-09-21', '1999-10-15'
            ],
            'overview': [
                'A mind-bending thriller about dream manipulation and reality layers.',
                'A hacker discovers reality is a computer simulation.',
                'A girl enters a world ruled by gods and witches.',
                'A poor family infiltrates a wealthy household.',
                'Batman faces the Joker in this dark and gritty superhero epic.',
                'The lives of two mob hitmen, a boxer, and a pair of diner bandits intertwine.',
                'Two teenagers share a profound, magical connection upon discovering they are swapping bodies.',
                'A failed comedian begins a slow descent into madness as he transforms into the criminal mastermind known as the Joker.',
                'A young blade runner discovers a secret that could plunge society into chaos.',
                'A team of explorers travel through a wormhole in space to ensure humanity\'s survival.',
                'A jazz musician and an aspiring actress meet and fall in love in Los Angeles.',
                'In a post-apocalyptic wasteland, Max teams up with Furiosa to survive.',
                'Two imprisoned men bond over a number of years, finding solace and eventual redemption.',
                'The aging patriarch of an organized crime dynasty transfers control to his reluctant son.',
                'The story of Henry Hill and his life in the mob, covering his relationship with his wife.',
                'An insomniac office worker and a devil-may-care soapmaker form an underground fight club.'
            ]
        }
        return pd.DataFrame(sample_data)
    
    def apply_dark_theme(self):
        """Apply pure black theme with Pinterest-style masonry layout"""
        st.markdown("""
        <style>
        /* Import beautiful font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        /* Global black theme */
        .stApp {
            background: #000000 !important;
            color: #ffffff !important;
            font-family: 'Inter', sans-serif;
        }
        
        /* Make all backgrounds black */
        .main .block-container {
            background: #000000 !important;
            padding-top: 2rem;
        }
        
        /* Sidebar black */
        .css-1d391kg, .css-1lcbmhc {
            background: #000000 !important;
        }
        
        /* Main header styling - black with white text */
        .main-header {
            background: #000000 !important;
            padding: 3rem 2rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: 0 20px 40px rgba(255, 255, 255, 0.1);
            border: 1px solid #333333;
        }
        
        .main-header h1 {
            color: #ffffff !important;
            font-size: 3.5rem;
            font-weight: 800;
            margin: 0;
            text-shadow: 2px 2px 8px rgba(255, 255, 255, 0.2);
            letter-spacing: -1px;
        }
        
        .main-header p {
            color: #ffffff !important;
            font-size: 1.3rem;
            margin: 1rem 0 0 0;
            font-weight: 400;
            opacity: 0.8;
        }
        
        /* Pinterest/Instagram Style Masonry Grid Layout */
        .poster-card {
            position: relative;
            border-radius: 0;
            overflow: hidden;
            transition: all 0.2s ease;
            cursor: pointer;
            box-shadow: none;
            margin: 0;
            background: none;
            border: none;
        }
        
        .poster-card:hover {
            transform: scale(1.02);
            z-index: 10;
        }
        
        .poster-card:hover .poster-overlay {
            opacity: 1;
        }
        
        .poster-card:hover .poster-image {
            filter: brightness(0.8);
        }
        
        .poster-image {
            width: 100%;
            height: auto;
            display: block;
            transition: filter 0.2s ease;
            object-fit: cover;
        }
        
        .poster-overlay {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(to bottom, rgba(0,0,0,0.4) 0%, rgba(0,0,0,0) 30%, rgba(0,0,0,0) 70%, rgba(0,0,0,0.6) 100%);
            opacity: 0;
            transition: opacity 0.2s ease;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            padding: 12px;
        }
        
        .poster-top-overlay {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }
        
        .poster-username {
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            text-shadow: none;
            backdrop-filter: blur(10px);
        }
        
        .poster-actions {
            display: flex;
            gap: 6px;
            align-items: center;
        }
        
        .poster-action-btn {
            background: rgba(0, 0, 0, 0.8);
            border: none;
            border-radius: 50%;
            width: 28px;
            height: 28px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
            backdrop-filter: blur(10px);
        }
        
        .poster-action-btn:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: scale(1.1);
        }
        
        .poster-bottom-overlay {
            display: flex;
            flex-direction: column;
            gap: 4px;
        }
        
        .poster-title {
            color: white;
            font-size: 13px;
            font-weight: 700;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
            line-height: 1.2;
            margin: 0;
        }
        
        .poster-meta {
            display: flex;
            gap: 6px;
            align-items: center;
        }
        
        .poster-rating {
            background: rgba(255, 193, 7, 0.95);
            color: black;
            padding: 2px 6px;
            border-radius: 8px;
            font-size: 10px;
            font-weight: 600;
        }
        
        .poster-year {
            color: white;
            font-size: 10px;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
        }
        
        /* Masonry Grid Layout - Pinterest Style */
        .poster-grid {
            columns: 5;
            column-gap: 4px;
            padding: 0;
            margin: 0;
        }
        
        .poster-grid .poster-card {
            break-inside: avoid;
            margin-bottom: 4px;
            display: inline-block;
            width: 100%;
        }
        
        /* Responsive columns */
        @media (max-width: 1200px) {
            .poster-grid {
                columns: 4;
            }
        }
        
        @media (max-width: 900px) {
            .poster-grid {
                columns: 3;
            }
        }
        
        @media (max-width: 600px) {
            .poster-grid {
                columns: 2;
                column-gap: 2px;
            }
            
            .poster-grid .poster-card {
                margin-bottom: 2px;
            }
        }
        
        /* Black buttons */
        .stButton > button {
            background: #000000 !important;
            color: #ffffff !important;
            border: 1px solid #333333 !important;
            border-radius: 15px;
            padding: 0.8rem 1.5rem;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            box-shadow: 0 4px 15px rgba(255, 255, 255, 0.1);
        }
        
        .stButton > button:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(255, 255, 255, 0.2);
            background: #333333 !important;
        }
        
        /* Search input styling */
        .stTextInput > div > div > input {
            background: #111111 !important;
            color: #ffffff !important;
            border: 1px solid #333333 !important;
            border-radius: 10px;
        }
        
        /* Select box styling */
        .stSelectbox > div > div {
            background: #111111 !important;
            color: #ffffff !important;
            border: 1px solid #333333 !important;
        }
        
        /* AI analysis styling */
        .ai-analysis {
            background: #111111 !important;
            border: 1px solid #333333 !important;
            border-radius: 15px;
            padding: 1.5rem;
            margin: 1rem 0;
            color: #ffffff !important;
        }
        
        /* Movie detail card styling */
        .movie-detail-card {
            background: #111111 !important;
            border: 1px solid #333333 !important;
            border-radius: 15px;
            padding: 1.5rem;
            margin: 1rem 0;
            color: #ffffff !important;
        }
        
        .movie-title {
            color: #ffffff !important;
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 0.8rem;
        }
        
        .movie-rating {
            background: #ffffff !important;
            color: #000000 !important;
            padding: 0.4rem 1rem;
            border-radius: 25px;
            font-weight: 700;
            display: inline-block;
            margin-right: 1rem;
            font-size: 0.9rem;
        }
        
        .movie-genre {
            background: #333333 !important;
            color: #ffffff !important;
            padding: 0.3rem 0.8rem;
            border-radius: 15px;
            font-size: 0.8rem;
            display: inline-block;
            margin-right: 0.5rem;
            margin-bottom: 0.5rem;
            border: 1px solid #666666;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """, unsafe_allow_html=True)
    
    def render_poster_card(self, movie, height_variation=None):
        """Render a Pinterest-style poster card"""
        title = movie.get('title', 'Unknown Title')
        rating = movie.get('vote_average', movie.get('imdb_rating', 0))
        year = movie.get('release_date', movie.get('year', ''))
        if isinstance(year, str) and len(year) >= 4:
            year = year[:4]
        
        # Generate random height for masonry effect
        if height_variation is None:
            height_variation = np.random.choice([240, 280, 320, 360, 400])
        
        # Use placeholder for poster since we don't have actual poster URLs
        poster_url = "https://via.placeholder.com/300x400/333/fff?text=" + title.replace(' ', '+')
        
        card_html = f"""
        <div class="poster-card" style="height: {height_variation}px;">
            <img class="poster-image" src="{poster_url}" alt="{title}" style="height: {height_variation}px; object-fit: cover;">
            <div class="poster-overlay">
                <div class="poster-top-overlay">
                    <div class="poster-username">CinemaAI</div>
                    <div class="poster-actions">
                        <div class="poster-action-btn">♡</div>
                        <div class="poster-action-btn">⋯</div>
                    </div>
                </div>
                <div class="poster-bottom-overlay">
                    <div class="poster-title">{title}</div>
                    <div class="poster-meta">
                        <div class="poster-rating">★ {rating:.1f}</div>
                        <div class="poster-year">{year}</div>
                    </div>
                </div>
            </div>
        </div>
        """
        return card_html
    
    def render_masonry_grid(self, movies, num_columns=5):
        """Render movies in a Pinterest-style masonry grid"""
        if movies.empty:
            st.warning("No movies to display")
            return
        
        # Create the masonry grid HTML
        grid_html = '<div class="poster-grid">'
        
        for _, movie in movies.iterrows():
            card_html = self.render_poster_card(movie)
            grid_html += card_html
        
        grid_html += '</div>'
        
        st.markdown(grid_html, unsafe_allow_html=True)
    
    def run(self):
        """Main application loop"""
        self.apply_dark_theme()
        
        # Header
        st.markdown("""
        <div class="main-header">
            <h1>🎬 CinemaAI Pro</h1>
            <p>Discover your next favorite movie with AI-powered recommendations</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sidebar
        with st.sidebar:
            st.title("🎯 Discover")
            
            # Search
            search_query = st.text_input("🔍 Search movies or describe what you want:", 
                                       placeholder="e.g., 'sci-fi thriller with time travel'")
            
            # Genre filter
            genres = ["All", "Action", "Comedy", "Drama", "Horror", "Romance", "Sci-Fi", "Thriller"]
            selected_genre = st.selectbox("🎭 Genre", genres)
            
            # Year range
            year_range = st.slider("📅 Release Year", 1980, 2024, (2000, 2024))
            
            # Rating filter
            min_rating = st.slider("⭐ Minimum Rating", 0.0, 10.0, 7.0, 0.1)
        
        # Main content area
        if search_query:
            st.subheader(f"🔍 Results for: '{search_query}'")
            
            if self.gemini_ai:
                # Use Gemini AI for search
                with st.spinner("🤖 AI is analyzing your request..."):
                    try:
                        result = self.gemini_ai.search_movies_by_description(search_query, top_k=12)
                        
                        if 'error' not in result:
                            st.markdown(f"**🤖 AI Analysis:** {result.get('total_movies_analyzed', 0)} movies analyzed")
                            
                            # Display AI response
                            with st.expander("🧠 AI Insights", expanded=True):
                                st.markdown(f"<div class='ai-analysis'>{result.get('ai_response', '')}</div>", 
                                          unsafe_allow_html=True)
                            
                            # Show movies in masonry grid
                            if self.movies_df is not None and len(self.movies_df) > 0:
                                sample_movies = self.movies_df.head(12)
                                self.render_masonry_grid(sample_movies)
                        else:
                            st.error(f"AI Search Error: {result['error']}")
                            # Fallback to regular search
                            filtered_movies = self.movies_df[
                                self.movies_df['title'].str.contains(search_query, case=False, na=False)
                            ].head(12)
                            self.render_masonry_grid(filtered_movies)
                    except Exception as e:
                        st.error(f"Search error: {e}")
                        filtered_movies = self.movies_df[
                            self.movies_df['title'].str.contains(search_query, case=False, na=False)
                        ].head(12)
                        self.render_masonry_grid(filtered_movies)
            else:
                # Regular search without AI
                filtered_movies = self.movies_df[
                    self.movies_df['title'].str.contains(search_query, case=False, na=False)
                ].head(12)
                self.render_masonry_grid(filtered_movies)
        
        else:
            # Default view - show trending/popular movies
            st.subheader("🔥 Trending Now")
            
            # Filter movies based on sidebar selections
            filtered_movies = self.movies_df.copy()
            
            if selected_genre != "All":
                filtered_movies = filtered_movies[
                    filtered_movies['genres'].str.contains(selected_genre, case=False, na=False)
                ]
            
            # Apply rating filter
            rating_col = 'vote_average' if 'vote_average' in filtered_movies.columns else 'imdb_rating'
            if rating_col in filtered_movies.columns:
                filtered_movies = filtered_movies[filtered_movies[rating_col] >= min_rating]
            
            # Show movies in masonry grid
            display_movies = filtered_movies.head(20)
            self.render_masonry_grid(display_movies)
            
            # Additional sections
            st.subheader("🎯 AI Powered Recommendations")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🤖 Get AI Recommendations", key="ai_recs"):
                    if self.gemini_ai:
                        with st.spinner("🧠 AI is curating recommendations..."):
                            try:
                                # Get AI recommendations based on popular movies
                                result = self.gemini_ai.get_enhanced_recommendations("Avatar", 5)
                                
                                if 'error' not in result:
                                    st.markdown("### 🎬 AI Recommended Movies")
                                    
                                    for movie in result.get('recommendations', []):
                                        with st.container():
                                            st.markdown(f"**{movie['title']}** (Similarity: {movie['similarity_score']})")
                                            st.write(f"Tags: {movie['tags'][:100]}...")
                                    
                                    with st.expander("🧠 AI Analysis", expanded=True):
                                        st.markdown(f"<div class='ai-analysis'>{result.get('ai_analysis', '')}</div>", 
                                                  unsafe_allow_html=True)
                                else:
                                    st.error(f"AI Error: {result['error']}")
                            except Exception as e:
                                st.error(f"AI recommendation error: {e}")
                    else:
                        st.warning("AI features require a Gemini API key. Please set GEMINI_API_KEY environment variable.")
            
            with col2:
                if st.button("📊 Movie Analytics", key="analytics"):
                    st.markdown("### 📈 Database Statistics")
                    
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        st.metric("Total Movies", len(self.movies_df))
                    
                    with col_b:
                        if 'vote_average' in self.movies_df.columns:
                            avg_rating = self.movies_df['vote_average'].mean()
                            st.metric("Avg Rating", f"{avg_rating:.1f}")
                        elif 'imdb_rating' in self.movies_df.columns:
                            avg_rating = self.movies_df['imdb_rating'].mean()
                            st.metric("Avg Rating", f"{avg_rating:.1f}")
                    
                    with col_c:
                        if 'year' in self.movies_df.columns:
                            latest_year = self.movies_df['year'].max()
                            st.metric("Latest Year", int(latest_year))
                        elif 'release_date' in self.movies_df.columns:
                            years = pd.to_datetime(self.movies_df['release_date']).dt.year
                            latest_year = years.max()
                            st.metric("Latest Year", int(latest_year))

# Run the application
if __name__ == "__main__":
    app = CinemaAIProApp()
    app.run()
