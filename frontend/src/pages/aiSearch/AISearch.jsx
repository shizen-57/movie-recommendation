import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useSelector } from "react-redux";
import InfiniteScroll from "react-infinite-scroll-component";
import dayjs from "dayjs";

import "./style.scss";

import { searchMoviesWithAI } from "../../utils/api";
import ContentWrapper from "../../components/contentWrapper/ContentWrapper";
import Spinner from "../../components/spinner/Spinner";
import Img from "../../components/lazyLoadImage/Img";
import noResults from "../../assets/no-results.png";
import PosterFallback from "../../assets/no-poster.png";

const AISearch = () => {
    const [data, setData] = useState(null);
    const [pageNum, setPageNum] = useState(1);
    const [loading, setLoading] = useState(false);
    const [query, setQuery] = useState("");
    const [aiResponse, setAiResponse] = useState("");
    const { query: urlParam } = useParams();
    const navigate = useNavigate();
    const { url } = useSelector((state) => state.home);

    // Custom movie card component for AI search with vertical layout
    const AIMovieCard = ({ data }) => {
        const posterUrl = data.poster_path
            ? `https://image.tmdb.org/t/p/w500${data.poster_path}`
            : PosterFallback;

        return (
            <div 
                className="movieCard"
                onClick={() => navigate(`/movie/${data.id}`)}
            >
                <div className="posterBlock">
                    <Img className="posterImg" src={posterUrl} />
                </div>
                <div className="textBlock">
                    <div className="title">{data.title || data.name}</div>
                    <div className="date">
                        {data.release_date ? dayjs(data.release_date).format("MMM D, YYYY") : "Release date unknown"}
                    </div>
                    {data.overview && (
                        <div className="overview">{data.overview}</div>
                    )}
                    {data.vote_average > 0 && (
                        <div className="rating">
                            ⭐ {data.vote_average.toFixed(1)}/10 ({data.vote_count || 0} votes)
                        </div>
                    )}
                    {data.genres && data.genres.length > 0 && (
                        <div className="genres">
                            {data.genres.slice(0, 3).map((genre, index) => (
                                <span key={index} className="genre">{genre}</span>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        );
    };

    const fetchInitialData = (searchQuery) => {
        setLoading(true);
        searchMoviesWithAI(searchQuery, true).then((res) => {
            setData(res);
            setAiResponse(res.ai_response || "");
            setPageNum(1);
            setLoading(false);
        });
    };

    const fetchNextPageData = () => {
        // For AI search, we typically return all results at once
        // This could be enhanced to support pagination if needed
    };

    useEffect(() => {
        setPageNum(1);
        fetchInitialData(urlParam);
        setQuery(urlParam);
    }, [urlParam]);

    const handleSearch = (e) => {
        e.preventDefault();
        if (query.trim()) {
            fetchInitialData(query);
        }
    };

    return (
        <div className="aiSearchResultsPage">
            <ContentWrapper>
                <div className="pageHeader">
                    <div className="pageTitle">
                        🤖 AI-Powered Movie Search
                    </div>
                    <form onSubmit={handleSearch} className="searchForm">
                        <input
                            type="text"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            placeholder="Describe what you're looking for... (e.g., 'sci-fi movies like Blade Runner')"
                            className="searchInput"
                        />
                        <button type="submit" className="searchButton">
                            Search with AI
                        </button>
                    </form>
                </div>

                {aiResponse && (
                    <div className="aiResponseSection">
                        <h3>🤖 AI Analysis:</h3>
                        <div className="aiResponseContent">
                            {aiResponse.split('\n').map((line, index) => {
                                // Check if line contains numbered recommendations
                                if (line.match(/^\d+\./)) {
                                    return (
                                        <div key={index} className="recommendation-item">
                                            <strong>{line}</strong>
                                        </div>
                                    );
                                }
                                // Check if line is a section header (RECOMMENDATIONS:, ANALYSIS:)
                                else if (line.includes('RECOMMENDATIONS:') || line.includes('ANALYSIS:')) {
                                    return (
                                        <div key={index} className="section-header">
                                            {line}
                                        </div>
                                    );
                                }
                                // Regular lines
                                else if (line.trim()) {
                                    return (
                                        <div key={index} className="analysis-line">
                                            {line}
                                        </div>
                                    );
                                }
                                // Empty lines for spacing
                                else {
                                    return <br key={index} />;
                                }
                            })}
                        </div>
                    </div>
                )}

                {loading && <Spinner initial={true} />}

                {!loading && (
                    <React.Fragment>
                        {data?.results?.length > 0 ? (
                            <React.Fragment>
                                <div className="resultsCount">
                                    {`Found ${data.results.length} movies`}
                                    {data.total_analyzed && (
                                        <span className="analyzed">
                                            {` (analyzed ${data.total_analyzed} movies total)`}
                                        </span>
                                    )}
                                </div>
                                <InfiniteScroll
                                    className="content"
                                    dataLength={data?.results?.length || []}
                                    next={fetchNextPageData}
                                    hasMore={false} // AI search returns all results at once
                                    loader={<Spinner />}
                                >
                                    {data?.results?.map((item, index) => {
                                        return (
                                            <AIMovieCard
                                                key={index}
                                                data={item}
                                            />
                                        );
                                    })}
                                </InfiniteScroll>
                            </React.Fragment>
                        ) : (
                            <div className="resultNotFound">
                                <img src={noResults} alt="No results" />
                                <span className="resultNotFoundText">
                                    No movies found for your search
                                </span>
                                <p className="aiSearchHint">
                                    Try describing what you're looking for in more detail, like:
                                    <br />
                                    • "Action movies with robots"
                                    <br />
                                    • "Romantic comedies from the 90s"
                                    <br />
                                    • "Horror movies like The Exorcist"
                                </p>
                            </div>
                        )}
                    </React.Fragment>
                )}
            </ContentWrapper>
        </div>
    );
};

export default AISearch;
