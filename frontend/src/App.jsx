import React,{ useEffect} from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import {fetchDataFromApi} from "./utils/api";
import { useSelector, useDispatch } from 'react-redux';
import { getApiConfiguration, getGenres } from './store/homeSlice';

import Header from "./components/header/Header";
import Footer from "./components/footer/Footer";
import Home from "./pages/home/Home";
import Details from "./pages/details/Details";
import SearchResult from './pages/searchResult/SearchResult';
import Explore from './pages/explore/Explore';
import AISearch from './pages/aiSearch/AISearch';
import PageNotFound from './pages/404/PageNotFound';

function App() {

  const dispatch = useDispatch();
  
  const {url} = useSelector((state)=>state.home);
  console.log(url);

  useEffect(()=>{
    fetchApiConfig();//invoke method
    genresCall();
  },[])//[]-dependency

const fetchApiConfig = () =>{
  // Use our local backend configuration endpoint instead of external TMDB API
  fetch('http://localhost:5000/api/configuration')
    .then(response => response.json())
    .then((res)=>{
      console.log('Backend configuration:', res);

      const url = {
        backdrop: res.images.secure_base_url + "original",
        poster: res.images.secure_base_url + "w500",  // Use w500 for better performance
        profile: res.images.secure_base_url + "original",
      }

      dispatch(getApiConfiguration(url))
    })
    .catch(error => {
      console.error('Error fetching configuration:', error);
      // Fallback configuration
      const url = {
        backdrop: "https://image.tmdb.org/t/p/original",
        poster: "https://image.tmdb.org/t/p/w500",
        profile: "https://image.tmdb.org/t/p/original",
      }
      dispatch(getApiConfiguration(url))
    });
};

//use promises because 2 request should send to server to get 2 responses at the same time.
const genresCall = async ()=>{
  let promises = [];
  let endPoints = ["tv","movie"];
  let allGenres = {};

  endPoints.forEach((endpoint) =>{
    promises.push(fetchDataFromApi(`/genre/${endpoint}/list`));
  });

  try {
    const data = await Promise.all(promises);
    console.log('Genres data:', data);
    data.map(({genres}) =>{
      return genres.map((item)=>(allGenres[item.id] = item));
    });

    //store genres in redux store
    dispatch(getGenres(allGenres));
  } catch (error) {
    console.error('Error fetching genres:', error);
  }
};


  return (<BrowserRouter>
  <Header/>
  <Routes>
    <Route path='/' element={<Home/>}/>
    <Route path='/:mediaType/:id' element={<Details/>}/>
    <Route path='/search/:query' element={<SearchResult/>}/>
    <Route path='/ai-search/:query' element={<AISearch/>}/>
    <Route path='/ai-search' element={<AISearch/>}/>
    <Route path='/explore/:mediaType' element={<Explore/>}/>
    <Route path='*' element={<PageNotFound/>}/>
  </Routes>
  <Footer/>
  </BrowserRouter>)
}

export default App
