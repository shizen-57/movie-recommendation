import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import InfiniteScroll from "react-infinite-scroll-component";
import Select from "react-select";

import "./style.scss";

import useFetch from "../../hooks/useFetch";
import { getLocalMovies, getLocalTVShows } from "../../utils/api";
import ContentWrapper from "../../components/contentWrapper/ContentWrapper";
import MovieCard from "../../components/movieCard/MovieCard";
import Spinner from "../../components/spinner/Spinner";

let filters = {};

//create sort by properties and values
const sortbyData = [
    { value: "popularity.desc", label: "Popularity Descending" },
    { value: "popularity.asc", label: "Popularity Ascending" },
    { value: "vote_average.desc", label: "Rating Descending" },
    { value: "vote_average.asc", label: "Rating Ascending" },
    {
        value: "primary_release_date.desc",
        label: "Release Date Descending",
    },
    { value: "primary_release_date.asc", label: "Release Date Ascending" },
    { value: "original_title.asc", label: "Title (A-Z)" },
];

const Explore = () => {

  //create states
    const [data, setData] = useState(null);
    const [pageNum, setPageNum] = useState(1);
    const [loading, setLoading] = useState(false);
    const [genre, setGenre] = useState(null);
    const [sortby, setSortby] = useState(null);
    const { mediaType } = useParams();

    //api call
    const { data: genresData } = useFetch(`/genre/${mediaType}/list`);

    const fetchInitialData = () => {
        setLoading(true);
        
        const category = 'popular';
        
        if (mediaType === 'tv') {
            // Use TV shows API
            getLocalTVShows(1, 20, '', '', category).then((res) => {
                if (res && res.tv_shows) {
                    const formattedData = {
                        results: res.tv_shows.map(tvShow => ({
                            id: tvShow.id,
                            title: tvShow.title,
                            overview: tvShow.overview,
                            poster_path: tvShow.poster_path,
                            backdrop_path: tvShow.backdrop_path,
                            release_date: tvShow.release_date || tvShow.year,
                            vote_average: tvShow.rating,
                            media_type: mediaType,
                            genre_ids: [],
                            genres: tvShow.genres || []
                        })),
                        total_results: res.total || 0,
                        total_pages: Math.ceil((res.total || 0) / 20)
                    };
                    setData(formattedData);
                    setPageNum((prev) => prev + 1);
                } else {
                    setData({
                        results: [],
                        total_results: 0,
                        total_pages: 0
                    });
                }
                setLoading(false);
            }).catch((err) => {
                console.error('Explore TV fetch error:', err);
                setData({
                    results: [],
                    total_results: 0,
                    total_pages: 0
                });
                setLoading(false);
            });
        } else {
            // Use movies API
            getLocalMovies(1, 20, '', '', category).then((res) => {
                if (res && res.movies) {
                    const formattedData = {
                        results: res.movies.map(movie => ({
                            id: movie.id,
                            title: movie.title,
                            overview: movie.overview,
                            poster_path: movie.poster_path,
                            backdrop_path: movie.backdrop_path,
                            release_date: movie.release_date || movie.year,
                            vote_average: movie.rating,
                            media_type: mediaType,
                            genre_ids: [],
                            genres: movie.genres || []
                        })),
                        total_results: res.total || 0,
                        total_pages: Math.ceil((res.total || 0) / 20)
                    };
                    setData(formattedData);
                    setPageNum((prev) => prev + 1);
                } else {
                    setData({
                        results: [],
                        total_results: 0,
                        total_pages: 0
                    });
                }
                setLoading(false);
            }).catch((err) => {
                console.error('Explore movies fetch error:', err);
                setData({
                    results: [],
                    total_results: 0,
                    total_pages: 0
                });
                setLoading(false);
            });
        }
    };

    const fetchNextPageData = () => {
        // For now, disable pagination as our backend returns all results at once
        // This could be enhanced later to support pagination
        return;
    };

    useEffect(() => {
        filters = {};
        setData(null);
        setPageNum(1);
        setSortby(null);
        setGenre(null);
        fetchInitialData();
    }, [mediaType]);

    //after selecting sort by option, this method call
    const onChange = (selectedItems, action) => {
        if (action.name === "sortby") {
            setSortby(selectedItems);
            // For now, sorting will be handled on the frontend
            // TODO: Implement backend sorting
        }

        if (action.name === "genres") {
            setGenre(selectedItems);
            // For now, genre filtering will be handled on the frontend
            // TODO: Implement backend genre filtering
        }

        // Re-fetch data when filters change
        setPageNum(1);
        fetchInitialData();
    };

    return (
        <div className="explorePage">
            <ContentWrapper>
                <div className="pageHeader">
                    <div className="pageTitle">
                        {mediaType === "tv"
                            ? "Explore TV Shows"
                            : "Explore Movies"}
                    </div>
                    <div className="filters">
                        <Select
                            isMulti
                            name="genres"
                            value={genre}
                            closeMenuOnSelect={false}
                            options={genresData?.genres}
                            getOptionLabel={(option) => option.name}
                            getOptionValue={(option) => option.id}
                            onChange={onChange}
                            placeholder="Select genres"
                            className="react-select-container genresDD"
                            classNamePrefix="react-select"
                        />
                        <Select
                            name="sortby"
                            value={sortby}
                            options={sortbyData}
                            onChange={onChange}
                            isClearable={true}
                            placeholder="Sort by"
                            className="react-select-container sortbyDD"
                            classNamePrefix="react-select"
                        />
                    </div>
                </div>
                {loading && <Spinner initial={true} />}
                {!loading && (
                    <>
                        {data?.results?.length > 0 ? (
                            <InfiniteScroll
                                className="content"
                                dataLength={data?.results?.length || []}
                                next={fetchNextPageData}
                                hasMore={false} // Disable pagination for now
                                loader={<Spinner />}
                            >
                                {data?.results?.map((item, index) => {
                                    if (item.media_type === "person") return;
                                    return (
                                        <MovieCard
                                            key={index}
                                            data={item}
                                            mediaType={mediaType}
                                        />
                                    );
                                })}
                            </InfiniteScroll>
                        ) : (
                            <span className="resultNotFound">
                                Sorry, Results not found!
                            </span>
                        )}
                    </>
                )}
            </ContentWrapper>
        </div>
    );
};

export default Explore;