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
import speech_recognition as sr
import io
import base64
from werkzeug.utils import secure_filename

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
            print("🔧 For now, using fallback data structure...")
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

@app.route('/api/tv')
def get_tv_shows():
    """Get TV shows from TMDB API with pagination and filtering"""
    try:
        page = int(request.args.get('page', 1))
        search_query = request.args.get('search', '')
        category = request.args.get('category', 'popular')  # popular, top_rated, trending
        
        # If search query provided, use search
        if search_query:
            tmdb_data = search_tmdb_tv(search_query, page=page)
        else:
            # Get TV shows by category
            if category == 'top_rated':
                tmdb_data = get_top_rated_tv_tmdb(page=page)
            elif category == 'trending':
                tmdb_data = get_trending_tv_tmdb(page=page)
            else:  # default to popular
                tmdb_data = get_popular_tv_tmdb(page=page)
        
        if not tmdb_data:
            return jsonify({'error': 'TMDB API not available or configured'}), 503
        
        # Format TV shows for frontend
        tv_list = []
        for tv_show in tmdb_data.get('results', []):
            formatted_tv = format_tmdb_tv(tv_show)
            tv_list.append(formatted_tv)
        
        return jsonify({
            'tv_shows': tv_list,
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
    """Search movies and TV shows using TMDB API or AI"""
    try:
        query = request.args.get('query', '')
        use_ai = request.args.get('ai', 'false').lower() == 'true'
        media_type = request.args.get('media_type', 'multi')  # movie, tv, or multi
        page = int(request.args.get('page', 1))
        
        if not query:
            return jsonify({'error': 'Query parameter is required'}), 400
        
        if use_ai and gemini_ai:
            # AI search: Get a broader set of content first, then let AI analyze
            if media_type == 'tv':
                tmdb_data = search_tmdb_tv(query, page=1)
            elif media_type == 'movie':
                tmdb_data = search_tmdb_movies(query, page=1)
            else:  # multi-search
                # For multi-search, search both movies and TV shows
                movie_data = search_tmdb_movies(query, page=1)
                tv_data = search_tmdb_tv(query, page=1)
                
                # Combine results
                tmdb_data = {
                    'results': [],
                    'total_results': 0,
                    'total_pages': 1
                }
                
                if movie_data and movie_data.get('results'):
                    for movie in movie_data['results'][:10]:  # Limit for performance
                        movie['media_type'] = 'movie'
                        tmdb_data['results'].append(movie)
                
                if tv_data and tv_data.get('results'):
                    for tv in tv_data['results'][:10]:  # Limit for performance
                        tv['media_type'] = 'tv'
                        tmdb_data['results'].append(tv)
                
                tmdb_data['total_results'] = len(tmdb_data['results'])
            
            if tmdb_data and tmdb_data.get('results'):
                # Convert content to format Gemini can analyze
                content_for_ai = []
                for item in tmdb_data['results'][:20]:  # Limit for AI analysis
                    if item.get('media_type') == 'tv' or 'name' in item:
                        # TV show
                        formatted = format_tmdb_tv(item)
                        content_for_ai.append({
                            'id': formatted['id'],
                            'title': formatted['title'],
                            'overview': formatted['overview'],
                            'genres': ', '.join(formatted['genres']),
                            'vote_average': formatted['rating'],
                            'release_date': formatted['release_date'],
                            'media_type': 'tv'
                        })
                    else:
                        # Movie
                        formatted = format_tmdb_movie(item)
                        content_for_ai.append({
                            'id': formatted['id'],
                            'title': formatted['title'],
                            'overview': formatted['overview'],
                            'genres': ', '.join(formatted['genres']),
                            'vote_average': formatted['rating'],
                            'release_date': formatted['release_date'],
                            'media_type': 'movie'
                        })
                
                # Use Gemini AI for intelligent search
                result = gemini_ai.search_movies_by_description(query, top_k=12)
                
                if 'error' not in result and result.get('movies'):
                    # Format AI results and fetch poster images from TMDB
                    content_list = []
                    for item in result['movies']:
                        # Try to get poster from TMDB API using title search
                        poster_path = None
                        backdrop_path = None
                        
                        # Search TMDB for this specific content to get poster
                        if tmdb_api_key:
                            try:
                                # Try both movie and TV search to find the best match
                                movie_search = search_tmdb_movies(item.get('title', ''), page=1)
                                tv_search = search_tmdb_tv(item.get('title', ''), page=1)
                                
                                best_match = None
                                if movie_search and movie_search.get('results'):
                                    best_match = movie_search['results'][0]
                                    best_match['media_type'] = 'movie'
                                elif tv_search and tv_search.get('results'):
                                    best_match = tv_search['results'][0]
                                    best_match['media_type'] = 'tv'
                                
                                if best_match:
                                    poster_path = best_match.get('poster_path')
                                    backdrop_path = best_match.get('backdrop_path')
                            except:
                                pass  # Continue without poster if TMDB search fails
                        
                        content_data = {
                            'id': item.get('id', 0),
                            'title': item.get('title', 'Unknown Title'),
                            'poster_path': poster_path,
                            'backdrop_path': backdrop_path,
                            'overview': item.get('overview', 'No description available'),
                            'release_date': item.get('release_date', ''),
                            'vote_average': float(item.get('vote_average', 0)),
                            'vote_count': item.get('vote_count', 0),
                            'genre_ids': [],
                            'genres': item.get('genres', '').split(', ') if item.get('genres') else [],
                            'media_type': item.get('media_type', 'movie'),
                            'adult': False,
                            'original_language': 'en',
                            'original_title': item.get('title', 'Unknown Title'),
                            'popularity': item.get('popularity', 0),
                            'video': False
                        }
                        content_list.append(content_data)
                    
                    return jsonify({
                        'results': content_list,
                        'ai_response': result.get('ai_response', ''),
                        'total_results': len(content_list),
                        'total_analyzed': result.get('total_movies_analyzed', 0),
                        'source': 'ai_search'
                    })
            
            # Fallback to regular TMDB search if AI fails
        
        # Regular TMDB search
        if media_type == 'tv':
            tmdb_data = search_tmdb_tv(query, page=page)
        elif media_type == 'movie':
            tmdb_data = search_tmdb_movies(query, page=page)
        else:  # multi-search
            # Use TMDB multi-search endpoint if available, otherwise combine results
            tmdb_data = fetch_tmdb_content(f"search/multi", page=page, query=query)
        
        if not tmdb_data:
            return jsonify({'error': 'TMDB API not available'}), 503
        
        # Format results to match expected frontend structure
        content_list = []
        for item in tmdb_data.get('results', []):
            # Determine if it's a movie or TV show
            if item.get('media_type') == 'tv' or 'name' in item:
                # TV show
                content_data = {
                    'id': item.get('id', 0),
                    'title': item.get('name', 'Unknown Title'),  # TV shows use 'name'
                    'poster_path': item.get('poster_path'),
                    'backdrop_path': item.get('backdrop_path'),
                    'overview': item.get('overview', 'No description available'),
                    'release_date': item.get('first_air_date', ''),  # TV shows use 'first_air_date'
                    'vote_average': float(item.get('vote_average', 0)),
                    'vote_count': item.get('vote_count', 0),
                    'genre_ids': item.get('genre_ids', []),
                    'genres': get_genre_names(item.get('genre_ids', [])),
                    'media_type': 'tv',
                    'adult': item.get('adult', False),
                    'original_language': item.get('original_language', 'en'),
                    'original_title': item.get('original_name', item.get('name', '')),
                    'popularity': item.get('popularity', 0),
                    'video': False
                }
            else:
                # Movie
                content_data = {
                    'id': item.get('id', 0),
                    'title': item.get('title', 'Unknown Title'),
                    'poster_path': item.get('poster_path'),
                    'backdrop_path': item.get('backdrop_path'),
                    'overview': item.get('overview', 'No description available'),
                    'release_date': item.get('release_date', ''),
                    'vote_average': float(item.get('vote_average', 0)),
                    'vote_count': item.get('vote_count', 0),
                    'genre_ids': item.get('genre_ids', []),
                    'genres': get_genre_names(item.get('genre_ids', [])),
                    'media_type': 'movie',
                    'adult': item.get('adult', False),
                    'original_language': item.get('original_language', 'en'),
                    'original_title': item.get('original_title', item.get('title', '')),
                    'popularity': item.get('popularity', 0),
                    'video': item.get('video', False)
                }
            content_list.append(content_data)
        
        return jsonify({
            'results': content_list,
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
        
        print(f"Fetching movie details for ID: {movie_id}")  # Debug log
        
        # Fetch movie details from TMDB
        url = f"https://api.themoviedb.org/3/movie/{movie_id}"
        response = requests.get(url, params={'api_key': tmdb_api_key}, timeout=10)
        
        if response.status_code == 200:
            movie = response.json()
            print(f"TMDB movie data received: {movie.get('title', 'Unknown')}")  # Debug log
            
            # Return the movie data in TMDB's native format for frontend compatibility
            return jsonify(movie)
        elif response.status_code == 404:
            return jsonify({'error': 'Movie not found'}), 404
        else:
            return jsonify({'error': f'TMDB API error: {response.status_code}'}), 500
    
    except Exception as e:
        print(f"Error in get_movie_details: {str(e)}")  # Debug log
        return jsonify({'error': str(e)}), 500

@app.route('/api/tv/<int:tv_id>')
def get_tv_details(tv_id):
    """Get detailed information about a specific TV show from TMDB API"""
    try:
        if not tmdb_api_key or tmdb_api_key == "your_tmdb_api_key_here":
            return jsonify({'error': 'TMDB API not configured'}), 503
        
        print(f"Fetching TV show details for ID: {tv_id}")  # Debug log
        
        # Fetch TV show details from TMDB
        url = f"https://api.themoviedb.org/3/tv/{tv_id}"
        response = requests.get(url, params={'api_key': tmdb_api_key}, timeout=10)
        
        if response.status_code == 200:
            tv_show = response.json()
            print(f"TMDB TV show data received: {tv_show.get('name', 'Unknown')}")  # Debug log
            
            # Return the TV show data in TMDB's native format for frontend compatibility
            return jsonify(tv_show)
        elif response.status_code == 404:
            return jsonify({'error': 'TV show not found'}), 404
        else:
            return jsonify({'error': f'TMDB API error: {response.status_code}'}), 500
    
    except Exception as e:
        print(f"Error in get_tv_details: {str(e)}")  # Debug log
        return jsonify({'error': str(e)}), 500

@app.route('/movie/<int:movie_id>/videos')
def get_movie_videos(movie_id):
    """Get videos (trailers, etc.) for a specific movie from TMDB API"""
    try:
        if not tmdb_api_key:
            return jsonify({'results': []})
        
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos"
        response = requests.get(url, params={'api_key': tmdb_api_key}, timeout=10)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'results': []})
    
    except Exception as e:
        return jsonify({'results': []})

@app.route('/tv/<int:tv_id>/videos')
def get_tv_videos(tv_id):
    """Get videos (trailers, etc.) for a specific TV show from TMDB API"""
    try:
        if not tmdb_api_key:
            return jsonify({'results': []})
        
        url = f"https://api.themoviedb.org/3/tv/{tv_id}/videos"
        response = requests.get(url, params={'api_key': tmdb_api_key}, timeout=10)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'results': []})
    
    except Exception as e:
        return jsonify({'results': []})

