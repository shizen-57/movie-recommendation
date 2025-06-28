"""
Movie Recommendation System using Gemini API
Architecture: Data Processing (pandas/numpy) + AI Recommendations (Gemini)
Author: Enhanced for Gemini Integration
Date: 2025-June-27
"""

import pandas as pd
import numpy as np
import google.generativeai as genai
import requests
import json
from typing import List, Dict, Any
import os
import sys

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from src.data_loader import MovieDataLoader
except ImportError:
    # Fallback for direct imports
    try:
        import sys
        import os
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.append(parent_dir)
        from data_loader import MovieDataLoader
    except ImportError:
        print("Warning: Could not import MovieDataLoader")

class GeminiMovieRecommender:
    def __init__(self, api_key: str):
        """Initialize the Gemini Movie Recommender"""
        self.api_key = api_key
        # Configure Gemini
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Initialize data loader
        try:
            self.data_loader = MovieDataLoader()
        except:
            self.data_loader = None
            print("Warning: MovieDataLoader not available")
        
        self.movies_data = None
        self.ratings_data = None
        self.processed_data = None
        
    def load_sample_movie_data(self):
        """Load movie data using the enhanced data loader"""
        print("📊 Loading movie data...")
        
        if not self.data_loader:
            print("❌ Data loader not available")
            return
        
        # Try to load from CSV files first
        if not self.data_loader.load_from_csv():
            print("📝 No CSV files found, creating enhanced sample data...")
            self.data_loader.create_enhanced_sample_data()
        
        # Get the data
        data = self.data_loader.get_data()
        self.movies_data = data['movies']
        self.ratings_data = data['ratings']
        
        print(f"✅ Loaded {len(self.movies_data)} movies and {len(self.ratings_data)} ratings")
        
    def preprocess_data(self):
        """Use pandas and numpy to clean and process the movie data"""
        if self.movies_data is None:
            self.load_sample_movie_data()
        
        if self.movies_data is None:
            print("❌ No movie data available")
            return None
        
        # Check if we have TMDB 5000 format (with 'id' column) or sample format (with 'movieId')
        if 'id' in self.movies_data.columns:
            # TMDB 5000 format - use as is with some processing
            processed_data = self.movies_data.copy()
            
            # Ensure required columns exist
            if 'vote_average' not in processed_data.columns:
                processed_data['vote_average'] = 6.0  # Default rating
            if 'popularity' not in processed_data.columns:
                processed_data['popularity'] = processed_data.get('vote_count', 100)  # Use vote count as popularity proxy
            
            # Calculate a simple popularity score
            processed_data['popularity_score'] = (
                processed_data.get('vote_average', 6.0) * 0.7 + 
                np.log1p(processed_data.get('vote_count', 100)) * 0.3
            )
            
            self.processed_data = processed_data
            print(f"✅ Processed {len(self.processed_data)} TMDB movies")
            
        elif 'movieId' in self.movies_data.columns:
            # Sample format - use existing logic
            # Merge movies and ratings if both exist
            if self.ratings_data is not None and not self.ratings_data.empty:
                merged_data = pd.merge(self.movies_data, self.ratings_data, on='movieId')
                
                # Calculate statistical features using numpy
                movie_stats = merged_data.groupby(['movieId', 'title', 'genres', 'year']).agg({
                    'rating': ['mean', 'count', 'std'],  # user ratings
                    'imdb_rating': 'first'  # IMDb rating
                }).reset_index()
                
                # Flatten column names
                movie_stats.columns = ['movieId', 'title', 'genres', 'year', 'avg_user_rating', 'num_ratings', 'rating_std', 'imdb_rating']
                
                # Calculate popularity score using numpy
                movie_stats['popularity_score'] = (
                    movie_stats['avg_user_rating'] * 0.4 + 
                    movie_stats['imdb_rating'] * 0.4 + 
                    np.log1p(movie_stats['num_ratings']) * 0.2
                )
                
                self.processed_data = movie_stats
            else:
                # No ratings data - work with movies only
                processed_data = self.movies_data.copy()
                processed_data['popularity_score'] = processed_data.get('imdb_rating', 6.0)
                self.processed_data = processed_data
        else:
            print("❌ Unknown data format - missing 'id' or 'movieId' column")
            return None
        
        # Sort by popularity score if available
        if 'popularity_score' in self.processed_data.columns:
            self.processed_data = self.processed_data.sort_values('popularity_score', ascending=False)
        
        return self.processed_data
    
    def get_movies_by_genre(self, genre: str, limit: int = 10) -> pd.DataFrame:
        """Filter movies by genre"""
        if self.processed_data is None:
            self.preprocess_data()
        
        if self.processed_data is None:
            return pd.DataFrame()
        
        filtered_movies = self.processed_data[
            self.processed_data['genres'].str.contains(genre, case=False, na=False)
        ].head(limit)
        
        return filtered_movies
    
    def get_top_rated_movies(self, limit: int = 20) -> pd.DataFrame:
        """Get top rated movies with sufficient ratings"""
        if self.processed_data is None:
            self.preprocess_data()
        
        if self.processed_data is None:
            return pd.DataFrame()
        
        # Filter movies with good ratings and sort by popularity score
        if 'num_ratings' in self.processed_data.columns:
            top_movies = self.processed_data[
                self.processed_data['num_ratings'] >= 5
            ].head(limit)
        else:
            top_movies = self.processed_data.head(limit)
        
        return top_movies
    
    def format_movies_for_gemini(self, movies_df: pd.DataFrame) -> str:
        """Format movie data for Gemini prompt"""
        movie_list = []
        for _, movie in movies_df.iterrows():
            # Handle different column names
            title = movie.get('title', 'Unknown')
            year = movie.get('year', 'Unknown')
            genres = movie.get('genres', 'Unknown')
            imdb_rating = movie.get('imdb_rating', movie.get('vote_average', 0))
            avg_rating = movie.get('avg_user_rating', imdb_rating/2 if imdb_rating else 4.0)
            popularity = movie.get('popularity_score', avg_rating * 1.5)
            
            movie_info = f"- {title} ({year}) | Genres: {genres} | IMDb: {imdb_rating}/10 | User Rating: {avg_rating:.1f}/5 | Popularity: {popularity:.2f}"
            movie_list.append(movie_info)
        
        return "\n".join(movie_list)
    
    def get_gemini_recommendations(self, user_preference: str, num_recommendations: int = 5) -> str:
        """Get movie recommendations from Gemini based on user preferences"""
        try:
            # Get top movies for context
            top_movies = self.get_top_rated_movies(30)
            if top_movies.empty:
                return "❌ No movie data available for recommendations"
            
            movies_context = self.format_movies_for_gemini(top_movies)
            
            prompt = f"""
You are a movie recommendation expert. Based on the following movie database and user preference, recommend {num_recommendations} movies with detailed explanations.

MOVIE DATABASE:
{movies_context}

USER PREFERENCE: "{user_preference}"

INSTRUCTIONS:
1. Analyze the user's preference and identify key themes, genres, or characteristics they're looking for
2. Select {num_recommendations} movies from the database that best match their preference
3. For each recommendation, provide:
   - Movie title and year
   - Why it matches their preference (2-3 sentences)
   - Key themes/elements that align with their request
   - A brief hook to get them excited about watching it

FORMAT your response as:
🎬 **Movie Title (Year)**
**Why it's perfect for you:** [Explanation]
**Key elements:** [Themes/Genre elements]
**The hook:** [Exciting one-liner about why they should watch]

---

Provide exactly {num_recommendations} recommendations, each clearly separated by the --- line.
"""
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"Error getting recommendations: {str(e)}"
    
    def get_movie_explanation(self, movie_title: str) -> str:
        """Get detailed explanation about a specific movie from Gemini"""
        try:
            if self.processed_data is None:
                self.preprocess_data()
            
            if self.processed_data is None:
                return "❌ No movie data available"
            
            # Get movie details from our database
            movie_info = self.processed_data[
                self.processed_data['title'].str.contains(movie_title, case=False, na=False)
            ]
            
            if movie_info.empty:
                return f"Movie '{movie_title}' not found in our database."
            
            movie = movie_info.iloc[0]
            
            # Handle different column structures
            title = movie.get('title', 'Unknown')
            year = movie.get('year', 'Unknown')
            genres = movie.get('genres', 'Unknown')
            imdb_rating = movie.get('imdb_rating', movie.get('vote_average', 0))
            avg_rating = movie.get('avg_user_rating', imdb_rating/2 if imdb_rating else 4.0)
            overview = movie.get('overview', 'No description available')
            
            prompt = f"""
Provide a detailed analysis of the movie "{title}" ({year}).

Movie Details:
- Title: {title}
- Year: {year}
- Genres: {genres}
- IMDb Rating: {imdb_rating}/10
- User Rating: {avg_rating:.1f}/5
- Plot Overview: {overview}

Please provide:
1. **Plot Summary** (2-3 sentences, no spoilers)
2. **What makes it special** (unique aspects, themes, style)
3. **Who would enjoy it** (target audience, similar movie preferences)
4. **Critical acclaim** (why it's well-regarded)
5. **Emotional impact** (what feelings/thoughts it evokes)

Format your response with clear sections and engaging language.
"""
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"Error getting movie explanation: {str(e)}"
    
    def search_movies_by_description(self, user_query: str, top_k: int = 10) -> Dict[str, Any]:
        """Search movies using natural language descriptions via Gemini AI"""
        try:
            if self.processed_data is None:
                self.preprocess_data()
            
            if self.processed_data is None:
                return {'error': 'No movie data available'}
            
            # Get sample of movies for Gemini to analyze
            sample_movies = self.processed_data.head(min(50, len(self.processed_data)))
            movies_text = self.format_movies_for_gemini(sample_movies)
            
            prompt = f"""
Based on this user query: "{user_query}"

From the following movie database, recommend the top {top_k} movies that best match the user's request:

{movies_text}

Please analyze the user's preferences and provide:
1. Top {top_k} movie recommendations with titles exactly as they appear in the database
2. Brief explanation for each recommendation
3. Overall analysis of what the user is looking for

Format your response as:
RECOMMENDATIONS:
1. [Movie Title] - [Brief explanation]
2. [Movie Title] - [Brief explanation]
etc.

ANALYSIS:
[Your analysis of user preferences]
"""
            
            response = self.model.generate_content(prompt)
            ai_response_text = response.text
            
            # Parse the AI response to extract movie titles and find matching movies
            lines = ai_response_text.split('\n')
            recommended_titles = []
            
            for line in lines:
                if line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.')):
                    # Extract title between the number and the dash
                    parts = line.split(' - ', 1)
                    if len(parts) > 0:
                        title_part = parts[0]
                        # Remove the number prefix
                        title = title_part.split('.', 1)[-1].strip()
                        # Clean up any extra characters
                        title = title.replace('[', '').replace(']', '').strip()
                        recommended_titles.append(title)
            
            # Find matching movies from our database
            movies_list = []
            if recommended_titles and self.processed_data is not None:
                for title in recommended_titles:
                    # Try exact match first
                    exact_match = self.processed_data[self.processed_data['title'].str.lower() == title.lower()]
                    if not exact_match.empty:
                        movie = exact_match.iloc[0]
                        movies_list.append({
                            'id': int(movie.get('id', 0)) if pd.notna(movie.get('id')) else 0,
                            'title': str(movie.get('title', title)),
                            'overview': str(movie.get('overview', 'No description available')),
                            'release_date': str(movie.get('release_date', '')),
                            'vote_average': float(movie.get('vote_average', 0)) if pd.notna(movie.get('vote_average')) else 0,
                            'vote_count': int(movie.get('vote_count', 0)) if pd.notna(movie.get('vote_count')) else 0,
                            'genres': str(movie.get('genres', '')),
                            'popularity': float(movie.get('popularity', 0)) if pd.notna(movie.get('popularity')) else 0
                        })
                    else:
                        # Try partial match
                        partial_match = self.processed_data[self.processed_data['title'].str.contains(title, case=False, na=False)]
                        if not partial_match.empty:
                            movie = partial_match.iloc[0]
                            movies_list.append({
                                'id': int(movie.get('id', 0)) if pd.notna(movie.get('id')) else 0,
                                'title': str(movie.get('title', title)),
                                'overview': str(movie.get('overview', 'No description available')),
                                'release_date': str(movie.get('release_date', '')),
                                'vote_average': float(movie.get('vote_average', 0)) if pd.notna(movie.get('vote_average')) else 0,
                                'vote_count': int(movie.get('vote_count', 0)) if pd.notna(movie.get('vote_count')) else 0,
                                'genres': str(movie.get('genres', '')),
                                'popularity': float(movie.get('popularity', 0)) if pd.notna(movie.get('popularity')) else 0
                            })
            
            # If no movies found from AI recommendations, return some relevant movies based on text search
            if not movies_list and self.processed_data is not None:
                # Fallback: text search in titles and overviews
                text_matches = self.processed_data[
                    self.processed_data['title'].str.contains(user_query, case=False, na=False) |
                    self.processed_data['overview'].str.contains(user_query, case=False, na=False)
                ].head(top_k)
                
                for _, movie in text_matches.iterrows():
                    movies_list.append({
                        'id': int(movie.get('id', 0)) if pd.notna(movie.get('id')) else 0,
                        'title': str(movie.get('title', 'Unknown')),
                        'overview': str(movie.get('overview', 'No description available')),
                        'release_date': str(movie.get('release_date', '')),
                        'vote_average': float(movie.get('vote_average', 0)) if pd.notna(movie.get('vote_average')) else 0,
                        'vote_count': int(movie.get('vote_count', 0)) if pd.notna(movie.get('vote_count')) else 0,
                        'genres': str(movie.get('genres', '')),
                        'popularity': float(movie.get('popularity', 0)) if pd.notna(movie.get('popularity')) else 0
                    })
            
            return {
                'query': user_query,
                'ai_response': ai_response_text,
                'movies': movies_list,
                'total_movies_analyzed': len(sample_movies)
            }
            
        except Exception as e:
            return {'error': f"Search failed: {str(e)}"}
    
    def search_movies(self, query: str, movies_df: pd.DataFrame = None) -> pd.DataFrame:
        """Simple search interface for compatibility"""
        result = self.search_movies_by_description(query, top_k=6)
        
        if 'error' in result:
            return self.get_top_rated_movies(6)  # Return top movies as fallback
        
        # Try to extract movie titles from AI response
        ai_response = result.get('ai_response', '')
        lines = ai_response.split('\n')
        
        recommended_titles = []
        for line in lines:
            if line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.')):
                # Extract title between the number and the dash
                parts = line.split(' - ', 1)
                if len(parts) > 0:
                    title_part = parts[0]
                    # Remove the number prefix
                    title = title_part.split('.', 1)[-1].strip()
                    recommended_titles.append(title)
        
        # Return matching movies from our database
        if recommended_titles and self.processed_data is not None:
            matches = self.processed_data[self.processed_data['title'].isin(recommended_titles)]
            if not matches.empty:
                return matches.head(6)
        
        # Fallback: return some top movies
        return self.get_top_rated_movies(6)

# Alias for backward compatibility
GeminiMovieAI = GeminiMovieRecommender
