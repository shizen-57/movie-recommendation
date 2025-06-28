"""
Flask Web Server for CinemaAI Pro
Serves the React frontend and provides API endpoints for movie recommendations
"""

from flask import Flask, render_template, jsonify, request, send_from_directory, send_file
from flask_cors import CORS
import os
import sys
import pandas as pd
import json
import requests
import random

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.data_loader import MovieDataLoader
    from src.ai.gemini import GeminiMovieRecommender
    from src.recommender import MovieRecommender
except ImportError as e:
    print(f"Warning: Could not import modules: {e}")

app = Flask(__name__)
CORS(app)

# Global variables for data and models
movies_df = None
gemini_ai = None
movie_recommender = None
tmdb_api_key = None

# List of TMDB API keys (replace with your actual keys)
TMDB_API_KEYS = [
    "611f5b9b659c50118c4488a0dd035ece",
    # Add more keys as needed
]

def initialize_data():
    """Initialize TMDB API and AI models"""
    global movies_df, gemini_ai, movie_recommender, tmdb_api_key
    
    try:
        # Randomly select a TMDB API key from the list
        if not TMDB_API_KEYS or all('REPLACE_WITH_YOUR_KEY' in k for k in TMDB_API_KEYS):
            print("⚠️ Warning: No valid TMDB API keys provided. Please update TMDB_API_KEYS in web_server.py.")
            print("📝 You can get an API key from: https://www.themoviedb.org/settings/api")
            print("� For now, using fallback data structure...")
            tmdb_api_key = None
            movies_df = pd.DataFrame(columns=['id', 'title', 'overview', 'release_date', 'vote_average', 'genres'])
        else:
            tmdb_api_key = random.choice(TMDB_API_KEYS)
            print(f"🔑 TMDB API key selected: {tmdb_api_key[:6]}... (hidden)")
            print(f"🌐 Using live TMDB API for movie data")
            
            # Test TMDB API connection
            test_response = requests.get(
                f"https://api.themoviedb.org/3/movie/popular",
                params={'api_key': tmdb_api_key, 'page': 1}
            )
            
            if test_response.status_code == 200:
                print(f"✅ TMDB API connection successful")
            else:
                print(f"❌ TMDB API connection failed: {test_response.status_code}")
        
        # Initialize Gemini AI
        gemini_api_key = os.getenv("GEMINI_API_KEY", "AIzaSyDJ3TY3gZP2g8yiV40sc-3a1gevGuHUXIU")
        if gemini_api_key:
            try:
                gemini_ai = GeminiMovieRecommender(gemini_api_key)
                print("🤖 Gemini AI recommender initialized")
            except Exception as e:
                print(f"⚠️ Gemini AI initialization failed: {e}")
                gemini_ai = None
        
        # Initialize movie recommender
        movie_recommender = MovieRecommender()
        
    except Exception as e:
        print(f"❌ Error initializing data: {e}")