@app.route('/movie/<int:movie_id>/credits')
def get_movie_credits(movie_id):
    """Get cast and crew for a specific movie from TMDB API"""
    try:
        if not tmdb_api_key:
            return jsonify({'cast': [], 'crew': []})
        
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits"
        response = requests.get(url, params={'api_key': tmdb_api_key}, timeout=10)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'cast': [], 'crew': []})
    
    except Exception as e:
        return jsonify({'cast': [], 'crew': []})

@app.route('/tv/<int:tv_id>/credits')
def get_tv_credits(tv_id):
    """Get cast and crew for a specific TV show from TMDB API"""
    try:
        if not tmdb_api_key:
            return jsonify({'cast': [], 'crew': []})
        
        url = f"https://api.themoviedb.org/3/tv/{tv_id}/credits"
        response = requests.get(url, params={'api_key': tmdb_api_key}, timeout=10)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'cast': [], 'crew': []})
    
    except Exception as e:
        return jsonify({'cast': [], 'crew': []})

@app.route('/movie/<int:movie_id>/similar')
def get_similar_movies(movie_id):
    """Get similar movies from TMDB API"""
    try:
        if not tmdb_api_key:
            return jsonify({'results': []})
        
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/similar"
        response = requests.get(url, params={'api_key': tmdb_api_key}, timeout=10)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'results': []})
    
    except Exception as e:
        return jsonify({'results': []})

