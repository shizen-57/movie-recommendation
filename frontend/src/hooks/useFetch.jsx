import { useEffect, useState } from "react";
import { fetchDataFromApi, getLocalMovies, getTrendingMovies, getPopularMovies, getTopRatedMovies } from "../utils/api";

const useFetch = (url) => {
    //3 states created , initial state of those null
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        setLoading("loading...");//before api call, loading..
        setData(null);
        setError(null);

        // Route to appropriate API based on URL
        const fetchData = async () => {
            try {
                let result;
                
                // Handle detail pages - route to backend API
                if (url.match(/^\/(movie|tv)\/\d+$/)) {
                    // Movie or TV show details: /movie/123 or /tv/456
                    const backendUrl = `/api${url}`;
                    result = await fetchDataFromApi(backendUrl);
                } else if (url.match(/^\/(movie|tv)\/\d+\/(videos|credits|similar|recommendations)$/)) {
                    // Movie or TV show sub-resources: /movie/123/videos, /tv/456/credits, etc.
                    const backendUrl = `/api${url}`;
                    result = await fetchDataFromApi(backendUrl);
                } else if (url.includes('/trending/')) {
                    // Use local trending data
                    const timeWindow = url.includes('/day') ? 'day' : 'week';
                    result = await getTrendingMovies('movie', timeWindow);
                } else if (url.includes('/popular')) {
                    // Use local popular movies
                    result = await getPopularMovies();
                } else if (url.includes('/top_rated')) {
                    // Use local top rated movies
                    result = await getTopRatedMovies();
                } else if (url.includes('/discover')) {
                    // Use local movie data for discover
                    const localData = await getLocalMovies(1, 20);
                    result = {
                        results: localData.movies || [],
                        total_results: localData.total || 0,
                        source: 'local'
                    };
                } else if (url.includes('/genre/')) {
                    // Handle genre requests with static data
                    result = {
                        genres: [
                            { id: 28, name: "Action" },
                            { id: 12, name: "Adventure" },
                            { id: 16, name: "Animation" },
                            { id: 35, name: "Comedy" },
                            { id: 80, name: "Crime" },
                            { id: 99, name: "Documentary" },
                            { id: 18, name: "Drama" },
                            { id: 10751, name: "Family" },
                            { id: 14, name: "Fantasy" },
                            { id: 36, name: "History" },
                            { id: 27, name: "Horror" },
                            { id: 10402, name: "Music" },
                            { id: 9648, name: "Mystery" },
                            { id: 10749, name: "Romance" },
                            { id: 878, name: "Science Fiction" },
                            { id: 10770, name: "TV Movie" },
                            { id: 53, name: "Thriller" },
                            { id: 10752, name: "War" },
                            { id: 37, name: "Western" }
                        ]
                    };
                } else {
                    // Fallback to external TMDB API for specific movie details, etc.
                    result = await fetchDataFromApi(url);
                }
                
                setLoading(false);
                setData(result);
            } catch (err) {
                setLoading(false);
                setError("Something went wrong!");
                console.error("Fetch error:", err);
            }
        };

        fetchData();
    }, [url]);

    return { data, loading, error };
};

export default useFetch;