# Movie recommendation system using pre-computed models from the notebook
import numpy as np
import pandas as pd
import pickle
import os

class MovieRecommender:
    def __init__(self, use_precomputed=True):
        self.new_df = None
        self.similarity = None
        self.vectorizer = None
        self.movies_full = None
        
        if use_precomputed:
            self._load_precomputed_models()
    
    def _load_precomputed_models(self):
        """Load pre-computed models from the notebook pipeline"""
        try:
            # Load the processed dataframe (movie_id, title, tags)
            with open('artifacts/movie_list.pkl', 'rb') as f:
                self.new_df = pickle.load(f)
            
            # Load the similarity matrix
            with open('artifacts/similarity.pkl', 'rb') as f:
                self.similarity = pickle.load(f)
                
            # Load the vectorizer (optional)
            if os.path.exists('artifacts/vectorizer.pkl'):
                with open('artifacts/vectorizer.pkl', 'rb') as f:
                    self.vectorizer = pickle.load(f)
            
            # Load the full movies dataframe (optional, for additional features)
            if os.path.exists('artifacts/movies_full.pkl'):
                with open('artifacts/movies_full.pkl', 'rb') as f:
                    self.movies_full = pickle.load(f)
            
            print(f"✅ Loaded pre-computed models with {len(self.new_df)} movies")
            
        except FileNotFoundError as e:
            print(f"❌ Pre-computed models not found: {e}")
            print("💡 Please run the notebook first to generate the models")
        except Exception as e:
            print(f"❌ Error loading models: {e}")
    
    def recommend(self, movie_title, num_recommendations=10):
        """
        Get movie recommendations using the pre-computed similarity matrix
        This is the same logic from the notebook
        """
        if self.new_df is None or self.similarity is None:
            print("❌ Models not loaded. Please run the notebook first.")
            return pd.DataFrame()
        
        try:
            # Find the movie index (case-insensitive search)
            movie_matches = self.new_df[self.new_df['title'].str.lower() == movie_title.lower()]
            
            if movie_matches.empty:
                print(f"❌ Movie '{movie_title}' not found in database")
                available_movies = self.new_df['title'].head(10).tolist()
                print(f"💡 Try one of these: {', '.join(available_movies)}")
                return pd.DataFrame()
            
            index = movie_matches.index[0]
            
            # Calculate similarity scores using the pre-computed matrix
            distances = sorted(list(enumerate(self.similarity[index])), reverse=True, key=lambda x: x[1])
            
            # Get recommendations (excluding the input movie itself)
            recommendations = []
            for i in distances[1:num_recommendations+1]:
                movie_info = {
                    'title': self.new_df.iloc[i[0]].title,
                    'similarity_score': round(i[1], 3)
                }
                recommendations.append(movie_info)
            
            # Convert to DataFrame
            result_df = pd.DataFrame(recommendations)
            return result_df
            
        except Exception as e:
            print(f"❌ Error in recommendation: {e}")
            return pd.DataFrame()
    
    def get_movie_info(self, movie_title):
        """Get detailed information about a specific movie"""
        if self.new_df is None:
            return None
        
        movie_matches = self.new_df[self.new_df['title'].str.lower() == movie_title.lower()]
        if not movie_matches.empty:
            return movie_matches.iloc[0].to_dict()
        return None
    
    def get_all_movies(self):
        """Get list of all available movies"""
        if self.new_df is not None:
            return self.new_df['title'].tolist()
        return []
    
    def search_movies(self, query):
        """Search movies by title (partial matching)"""
        if self.new_df is None:
            return pd.DataFrame()
        
        # Case-insensitive partial matching
        matches = self.new_df[self.new_df['title'].str.lower().str.contains(query.lower(), na=False)]
        return matches[['title']].head(10)
    
    def get_stats(self):
        """Get statistics about the movie database"""
        if self.new_df is None:
            return {}
        
        return {
            'total_movies': len(self.new_df),
            'similarity_matrix_shape': self.similarity.shape if self.similarity is not None else None,
            'sample_movies': self.new_df['title'].head(5).tolist()
        }