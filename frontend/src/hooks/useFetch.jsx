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
                
                if (url.includes('/trending/')) {
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