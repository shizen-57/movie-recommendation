"""
Advanced Data Loader for Movie Recommendation System
Supports multiple data sources: CSV files, online datasets, APIs
"""

import pandas as pd
import numpy as np
import requests
import os
from typing import Optional, Dict, List
from datetime import datetime

class MovieDataLoader:
    """Enhanced data loader for movie datasets"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.movies_df = None
        self.ratings_df = None
        
    def download_movielens_dataset(self, size: str = "small") -> bool:
        """Download MovieLens dataset"""
        try:
            if size == "small":
                url = "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
                filename = "ml-latest-small.zip"
            else:
                url = "https://files.grouplens.org/datasets/movielens/ml-25m.zip"
                filename = "ml-25m.zip"
            
            print(f"📥 Downloading MovieLens {size} dataset...")
            
            # Create data directory if it doesn't exist
            os.makedirs(self.data_dir, exist_ok=True)
            
            # Download and extract
            import zipfile
            response = requests.get(url)
            zip_path = os.path.join(self.data_dir, filename)
            
            with open(zip_path, 'wb') as f:
                f.write(response.content)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.data_dir)
            
            # Remove zip file
            os.remove(zip_path)
            
            print("✅ Dataset downloaded successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error downloading dataset: {e}")
            return False
    
    def load_from_csv(self, movies_file: str = None, ratings_file: str = None) -> bool:
        """Load movie data from CSV files"""
        try:
            # Try to find CSV files automatically
            if movies_file is None:
                potential_files = [
                    os.path.join(self.data_dir, "movies.csv"),
                    os.path.join(self.data_dir, "ml-latest-small", "movies.csv"),
                    os.path.join(self.data_dir, "ml-25m", "movies.csv"),
                    os.path.join(self.data_dir, "tmdb_5000_movies.csv")
                ]
                for file in potential_files:
                    if os.path.exists(file):
                        movies_file = file
                        break
            
            if ratings_file is None:
                potential_files = [
                    os.path.join(self.data_dir, "ratings.csv"),
                    os.path.join(self.data_dir, "ml-latest-small", "ratings.csv"),
                    os.path.join(self.data_dir, "ml-25m", "ratings.csv"),
                    os.path.join(self.data_dir, "tmdb_5000_credits.csv")
                ]
                for file in potential_files:
                    if os.path.exists(file):
                        ratings_file = file
                        break
            
            if movies_file and os.path.exists(movies_file):
                print(f"📖 Loading movies from: {movies_file}")
                self.movies_df = pd.read_csv(movies_file)
                print(f"✅ Loaded {len(self.movies_df)} movies")
            
            if ratings_file and os.path.exists(ratings_file):
                print(f"📖 Loading ratings from: {ratings_file}")
                self.ratings_df = pd.read_csv(ratings_file)
                print(f"✅ Loaded {len(self.ratings_df)} ratings")
            
            return self.movies_df is not None
            
        except Exception as e:
            print(f"❌ Error loading CSV files: {e}")
            return False
    
    def create_enhanced_sample_data(self) -> Dict[str, pd.DataFrame]:
        """Create an enhanced sample dataset with more variety"""
        print("🎬 Creating enhanced sample movie dataset...")
        
        # Enhanced movie data with more variety
        movies_data = {
            'movieId': list(range(1, 101)),
            'title': [
                # Popular blockbusters
                'Avatar', 'Avengers: Endgame', 'Titanic', 'Star Wars: The Force Awakens',
                'Avengers: Infinity War', 'Spider-Man: No Way Home', 'Jurassic World',
                'The Lion King (2019)', 'The Avengers', 'Furious 7',
                
                # Classic films
                'The Godfather', 'The Shawshank Redemption', 'Schindler\'s List', 
                'Raging Bull', 'Casablanca', 'Gone with the Wind',
                'Lawrence of Arabia', 'The Wizard of Oz', 'Sunset Boulevard',
                'Vertigo',
                
                # Recent acclaimed films
                'Parasite', 'Nomadland', 'Minari', 'Sound of Metal', 'The Trial of the Chicago 7',
                'Mank', 'Judas and the Black Messiah', 'Promising Young Woman',
                'Soul', 'Another Round',
                
                # Sci-Fi & Fantasy
                'Blade Runner 2049', 'Dune', 'Interstellar', 'Inception', 'The Matrix',
                'Star Wars: A New Hope', 'E.T. the Extra-Terrestrial', 'Close Encounters of the Third Kind',
                'Alien', '2001: A Space Odyssey',
                
                # Action & Adventure
                'Mad Max: Fury Road', 'John Wick', 'Mission: Impossible - Fallout',
                'The Dark Knight', 'Heat', 'Die Hard', 'Raiders of the Lost Ark',
                'Terminator 2: Judgment Day', 'Aliens', 'The Matrix Reloaded',
                
                # Comedy
                'The Grand Budapest Hotel', 'Parasite', 'Knives Out', 'Jojo Rabbit',
                'Once Upon a Time in Hollywood', 'The Big Lebowski', 'Pulp Fiction',
                'Goodfellas', 'Some Like It Hot', 'Dr. Strangelove',
                
                # Drama
                'Manchester by the Sea', 'Moonlight', 'La La Land', 'Spotlight',
                'Birdman', '12 Years a Slave', 'Argo', 'The Artist',
                'The King\'s Speech', 'Slumdog Millionaire',
                
                # Horror & Thriller
                'Get Out', 'A Quiet Place', 'Hereditary', 'The Babadook',
                'It Follows', 'Psycho', 'The Silence of the Lambs', 'Se7en',
                'The Sixth Sense', 'Jaws',
                
                # Animation
                'Spirited Away', 'Toy Story', 'Finding Nemo', 'WALL-E',
                'Inside Out', 'Coco', 'Moana', 'Frozen', 'Zootopia', 'Up',
                
                # International Cinema
                'Roma', 'Amour', 'The Lives of Others', 'City of God',
                'Amélie', 'Life is Beautiful', 'Cinema Paradiso', 'Seven Samurai',
                'Tokyo Story', 'Bicycle Thieves'
            ],
            'genres': [
                # Corresponding genres for the movies above
                'Action|Adventure|Fantasy|Sci-Fi', 'Action|Adventure|Drama|Sci-Fi', 
                'Drama|Romance', 'Action|Adventure|Fantasy|Sci-Fi',
                'Action|Adventure|Sci-Fi', 'Action|Adventure|Sci-Fi', 'Action|Adventure|Sci-Fi',
                'Animation|Adventure|Drama|Family', 'Action|Adventure|Sci-Fi', 'Action|Crime|Thriller',
                
                'Crime|Drama', 'Drama', 'Biography|Drama|History', 
                'Biography|Drama|Sport', 'Drama|Romance|War', 'Drama|Romance|War',
                'Adventure|Biography|Drama|History', 'Adventure|Family|Fantasy|Musical', 'Drama|Film-Noir|Romance',
                'Mystery|Romance|Thriller',
                
                'Comedy|Drama|Thriller', 'Drama', 'Drama', 'Drama|Music', 'Drama|History',
                'Biography|Drama', 'Biography|Crime|Drama|History', 'Crime|Drama|Thriller',
                'Animation|Drama|Family|Fantasy', 'Comedy|Drama',
                
                'Drama|Mystery|Sci-Fi|Thriller', 'Adventure|Drama|Sci-Fi', 'Adventure|Drama|Sci-Fi', 
                'Action|Crime|Drama|Mystery|Sci-Fi|Thriller', 'Action|Sci-Fi',
                'Action|Adventure|Fantasy|Sci-Fi', 'Family|Sci-Fi', 'Adventure|Drama|Sci-Fi',
                'Horror|Sci-Fi|Thriller', 'Adventure|Sci-Fi',
                
                'Action|Adventure|Sci-Fi|Thriller', 'Action|Crime|Thriller', 'Action|Adventure|Thriller',
                'Action|Crime|Drama|Thriller', 'Action|Crime|Drama|Thriller', 'Action|Thriller', 'Action|Adventure',
                'Action|Sci-Fi|Thriller', 'Action|Adventure|Horror|Sci-Fi|Thriller', 'Action|Sci-Fi',
                
                'Adventure|Comedy|Crime', 'Comedy|Drama|Thriller', 'Comedy|Crime|Drama|Mystery|Thriller', 'Comedy|Drama|War',
                'Comedy|Crime|Drama', 'Comedy|Crime', 'Crime|Drama',
                'Biography|Crime|Drama', 'Comedy|Music|Romance', 'Comedy|War',
                
                'Drama', 'Drama', 'Comedy|Drama|Music|Romance', 'Biography|Crime|Drama|Thriller',
                'Comedy|Drama', 'Biography|Drama|History', 'Biography|Drama|Thriller', 'Comedy|Drama|Romance',
                'Biography|Drama|History', 'Drama|Romance',
                
                'Horror|Mystery|Thriller', 'Drama|Horror|Sci-Fi|Thriller', 'Drama|Horror|Mystery|Thriller', 'Drama|Horror|Mystery|Thriller',
                'Horror|Mystery|Thriller', 'Horror|Mystery|Thriller', 'Crime|Drama|Thriller', 'Crime|Drama|Mystery|Thriller',
                'Drama|Mystery|Thriller', 'Adventure|Drama|Thriller',
                
                'Animation|Adventure|Family|Supernatural', 'Animation|Adventure|Comedy|Family', 'Animation|Adventure|Comedy|Family', 'Animation|Adventure|Family|Sci-Fi',
                'Animation|Adventure|Comedy|Family', 'Animation|Adventure|Comedy|Family', 'Animation|Adventure|Comedy|Family', 'Animation|Adventure|Comedy|Family', 'Animation|Adventure|Comedy|Crime|Family', 'Animation|Adventure|Comedy|Drama|Family',
                
                'Drama', 'Drama|Romance', 'Drama|History|Thriller', 'Action|Crime|Drama',
                'Comedy|Romance', 'Comedy|Drama|Romance|War', 'Drama', 'Action|Drama',
                'Drama|Family', 'Drama'
            ],
            'year': [
                2009, 2019, 1997, 2015, 2018, 2021, 2015, 2019, 2012, 2015,
                1972, 1994, 1993, 1980, 1942, 1939, 1962, 1939, 1950, 1958,
                2019, 2020, 2020, 2020, 2020, 2020, 2021, 2020, 2020, 2020,
                2017, 2021, 2014, 2010, 1999, 1977, 1982, 1977, 1979, 1968,
                2015, 2014, 2018, 2008, 1995, 1988, 1981, 1991, 1986, 2003,
                2014, 2019, 2019, 2019, 2019, 1998, 1994, 1990, 1959, 1964,
                2016, 2016, 2016, 2015, 2014, 2013, 2012, 2011, 2010, 2008,
                2017, 2018, 2018, 2014, 2014, 1960, 1991, 1995, 1999, 1975,
                2001, 1995, 2003, 2008, 2015, 2017, 2016, 2013, 2016, 2009,
                2018, 2012, 2006, 2000, 2001, 1948, 1988, 1954, 1953, 1948
            ],
            'imdb_rating': [
                7.8, 8.4, 7.8, 7.8, 8.4, 8.2, 7.0, 6.8, 8.0, 7.1,
                9.2, 9.3, 8.9, 8.2, 8.5, 8.1, 8.3, 8.0, 8.4, 8.3,
                8.6, 7.3, 7.9, 7.1, 7.8, 7.9, 7.5, 6.7, 8.0, 7.7,
                8.0, 8.0, 8.6, 8.8, 8.7, 8.6, 7.9, 7.7, 8.4, 8.3,
                8.1, 7.4, 7.7, 9.0, 8.2, 8.2, 8.4, 8.5, 8.3, 8.7,
                8.1, 8.6, 7.9, 7.8, 8.4, 8.1, 8.9, 8.7, 8.1, 8.3,
                7.3, 8.1, 8.0, 8.5, 8.4, 8.2, 8.1, 8.0, 7.8, 8.2,
                7.3, 7.9, 7.5, 6.8, 6.8, 8.5, 8.6, 8.6, 8.2, 7.9,
                9.2, 8.2, 8.2, 8.4, 8.2, 7.2, 8.0, 8.6, 8.1, 8.3,
                7.7, 8.1, 8.4, 7.8, 7.9, 8.3, 8.2, 8.6, 8.2, 8.3
            ],
            'director': [
                'James Cameron', 'Anthony Russo', 'James Cameron', 'J.J. Abrams',
                'Anthony Russo', 'Jon Watts', 'Colin Trevorrow', 'Jon Favreau', 'Joss Whedon', 'James Wan',
                'Francis Ford Coppola', 'Frank Darabont', 'Steven Spielberg', 'Martin Scorsese', 'Michael Curtiz', 'Victor Fleming',
                'David Lean', 'Victor Fleming', 'Billy Wilder', 'Alfred Hitchcock',
                'Bong Joon Ho', 'Chloé Zhao', 'Lee Isaac Chung', 'Darius Marder', 'Aaron Sorkin',
                'David Fincher', 'Shaka King', 'Emerald Fennell', 'Pete Docter', 'Thomas Vinterberg',
                'Denis Villeneuve', 'Denis Villeneuve', 'Christopher Nolan', 'Christopher Nolan', 'Lana Wachowski',
                'George Lucas', 'Steven Spielberg', 'Steven Spielberg', 'Ridley Scott', 'Stanley Kubrick',
                'George Miller', 'Chad Stahelski', 'Christopher McQuarrie', 'Christopher Nolan', 'Michael Mann', 
                'John McTiernan', 'Steven Spielberg', 'James Cameron', 'James Cameron', 'Lana Wachowski',
                'Wes Anderson', 'Bong Joon Ho', 'Rian Johnson', 'Taika Waititi', 'Quentin Tarantino',
                'Joel Coen', 'Quentin Tarantino', 'Martin Scorsese', 'Billy Wilder', 'Stanley Kubrick',
                'Kenneth Lonergan', 'Barry Jenkins', 'Damien Chazelle', 'Tom McCarthy', 'Alejandro G. Iñárritu',
                'Steve McQueen', 'Ben Affleck', 'Michel Hazanavicius', 'Tom Hooper', 'Danny Boyle',
                'Jordan Peele', 'John Krasinski', 'Ari Aster', 'Jennifer Kent', 'David Robert Mitchell',
                'Alfred Hitchcock', 'Jonathan Demme', 'David Fincher', 'M. Night Shyamalan', 'Steven Spielberg',
                'Hayao Miyazaki', 'John Lasseter', 'Andrew Stanton', 'Andrew Stanton', 'Pete Docter',
                'Lee Unkrich', 'Ron Clements', 'Chris Buck', 'Byron Howard', 'Pete Docter',
                'Alfonso Cuarón', 'Michael Haneke', 'Florian Henckel von Donnersmarck', 'Fernando Meirelles',
                'Jean-Pierre Jeunet', 'Roberto Benigni', 'Giuseppe Tornatore', 'Akira Kurosawa', 'Yasujirō Ozu', 'Vittorio De Sica'
            ]
        }
        
        # Create ratings data
        np.random.seed(42)
        ratings_data = []
        
        for user_id in range(1, 1001):  # 1000 users
            # Each user rates 10-50 movies
            num_ratings = np.random.randint(10, 51)
            movie_ids = np.random.choice(movies_data['movieId'], num_ratings, replace=False)
            
            for movie_id in movie_ids:
                # Create realistic ratings based on movie quality
                movie_idx = movie_id - 1
                base_rating = movies_data['imdb_rating'][movie_idx] / 2  # Convert from 0-10 to 0-5 scale
                
                # Add some noise
                rating = base_rating + np.random.normal(0, 0.5)
                rating = np.clip(rating, 0.5, 5.0)  # Ensure rating is between 0.5 and 5.0
                rating = round(rating * 2) / 2  # Round to nearest 0.5
                
                ratings_data.append({
                    'userId': user_id,
                    'movieId': movie_id,
                    'rating': rating,
                    'timestamp': int(datetime.now().timestamp())
                })
        
        movies_df = pd.DataFrame(movies_data)
        ratings_df = pd.DataFrame(ratings_data)
        
        self.movies_df = movies_df
        self.ratings_df = ratings_df
        
        print(f"✅ Created enhanced dataset: {len(movies_df)} movies, {len(ratings_df)} ratings")
        return {'movies': movies_df, 'ratings': ratings_df}
    
    def get_data(self) -> Dict[str, pd.DataFrame]:
        """Get the loaded data"""
        if self.movies_df is None:
            self.create_enhanced_sample_data()
        
        return {
            'movies': self.movies_df,
            'ratings': self.ratings_df if self.ratings_df is not None else pd.DataFrame()
        }
