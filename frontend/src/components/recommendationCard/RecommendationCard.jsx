import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useSelector } from "react-redux";
import dayjs from "dayjs";

import "./style.scss";
import Img from "../lazyLoadImage/Img";
import CircleRating from "../circleRating/CircleRating";
import Genres from "../genres/Genres";
import PosterFallback from "../../assets/no-poster.png";
import { getMovieRecommendations } from "../../utils/api";

const RecommendationCard = ({ data, fromSearch, mediaType }) => {
    const { url } = useSelector((state) => state.home);
    const navigate = useNavigate();
    const [recommendations, setRecommendations] = useState([]);
    const [showRecommendations, setShowRecommendations] = useState(false);
    const [loading, setLoading] = useState(false);

    const posterUrl = data.poster_path
        ? url.poster + data.poster_path
        : PosterFallback;

    const handleGetRecommendations = async (e) => {
        e.stopPropagation();
        setLoading(true);
        
        try {
            const result = await getMovieRecommendations(data.title || data.name, 6);
            if (result.error) {
                console.error("Recommendation error:", result.error);
            } else {
                setRecommendations(result.recommendations || []);
                setShowRecommendations(true);
            }
        } catch (error) {
            console.error("Error fetching recommendations:", error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="recommendationCard">
            <div className="movieCard" onClick={() => navigate(`/${data.media_type || mediaType}/${data.id}`)}>
                <div className="posterBlock">
                    <Img className="posterImg" src={posterUrl} />
                    {!fromSearch && (
                        <React.Fragment>
                            <CircleRating rating={data.vote_average.toFixed(1)} />
                            <Genres data={data.genre_ids?.slice(0, 2)} />
                        </React.Fragment>
                    )}
                </div>
                <div className="textBlock">
                    <span className="title">{data.title || data.name}</span>
                    <span className="date">
                        {dayjs(data.release_date || data.first_air_date).format("MMM D, YYYY")}
                    </span>
                </div>
            </div>
            
            <div className="recommendationActions">
                <button 
                    className="recommendBtn"
                    onClick={handleGetRecommendations}
                    disabled={loading}
                >
                    {loading ? "Getting Recommendations..." : "🤖 AI Recommendations"}
                </button>
            </div>

            {showRecommendations && recommendations.length > 0 && (
                <div className="recommendationsList">
                    <h4>Recommended for you:</h4>
                    <div className="recommendationsGrid">
                        {recommendations.map((rec, index) => (
                            <div key={index} className="miniCard" onClick={() => navigate(`/movie/${rec.id}`)}>
                                <div className="miniPoster">
                                    <Img 
                                        src={rec.poster || PosterFallback} 
                                        className="miniPosterImg"
                                    />
                                </div>
                                <div className="miniInfo">
                                    <span className="miniTitle">{rec.title}</span>
                                    <span className="miniRating">⭐ {rec.rating || 'N/A'}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default RecommendationCard;
