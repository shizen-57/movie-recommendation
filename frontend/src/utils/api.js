import axios from "axios";

// TMDB API configuration
const TMDB_BASE_URL = "https://api.themoviedb.org/3";
const TMDB_TOKEN = import.meta.env.VITE_APP_TMDB_TOKEN;

// Local backend API configuration
const LOCAL_BASE_URL = "http://localhost:5000/api";

const tmdbHeaders = {
    Authorization: "bearer " + TMDB_TOKEN,
};

// API calls - routes to appropriate backend based on URL
export const fetchDataFromApi = async (url, params) => {
    try {
        let apiUrl;
        let headers = {};
        
        // Route to local backend for our API endpoints
        if (url.startsWith('/api/')) {
            apiUrl = `http://localhost:5000${url}`;
        } else {
            // Route to TMDB API for other requests
            apiUrl = TMDB_BASE_URL + url;
            headers = tmdbHeaders;
        }
        
        const { data } = await axios.get(apiUrl, {
            headers,
            params,
        });
        return data;
    } catch (err) {
        console.log("API Error:", err);
        return err;
    }
};

// Local backend API calls (for recommendations and local movie data)
export const fetchFromLocalAPI = async (endpoint, params = {}) => {
    try {
        const { data } = await axios.get(LOCAL_BASE_URL + endpoint, {
            params,
        });
        return data;
    } catch (err) {
        console.log("Local API Error:", err);
        return err;
    }
};

// Movie recommendations from our ML model
export const getMovieRecommendations = async (movieTitle, count = 10) => {
    try {
        const response = await axios.get(`${LOCAL_BASE_URL}/recommendations/${encodeURIComponent(movieTitle)}`, {
            params: { count }
        });
        return response.data;
    } catch (err) {
        console.log("Recommendation API Error:", err);
        return { error: err.message };
    }
};

// AI-powered movie and TV show search
export const searchMoviesWithAI = async (query, useAI = true, mediaType = 'multi') => {
    try {
        const response = await axios.get(`${LOCAL_BASE_URL}/search`, {
            params: { 
                query, 
                ai: useAI.toString(),
                media_type: mediaType  // movie, tv, or multi
            }
        });
        return response.data;
    } catch (err) {
        console.log("AI Search API Error:", err);
        return { error: err.message };
    }
};

// Get local movies with pagination and filtering (now from TMDB API)
export const getLocalMovies = async (page = 1, perPage = 20, search = '', genre = '', category = 'popular') => {
    try {
        const response = await axios.get(`${LOCAL_BASE_URL}/movies`, {
            params: { 
                page, 
                per_page: perPage,
                search,
                genre,
                category  // popular, top_rated, trending
            }
        });
        return response.data;
    } catch (err) {
        console.log("Local Movies API Error:", err);
        return { error: err.message };
    }
};

// Get local TV shows with pagination and filtering (from TMDB API)
export const getLocalTVShows = async (page = 1, perPage = 20, search = '', genre = '', category = 'popular') => {
    try {
        const response = await axios.get(`${LOCAL_BASE_URL}/tv`, {
            params: { 
                page, 
                per_page: perPage,
                search,
                genre,
                category  // popular, top_rated, trending
            }
        });
        return response.data;
    } catch (err) {
        console.log("Local TV Shows API Error:", err);
        return { error: err.message };
    }
};

// Get movie statistics
export const getMovieStats = async () => {
    try {
        const response = await axios.get(`${LOCAL_BASE_URL}/stats`);
        return response.data;
    } catch (err) {
        console.log("Stats API Error:", err);
        return { error: err.message };
    }
};

// Get trending movies (now from TMDB API via local backend)
export const getTrendingMovies = async (mediaType = 'movie', timeWindow = 'week') => {
    try {
        // Use local backend which now calls TMDB API
        const localData = await getLocalMovies(1, 20, '', '', 'trending');
        
        if (localData && localData.movies) {
            return {
                results: localData.movies.map(movie => ({
                    id: movie.id,
                    title: movie.title,
                    overview: movie.overview,
                    poster_path: movie.poster ? movie.poster.replace('https://image.tmdb.org/t/p/w500', '') : null,
                    backdrop_path: movie.backdrop ? movie.backdrop.replace('https://image.tmdb.org/t/p/w1280', '') : null,
                    release_date: movie.release_date || movie.year,
                    vote_average: movie.rating,
                    media_type: 'movie',
                    genre_ids: [],
                    genres: movie.genres || []
                })),
                total_results: localData.total || 0,
                source: 'tmdb_api'
            };
        }
        
        return { error: "No data available" };
    } catch (err) {
        console.log("Trending Movies Error:", err);
        return { error: err.message };
    }
};

// Get popular movies from TMDB API via local backend
export const getPopularMovies = async () => {
    try {
        const localData = await getLocalMovies(1, 20, '', '', 'popular');
        
        if (localData && localData.movies) {
            return {
                results: localData.movies.map(movie => ({
                    id: movie.id,
                    title: movie.title,
                    overview: movie.overview,
                    poster_path: movie.poster ? movie.poster.replace('https://image.tmdb.org/t/p/w500', '') : null,
                    backdrop_path: movie.backdrop ? movie.backdrop.replace('https://image.tmdb.org/t/p/w1280', '') : null,
                    release_date: movie.release_date || movie.year,
                    vote_average: movie.rating,
                    media_type: 'movie',
                    genre_ids: [],
                    genres: movie.genres || []
                })),
                total_results: localData.total || 0,
                source: 'tmdb_api'
            };
        }
        
        return { error: "No data available" };
    } catch (err) {
        console.log("Popular Movies Error:", err);
        return { error: err.message };
    }
};

// Get top rated movies from TMDB API via local backend
export const getTopRatedMovies = async () => {
    try {
        const localData = await getLocalMovies(1, 20, '', '', 'top_rated');
        
        if (localData && localData.movies) {
            return {
                results: localData.movies.map(movie => ({
                    id: movie.id,
                    title: movie.title,
                    overview: movie.overview,
                    poster_path: movie.poster ? movie.poster.replace('https://image.tmdb.org/t/p/w500', '') : null,
                    backdrop_path: movie.backdrop ? movie.backdrop.replace('https://image.tmdb.org/t/p/w1280', '') : null,
                    release_date: movie.release_date || movie.year,
                    vote_average: movie.rating,
                    media_type: 'movie',
                    genre_ids: [],
                    genres: movie.genres || []
                })),
                total_results: localData.total || 0,
                source: 'tmdb_api'
            };
        }
        
        return { error: "No data available" };
    } catch (err) {
        console.log("Top Rated Movies Error:", err);
        return { error: err.message };
    }
};

// Utility function to get image URLs
export const getImageUrl = (imagePath, size = 'original') => {
    if (!imagePath) return null;
    
    // If it's already a full URL, return as is
    if (imagePath.startsWith('http')) return imagePath;
    
    // TMDB image URL construction
    const baseUrl = "https://image.tmdb.org/t/p/";
    return `${baseUrl}${size}${imagePath}`;
};