@app.route('/')
def index():
    """Serve the React frontend"""
    return send_from_directory('frontend/dist', 'index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve React build static files"""
    return send_from_directory('frontend/dist/static', filename)

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    """Serve React build assets"""
    return send_from_directory('frontend/dist/assets', filename)

# Catch-all route for React Router
@app.route('/<path:path>')
def catch_all(path):
    """Serve React app for all routes (SPA routing)"""
    if path.startswith('api/'):
        return jsonify({'error': 'API endpoint not found'}), 404
    return send_from_directory('frontend/dist', 'index.html')

@app.route('/api/movies')
def get_movies():
    """Get movies from TMDB API with pagination and filtering"""
    try:
        page = int(request.args.get('page', 1))
        search_query = request.args.get('search', '')
        category = request.args.get('category', 'popular')  # popular, top_rated, trending
        
        # If search query provided, use search
        if search_query:
            tmdb_data = search_tmdb_movies(search_query, page=page)
        else:
            # Get movies by category
            if category == 'top_rated':
                tmdb_data = get_top_rated_movies_tmdb(page=page)
            elif category == 'trending':
                tmdb_data = get_trending_movies_tmdb(page=page)
            else:  # default to popular
                tmdb_data = get_popular_movies_tmdb(page=page)
        
        if not tmdb_data:
            return jsonify({'error': 'TMDB API not available or configured'}), 503
        
        # Format movies for frontend
        movies_list = []
        for movie in tmdb_data.get('results', []):
            formatted_movie = format_tmdb_movie(movie)
            movies_list.append(formatted_movie)
        
        return jsonify({
            'movies': movies_list,
            'total': tmdb_data.get('total_results', 0),
            'page': page,
            'total_pages': tmdb_data.get('total_pages', 1),
            'has_more': page < tmdb_data.get('total_pages', 1),
            'source': 'tmdb_api'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search')
def search_movies():
    """Search movies using TMDB API or AI"""
    try:
        query = request.args.get('query', '')
        use_ai = request.args.get('ai', 'false').lower() == 'true'
        page = int(request.args.get('page', 1))
        
        if not query:
            return jsonify({'error': 'Query parameter is required'}), 400
        
        if use_ai and gemini_ai:
            # AI search: Get movies from TMDB first, then let AI analyze and filter
            
            # For queries like "latest movies", get recent/trending movies
            if any(word in query.lower() for word in ['latest', 'recent', 'new', 'current']):
                tmdb_data = get_trending_movies_tmdb(page=1)
            # For queries like "popular", get popular movies  
            elif any(word in query.lower() for word in ['popular', 'trending', 'best']):
                tmdb_data = get_popular_movies_tmdb(page=1)
            # For specific searches, try search first
            else:
                tmdb_data = search_tmdb_movies(query, page=1)
                # If search doesn't return enough results, get popular movies as fallback
                if not tmdb_data or len(tmdb_data.get('results', [])) < 5:
                    tmdb_data = get_popular_movies_tmdb(page=1)
            
            if tmdb_data and tmdb_data.get('results'):
                # Format movies for AI analysis
                movies_for_ai = []
                for movie in tmdb_data['results'][:20]:  # Limit for AI analysis
                    formatted = format_tmdb_movie(movie)
                    movies_for_ai.append({
                        'id': formatted['id'],
                        'title': formatted['title'],
                        'overview': formatted['overview'],
                        'genres': ', '.join(formatted['genres']),
                        'vote_average': formatted['rating'],
                        'release_date': formatted['release_date']
                    })
                
                # Use AI to analyze and filter the movies based on the query
                try:
                    # Create a custom AI analysis request
                    ai_prompt = f"Based on the query '{query}', analyze and recommend the most relevant movies from this list. Return the top 10-12 most relevant movies."
                    result = gemini_ai.search_movies_by_description(query, top_k=12)
                    
                    if 'error' not in result and result.get('movies'):
                        # Use AI results
                        ai_movies = result['movies']
                    else:
                        # Fallback: return the TMDB movies directly
                        ai_movies = movies_for_ai[:12]
                except Exception as e:
                    print(f"AI analysis failed: {e}")
                    # Fallback: return the TMDB movies directly
                    ai_movies = movies_for_ai[:12]
                
                # Format AI results and fetch poster images from TMDB
                movies_list = []
                for movie in ai_movies:
                    # Try to get poster from TMDB API using movie title search
                    poster_path = None
                    backdrop_path = None
                    
                    # Search TMDB for this specific movie to get poster
                    if tmdb_api_key:
                        try:
                            search_result = search_tmdb_movies(movie.get('title', ''), page=1)
                            if search_result and search_result.get('results'):
                                # Find the best match (first result is usually most relevant)
                                tmdb_movie = search_result['results'][0]
                                poster_path = tmdb_movie.get('poster_path')
                                backdrop_path = tmdb_movie.get('backdrop_path')
                        except:
                            pass  # Continue without poster if TMDB search fails
                    
                    movie_data = {
                        'id': movie.get('id', 0),
                        'title': movie.get('title', 'Unknown Title'),
                        'poster_path': poster_path,
                        'backdrop_path': backdrop_path,
                        'overview': movie.get('overview', 'No description available'),
                        'release_date': movie.get('release_date', ''),
                        'vote_average': float(movie.get('vote_average', 0)),
                        'vote_count': movie.get('vote_count', 0),
                        'genre_ids': [],
                        'genres': movie.get('genres', '').split(', ') if movie.get('genres') else [],
                        'media_type': 'movie',
                        'adult': False,
                        'original_language': 'en',
                        'original_title': movie.get('title', 'Unknown Title'),
                        'popularity': movie.get('popularity', 0),
                        'video': False
                    }
                    movies_list.append(movie_data)
                
                return jsonify({
                    'results': movies_list,
                    'ai_response': result.get('ai_response', f'Found {len(movies_list)} movies matching "{query}"'),
                    'total_results': len(movies_list),
                    'total_analyzed': len(movies_for_ai),
                    'source': 'ai_search'
                })
            
            # Fallback to regular TMDB search if AI fails
            
        # Regular TMDB search
        tmdb_data = search_tmdb_movies(query, page=page)
        
        if not tmdb_data:
            return jsonify({'error': 'TMDB API not available'}), 503
        
        # Format results to match expected frontend structure
        movies_list = []
        for movie in tmdb_data.get('results', []):
            movie_data = {
                'id': movie.get('id', 0),
                'title': movie.get('title', 'Unknown Title'),
                'poster_path': movie.get('poster_path'),
                'backdrop_path': movie.get('backdrop_path'),
                'overview': movie.get('overview', 'No description available'),
                'release_date': movie.get('release_date', ''),
                'vote_average': float(movie.get('vote_average', 0)),
                'vote_count': movie.get('vote_count', 0),
                'genre_ids': movie.get('genre_ids', []),
                'genres': get_genre_names(movie.get('genre_ids', [])),
                'media_type': 'movie',
                'adult': movie.get('adult', False),
                'original_language': movie.get('original_language', 'en'),
                'original_title': movie.get('original_title', movie.get('title', '')),
                'popularity': movie.get('popularity', 0),
                'video': movie.get('video', False)
            }
            movies_list.append(movie_data)
        
        return jsonify({
            'results': movies_list,
            'total_results': tmdb_data.get('total_results', 0),
            'page': page,
            'total_pages': tmdb_data.get('total_pages', 1),
            'source': 'tmdb_search'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/recommendations/<movie_title>')
def get_recommendations(movie_title):
    """Get AI-powered recommendations for a movie"""
    try:
        if gemini_ai:
            result = gemini_ai.get_enhanced_recommendations(movie_title, 6)
            
            if 'error' not in result:
                recommendations = []
                for movie in result.get('recommendations', []):
                    recommendations.append({
                        'title': movie.get('title', ''),
                        'similarity_score': movie.get('similarity_score', 0),
                        'tags': movie.get('tags', ''),
                        'poster': get_poster_url(movie.get('title', ''), movie.get('id'))
                    })
                
                return jsonify({
                    'recommendations': recommendations,
                    'ai_analysis': result.get('ai_analysis', '')
                })
            else:
                return jsonify({'error': result['error']}), 500
        else:
            return jsonify({'error': 'AI recommendations not available'}), 503
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/movie/<int:movie_id>')
def get_movie_details(movie_id):
    """Get detailed information about a specific movie from TMDB API"""
    try:
        if not tmdb_api_key or tmdb_api_key == "your_tmdb_api_key_here":
            return jsonify({'error': 'TMDB API not configured'}), 503
        
        # Fetch movie details from TMDB
        url = f"https://api.themoviedb.org/3/movie/{movie_id}"
        response = requests.get(url, params={'api_key': tmdb_api_key}, timeout=10)
        
        if response.status_code == 200:
            movie = response.json()
            
            movie_data = {
                'id': movie.get('id', movie_id),
                'title': movie.get('title', 'Unknown Title'),
                'year': movie.get('release_date', '')[:4] if movie.get('release_date') else '',
                'rating': float(movie.get('vote_average', 0)),
                'genres': [genre['name'] for genre in movie.get('genres', [])],
                'overview': movie.get('overview', 'No description available'),
                'poster': get_tmdb_poster_url(movie.get('poster_path')),
                'backdrop': get_tmdb_poster_url(movie.get('backdrop_path'), 'original'),
                'runtime': movie.get('runtime', 'Unknown'),
                'budget': movie.get('budget', 0),
                'revenue': movie.get('revenue', 0),
                'vote_count': movie.get('vote_count', 0),
                'popularity': movie.get('popularity', 0),
                'release_date': movie.get('release_date', ''),
                'original_title': movie.get('original_title', movie.get('title', '')),
                'tagline': movie.get('tagline', ''),
                'homepage': movie.get('homepage', ''),
                'status': movie.get('status', ''),
                'production_companies': [company['name'] for company in movie.get('production_companies', [])],
                'production_countries': [country['name'] for country in movie.get('production_countries', [])]
            }
            return jsonify(movie_data)
        elif response.status_code == 404:
            return jsonify({'error': 'Movie not found'}), 404
        else:
            return jsonify({'error': f'TMDB API error: {response.status_code}'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# TMDB API helper functions
def fetch_tmdb_movies(endpoint, page=1, **params):
    """Fetch movies from TMDB API"""
    if not tmdb_api_key or tmdb_api_key == "your_tmdb_api_key_here":
        return None
    
    try:
        url = f"https://api.themoviedb.org/3/{endpoint}"
        params['api_key'] = tmdb_api_key
        params['page'] = page
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"TMDB API Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"TMDB API Request Error: {e}")
        return None

def format_tmdb_movie(movie):
    """Convert TMDB API movie format to our standard format"""
    return {
        'id': movie.get('id', 0),
        'title': movie.get('title', 'Unknown Title'),
        'year': movie.get('release_date', '')[:4] if movie.get('release_date') else '',
        'rating': float(movie.get('vote_average', 0)),
        'genres': get_genre_names(movie.get('genre_ids', [])),
        'overview': movie.get('overview', 'No description available'),
        'poster': get_tmdb_poster_url(movie.get('poster_path')),
        'backdrop': get_tmdb_poster_url(movie.get('backdrop_path'), size='w1280'),
        'vote_count': movie.get('vote_count', 0),
        'popularity': movie.get('popularity', 0),
        'release_date': movie.get('release_date', ''),
        'original_title': movie.get('original_title', movie.get('title', ''))
    }

def get_tmdb_poster_url(poster_path, size='w500'):
    """Get full TMDB poster URL"""
    if poster_path:
        return f"https://image.tmdb.org/t/p/{size}{poster_path}"
    return None

def get_genre_names(genre_ids):
    """Convert genre IDs to genre names"""
    # TMDB genre mapping
    genre_map = {
        28: "Action", 12: "Adventure", 16: "Animation", 35: "Comedy", 80: "Crime",
        99: "Documentary", 18: "Drama", 10751: "Family", 14: "Fantasy", 36: "History",
        27: "Horror", 10402: "Music", 9648: "Mystery", 10749: "Romance", 878: "Science Fiction",
        10770: "TV Movie", 53: "Thriller", 10752: "War", 37: "Western"
    }
    
    return [genre_map.get(gid, f"Genre-{gid}") for gid in genre_ids]

def search_tmdb_movies(query, page=1):
    """Search movies using TMDB API"""
    return fetch_tmdb_movies(f"search/movie", page=page, query=query)

def get_popular_movies_tmdb(page=1):
    """Get popular movies from TMDB"""
    return fetch_tmdb_movies("movie/popular", page=page)

def get_top_rated_movies_tmdb(page=1):
    """Get top rated movies from TMDB"""
    return fetch_tmdb_movies("movie/top_rated", page=page)

def get_trending_movies_tmdb(time_window='week', page=1):
    """Get trending movies from TMDB"""
    return fetch_tmdb_movies(f"trending/movie/{time_window}", page=page)

def extract_year(date_str):
    """Extract year from date string"""
    if isinstance(date_str, str) and len(date_str) >= 4:
        return date_str[:4]
    return str(date_str) if date_str else ''

def parse_genres(genres_str):
    """Parse genres string into list"""
    if pd.isna(genres_str) or not genres_str:
        return ['Unknown']
    
    if isinstance(genres_str, str):
        # Handle different genre formats
        if '|' in genres_str:
            return genres_str.split('|')[:3]  # Max 3 genres
        elif ',' in genres_str:
            return [g.strip() for g in genres_str.split(',')][:3]
        else:
            return [genres_str]
    
    return ['Unknown']

def get_poster_url(title, movie_id=None):
    """Get movie poster URL - enhanced version with TMDB API fallback"""
    
    # Option 1: Try TMDB API if we have a movie ID (optional feature)
    if movie_id and os.getenv('TMDB_API_KEY'):
        try:
            tmdb_api_key = os.getenv('TMDB_API_KEY')
            url = f"https://api.themoviedb.org/3/movie/{movie_id}"
            response = requests.get(url, params={'api_key': tmdb_api_key}, timeout=2)
            if response.status_code == 200:
                data = response.json()
                if data.get('poster_path'):
                    return f"https://image.tmdb.org/t/p/w500{data['poster_path']}"
        except:
            pass  # Fallback to placeholder if API fails
    
    # Option 2: Enhanced placeholder with better styling and movie title
    title_clean = title.replace(' ', '+').replace(':', '').replace('?', '').replace('&', 'and')
    
    # Use a more sophisticated placeholder service with better colors
    # Dark theme placeholders that match the movie app aesthetic
    base_url = "https://via.placeholder.com/500x750"
    background_colors = [
        "1a1a1a",  # Dark charcoal
        "2c3e50",  # Dark blue
        "34495e",  # Dark slate
        "27ae60",  # Dark green
        "8e44ad",  # Dark purple
        "e74c3c",  # Dark red
        "f39c12",  # Dark orange
    ]
    
    # Use title length to pick a consistent color for each movie
    color_index = hash(title) % len(background_colors)
    bg_color = background_colors[color_index]
    
    return f"{base_url}/{bg_color}/ffffff?text={title_clean}"

if __name__ == '__main__':
    print("🎬 Initializing CinemaAI Pro...")
    initialize_data()
    print("🚀 Starting web server...")
    app.run(debug=True, host='0.0.0.0', port=5000)
