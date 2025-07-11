import React ,{useState, useEffect} from 'react';
import "./style.scss"
import { useParams } from 'react-router-dom';
import InfiniteScroll from 'react-infinite-scroll-component';
import { searchMoviesWithAI } from './../../utils/api';
import ContentWrapper from './../../components/contentWrapper/ContentWrapper';
import noResults from "../../assets/no-results.png"
import Spinner from '../../components/spinner/Spinner';
import MovieCard from '../../components/movieCard/MovieCard';

const SearchResult = () => {
  //creating states
  const [data, setData] = useState(null);
  const [pageNum, setPageNum] = useState(1);
  const [loading, setLoading] = useState(false);
  const {query} = useParams();

  const fetchInitialData = () =>{
    	setLoading(true);
      // Use multi-search to include both movies and TV shows
      searchMoviesWithAI(query, false, 'multi').then((res)=>{
        setData(res)
        setPageNum((prev)=>prev+1)
        setLoading(false)
      }).catch((err) => {
        console.error('Search error:', err);
        setLoading(false);
      });
  }

  const fetchNextPageData = () =>{
    // For now, disable pagination as our backend returns all results at once
    // This could be enhanced later to support pagination
    return;
  }

  useEffect(()=>{
      fetchInitialData();
  },[query])

  return (
    <div className='searchResultsPage'>
      {loading && <Spinner initial={true}/>}
      {!loading && (<ContentWrapper>
        {data?.results?.length > 0 ?(<>
        <div className="pageTitle">{`Search ${data?.total_results > 1 ? "results" : "result"} of '${query}'`}</div>
        <InfiniteScroll 
          className='content' 
          dataLength={data?.results?.length || []}
          next={fetchNextPageData}
          hasMore={false} // Disable pagination for now
          loader={<Spinner/>}
        >
          {data?.results.map((item,index)=>{
            if(item.media_type === 'person') return;
            return (
              <MovieCard 
              key={index} 
              data={item} 
              fromSearch={true} 
              />
            )
          })}
        </InfiniteScroll>
        </>):(
          <span className="resultNotFound">Sorry, Results not found</span>
        )}
      </ContentWrapper>)}
    </div>
  )
}

export default SearchResult