@app.route('/tv/<int:tv_id>/similar')
def get_similar_tv(tv_id):
    """Get similar TV shows from TMDB API"""
    try:
        if not tmdb_api_key:
            return jsonify({'results': []})
        
        url = f"https://api.themoviedb.org/3/tv/{tv_id}/similar"
        response = requests.get(url, params={'api_key': tmdb_api_key}, timeout=10)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'results': []})
    
    except Exception as e:
        return jsonify({'results': []})

@app.route('/movie/<int:movie_id>/recommendations')
def get_movie_recommendations_tmdb(movie_id):
    """Get movie recommendations from TMDB API"""
    try:
        if not tmdb_api_key:
            return jsonify({'results': []})
        
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/recommendations"
        response = requests.get(url, params={'api_key': tmdb_api_key}, timeout=10)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'results': []})
    
    except Exception as e:
        return jsonify({'results': []})

@app.route('/tv/<int:tv_id>/recommendations')
def get_tv_recommendations_tmdb(tv_id):
    """Get TV show recommendations from TMDB API"""
    try:
        if not tmdb_api_key:
            return jsonify({'results': []})
        
        url = f"https://api.themoviedb.org/3/tv/{tv_id}/recommendations"
        response = requests.get(url, params={'api_key': tmdb_api_key}, timeout=10)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'results': []})
    
    except Exception as e:
        return jsonify({'results': []})

# TMDB-style endpoints for frontend compatibility  
@app.route('/movie/<int:movie_id>')
def get_movie_details_frontend(movie_id):
    """Get movie details - frontend compatible endpoint"""
    return get_movie_details(movie_id)

@app.route('/tv/<int:tv_id>')  
def get_tv_details_frontend(tv_id):
    """Get TV show details - frontend compatible endpoint"""
    return get_tv_details(tv_id)

# API endpoints for frontend compatibility
@app.route('/api/movie/<int:movie_id>/videos')
def get_movie_videos_api(movie_id):
    """Get movie videos - API endpoint"""
    return get_movie_videos(movie_id)

@app.route('/api/tv/<int:tv_id>/videos')
def get_tv_videos_api(tv_id):
    """Get TV show videos - API endpoint"""
    return get_tv_videos(tv_id)

@app.route('/api/movie/<int:movie_id>/credits')
def get_movie_credits_api(movie_id):
    """Get movie credits - API endpoint"""
    return get_movie_credits(movie_id)

@app.route('/api/tv/<int:tv_id>/credits')
def get_tv_credits_api(tv_id):
    """Get TV show credits - API endpoint"""
    return get_tv_credits(tv_id)

@app.route('/api/movie/<int:movie_id>/similar')
def get_movie_similar_api(movie_id):
    """Get similar movies - API endpoint"""
    return get_similar_movies(movie_id)

@app.route('/api/tv/<int:tv_id>/similar')
def get_tv_similar_api(tv_id):
    """Get similar TV shows - API endpoint"""
    return get_similar_tv(tv_id)

@app.route('/api/movie/<int:movie_id>/recommendations')
def get_movie_recommendations_api(movie_id):
    """Get movie recommendations - API endpoint"""
    return get_movie_recommendations_tmdb(movie_id)

@app.route('/api/tv/<int:tv_id>/recommendations')
def get_tv_recommendations_api(tv_id):
    """Get TV show recommendations - API endpoint"""
    return get_tv_recommendations_tmdb(tv_id)

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

def fetch_tmdb_content(endpoint, page=1, **params):
    """Fetch movies or TV shows from TMDB API (generic function)"""
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
        'poster_path': movie.get('poster_path'),  # Add raw path for frontend
        'backdrop_path': movie.get('backdrop_path'),  # Add raw path for frontend
        'vote_count': movie.get('vote_count', 0),
        'popularity': movie.get('popularity', 0),
        'release_date': movie.get('release_date', ''),
        'original_title': movie.get('original_title', movie.get('title', ''))
    }

def format_tmdb_tv(tv_show):
    """Convert TMDB API TV show format to our standard format"""
    return {
        'id': tv_show.get('id', 0),
        'title': tv_show.get('name', 'Unknown Title'),  # TV shows use 'name' instead of 'title'
        'year': tv_show.get('first_air_date', '')[:4] if tv_show.get('first_air_date') else '',
        'rating': float(tv_show.get('vote_average', 0)),
        'genres': get_genre_names(tv_show.get('genre_ids', [])),
        'overview': tv_show.get('overview', 'No description available'),
        'poster': get_tmdb_poster_url(tv_show.get('poster_path')),
        'backdrop': get_tmdb_poster_url(tv_show.get('backdrop_path'), size='w1280'),
        'poster_path': tv_show.get('poster_path'),  # Add raw path for frontend
        'backdrop_path': tv_show.get('backdrop_path'),  # Add raw path for frontend
        'vote_count': tv_show.get('vote_count', 0),
        'popularity': tv_show.get('popularity', 0),
        'release_date': tv_show.get('first_air_date', ''),  # TV shows use 'first_air_date'
        'original_title': tv_show.get('original_name', tv_show.get('name', ''))
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

def search_tmdb_tv(query, page=1):
    """Search TV shows using TMDB API"""
    return fetch_tmdb_content(f"search/tv", page=page, query=query)

def get_popular_tv_tmdb(page=1):
    """Get popular TV shows from TMDB"""
    return fetch_tmdb_content("tv/popular", page=page)

def get_top_rated_tv_tmdb(page=1):
    """Get top rated TV shows from TMDB"""
    return fetch_tmdb_content("tv/top_rated", page=page)

def get_trending_tv_tmdb(time_window='week', page=1):
    """Get trending TV shows from TMDB"""
    return fetch_tmdb_content(f"trending/tv/{time_window}", page=page)

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

@app.route('/api/voice-search', methods=['POST'])
def voice_search():
    """Process voice search requests"""
    try:
        # Check if audio data is provided
        if 'audio' not in request.json:
            return jsonify({'error': 'No audio data provided'}), 400
        
        # Get the base64 encoded audio data
        audio_data = request.json['audio']
        
        # Decode the base64 audio data
        try:
            # Remove data URL prefix if present
            if ',' in audio_data:
                audio_data = audio_data.split(',')[1]
            
            audio_bytes = base64.b64decode(audio_data)
            
            # Convert audio to text using speech recognition
            recognizer = sr.Recognizer()
            
            # Create an AudioFile from the bytes
            with sr.AudioFile(io.BytesIO(audio_bytes)) as audio_file:
                audio = recognizer.record(audio_file)
                
            # Recognize speech using Google's speech recognition
            try:
                text = recognizer.recognize_google(audio)
                print(f"🎤 Voice search recognized: '{text}'")
                
                # Process the recognized text as a regular search
                return process_voice_search_text(text)
                
            except sr.UnknownValueError:
                return jsonify({'error': 'Could not understand the audio'}), 400
            except sr.RequestError as e:
                return jsonify({'error': f'Speech recognition service error: {str(e)}'}), 500
                
        except Exception as e:
            return jsonify({'error': f'Audio processing error: {str(e)}'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Voice search error: {str(e)}'}), 500

@app.route('/api/voice-search-text', methods=['POST'])
def voice_search_text():
    """Process recognized voice text directly"""
    try:
        if 'text' not in request.json:
            return jsonify({'error': 'No text provided'}), 400
        
        text = request.json['text'].strip()
        if not text:
            return jsonify({'error': 'Empty text provided'}), 400
        
        return process_voice_search_text(text)
        
    except Exception as e:
        return jsonify({'error': f'Voice text search error: {str(e)}'}), 500

def process_voice_search_text(text):
    """Process voice search text and return movie results"""
    try:
        # Enhanced voice search processing with natural language understanding
        enhanced_query = enhance_voice_query(text)
        
        # Use AI search if available
        if gemini_ai:
            # Get movies from TMDB first
            tmdb_data = search_tmdb_movies(enhanced_query, page=1)
            
            if tmdb_data and tmdb_data.get('results'):
                # Convert TMDB movies for AI analysis
                movies_for_ai = []
                for movie in tmdb_data['results'][:25]:  # More movies for voice search
                    formatted = format_tmdb_movie(movie)
                    movies_for_ai.append({
                        'id': formatted['id'],
                        'title': formatted['title'],
                        'overview': formatted['overview'],
                        'genres': ', '.join(formatted['genres']),
                        'vote_average': formatted['rating'],
                        'release_date': formatted['release_date']
                    })
                
                # Use Gemini AI for intelligent voice search analysis
                voice_prompt = f"""
                The user said: "{text}"
                
                This appears to be a voice search for movies. Please analyze what the user is looking for and provide the best movie recommendations from the available data.
                
                Consider:
                - Natural speech patterns and colloquialisms
                - Possible misheard words or speech recognition errors
                - User intent (genre, mood, actors, directors, themes)
                - Similar sounding movie titles
                
                Available movies: {movies_for_ai[:15]}
                
                Provide 8-10 best matching movies with explanations.
                """
                
                result = gemini_ai.search_movies_by_description(voice_prompt, top_k=10)
                
                if 'error' not in result and result.get('movies'):
                    # Format AI results
                    movies_list = []
                    for movie in result['movies']:
                        # Get poster from TMDB
                        poster_path = None
                        backdrop_path = None
                        
                        if tmdb_api_key:
                            try:
                                search_result = search_tmdb_movies(movie.get('title', ''), page=1)
                                if search_result and search_result.get('results'):
                                    tmdb_movie = search_result['results'][0]
                                    poster_path = tmdb_movie.get('poster_path')
                                    backdrop_path = tmdb_movie.get('backdrop_path')
                            except:
                                pass
                        
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
                            'voice_confidence': 0.9,  # High confidence for AI results
                            'search_method': 'voice_ai'
                        }
                        movies_list.append(movie_data)
                    
                    return jsonify({
                        'success': True,
                        'recognized_text': text,
                        'enhanced_query': enhanced_query,
                        'results': movies_list,
                        'ai_response': result.get('ai_response', ''),
                        'total_results': len(movies_list),
                        'source': 'voice_ai_search',
                        'message': f"Found {len(movies_list)} movies based on your voice search"
                    })
        
        # Fallback to regular TMDB search
        tmdb_data = search_tmdb_movies(enhanced_query, page=1)
        
        if not tmdb_data:
            return jsonify({'error': 'Search service not available'}), 503
        
        # Format results
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
                'voice_confidence': 0.8,  # Good confidence for TMDB results
                'search_method': 'voice_tmdb'
            }
            movies_list.append(movie_data)
        
        return jsonify({
            'success': True,
            'recognized_text': text,
            'enhanced_query': enhanced_query,
            'results': movies_list,
            'total_results': tmdb_data.get('total_results', 0),
            'source': 'voice_tmdb_search',
            'message': f"Found {len(movies_list)} movies for '{text}'"
        })
        
    except Exception as e:
        return jsonify({'error': f'Voice search processing error: {str(e)}'}), 500

def enhance_voice_query(text):
    """Enhance voice search query to handle speech recognition quirks"""
    # Common voice search enhancements
    enhancements = {
        # Handle common speech recognition errors
        'axion': 'action',
        'akshun': 'action',
        'comidy': 'comedy',
        'horrer': 'horror',
        'syfy': 'sci-fi',
        'sifi': 'sci-fi',
        'fantacy': 'fantasy',
        'advanture': 'adventure',
        'cartun': 'cartoon',
        'cartoons': 'animation',
        'animeted': 'animated',
        'moovie': 'movie',
        'fillm': 'film',
        'holly wood': 'hollywood',
        'actors': 'actor',
        'actres': 'actress',
        
        # Handle common phrases
        'funny movies': 'comedy movies',
        'scary movies': 'horror movies',
        'kids movies': 'family animation',
        'superhero movies': 'superhero action',
        'robot movies': 'sci-fi robots',
        'space movies': 'sci-fi space',
        'war movies': 'war action',
        'old movies': 'classic movies',
        'new movies': 'recent movies',
        'best movies': 'top rated',
        'good movies': 'highly rated',
        
        # Handle actor name variations
        'tom cruse': 'tom cruise',
        'will smyth': 'will smith',
        'robert downy': 'robert downey',
        'scarlet johnson': 'scarlett johansson',
        'leonardo dicaprio': 'leonardo dicaprio',
        'brad pit': 'brad pitt',
        
        # Movie title corrections
        'avengers end game': 'avengers endgame',
        'star wars': 'star wars',
        'harry poter': 'harry potter',
        'jurrasic park': 'jurassic park',
        'fast and furious': 'fast furious',
    }
    
    # Convert to lowercase for processing
    enhanced = text.lower()
    
    # Apply enhancements
    for wrong, right in enhancements.items():
        enhanced = enhanced.replace(wrong, right)
    
    # Remove filler words common in speech
    filler_words = ['um', 'uh', 'like', 'you know', 'basically', 'actually', 'literally']
    words = enhanced.split()
    enhanced_words = [word for word in words if word not in filler_words]
    
    return ' '.join(enhanced_words) if enhanced_words else text

@app.route('/api/voice-search/status')
def voice_search_status():
    """Check if voice search is available"""
    try:
        # Check if speech recognition is available
        import speech_recognition as sr
        return jsonify({
            'available': True,
            'message': 'Voice search is available',
            'supported_languages': ['en-US', 'en-GB', 'en-CA', 'en-AU'],
            'features': [
                'Natural language processing',
                'Speech recognition error correction',
                'AI-powered movie understanding',
                'Voice query enhancement'
            ]
        })
    except ImportError:
        return jsonify({
            'available': False,
            'message': 'Voice search not available - speech recognition library not installed',
            'install_command': 'pip install SpeechRecognition pyaudio'
        })
    except Exception as e:
        return jsonify({
            'available': False,
            'message': f'Voice search error: {str(e)}'
        })

@app.route('/api/voice-search/test')
def test_voice_search():
    """Test voice search functionality"""
    try:
        # Test with a sample query
        test_query = "action movies with superheroes"
        result = process_voice_search_text(test_query)
        
        if result.status_code == 200:
            return jsonify({
                'status': 'success',
                'message': 'Voice search is working correctly',
                'test_query': test_query,
                'test_results': result.get_json()
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Voice search test failed',
                'error': result.get_json()
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Voice search test error: {str(e)}'
        })

@app.route('/api/configuration')
def get_tmdb_configuration():
    """Get TMDB API configuration for frontend"""
    return jsonify({
        "images": {
            "secure_base_url": "https://image.tmdb.org/t/p/",
            "base_url": "http://image.tmdb.org/t/p/",
            "backdrop_sizes": ["w300", "w780", "w1280", "original"],
            "logo_sizes": ["w45", "w92", "w154", "w185", "w300", "w500", "original"],
            "poster_sizes": ["w92", "w154", "w185", "w342", "w500", "w780", "original"],
            "profile_sizes": ["w45", "w185", "h632", "original"],
            "still_sizes": ["w92", "w185", "w300", "original"]
        },
        "change_keys": []
    })

@app.route('/configuration')
def get_tmdb_configuration_legacy():
    """Legacy endpoint for TMDB configuration (frontend compatibility)"""
    return get_tmdb_configuration()

@app.route('/genre/<media_type>/list')
def get_genres(media_type):
    """Get genre list for movies or TV shows"""
    if not tmdb_api_key:
        return jsonify({'error': 'TMDB API not available'}), 503
    
    try:
        if media_type not in ['movie', 'tv']:
            return jsonify({'error': 'Invalid media type'}), 400
        
        url = f"https://api.themoviedb.org/3/genre/{media_type}/list"
        response = requests.get(url, params={'api_key': tmdb_api_key}, timeout=10)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': f'TMDB API error: {response.status_code}'}), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Start the Flask server
if __name__ == '__main__':
    print("🎬 Starting Movie Recommender Flask Server...")
    print("🚀 Server will be available at: http://localhost:5000")
    print("📝 API Endpoints:")
    print("   - GET  /api/search - Search movies")
    print("   - POST /api/voice-search - Voice search with audio")
    print("   - POST /api/voice-search-text - Voice search with text")
    print("   - GET  /api/voice-search/status - Voice search status")
    print("   - GET  /api/voice-search/test - Test voice search")
    print("-" * 50)
    
    # Initialize data and services
    print("🔧 Initializing services...")
    initialize_data()
    print("✅ Initialization complete!")
    print("-" * 50)
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        input("Press Enter to exit...")
