import React, { useState, useEffect } from "react";
import { HiOutlineSearch } from "react-icons/hi";
import { SlMenu } from "react-icons/sl";
import { VscChromeClose } from "react-icons/vsc";
import { AiOutlineRobot } from "react-icons/ai";
import { MdMic, MdMicOff } from "react-icons/md";
import { useNavigate, useLocation } from "react-router-dom";

import "./style.scss";

import ContentWrapper from "../contentWrapper/ContentWrapper";
import logo from "../../assets/cinemx.png";

const Header = () => {
  //states creating
    const [show, setShow] = useState("top");
    const [lastScrollY, setLastScrollY] = useState(0);
    const [mobileMenu, setMobileMenu] = useState(false);
    const [query, setQuery] = useState("");
    const [showSearch, setShowSearch] = useState("");
    const [searchMode, setSearchMode] = useState("normal"); // "normal" or "ai"
    const [isListening, setIsListening] = useState(false);
    const [recognition, setRecognition] = useState(null);
    const navigate = useNavigate();
    const location = useLocation();

    //all new pages start showing top
    useEffect(()=>{
      window.scrollTo(0,0);
    },[location])

    const controlNavBar = () =>{
        if(window.scrollY > 200){
          if(window.scrollY > lastScrollY && !mobileMenu){
            setShow("hide")
          }else{
            setShow("show")
          }
          setLastScrollY(window.scrollY);
        }else{
          setShow("top");
        }
    }

    useEffect(()=>{
      window.addEventListener("scroll",controlNavBar)
      return ()=>{
        window.removeEventListener("scroll",controlNavBar)
      }
    },[lastScrollY])

    const openSearch = () =>{
      setMobileMenu(false);
      setShowSearch(true)
    }

    const openMobileMenu = () =>{
      setMobileMenu(true);
      setShowSearch(false)
    }

    const searchQueryHandler = (event)=>{
      //if user type search query and press enter, and search query not empty, then api call
      if(event.key === 'Enter' && query.length >0 ){
          if(searchMode === "ai") {
            navigate(`/ai-search/${query}`);
          } else {
            navigate(`/search/${query}`);
          }

          setTimeout(()=>{
            setShowSearch(false)
          },1000)
      }
    }

    const toggleSearchMode = () => {
      setSearchMode(searchMode === "normal" ? "ai" : "normal");
    }

    const navigationHandler = (type) =>{
      if(type === "movie"){
        navigate('/explore/movie')
      }else{
        navigate('/explore/tv')
      }
      setMobileMenu(false);
    }

    // Initialize Speech Recognition
    useEffect(() => {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            try {
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                const recognitionInstance = new SpeechRecognition();
                
                recognitionInstance.continuous = false;
                recognitionInstance.interimResults = false;
                recognitionInstance.lang = 'en-US';
                recognitionInstance.maxAlternatives = 1;
                
                recognitionInstance.onstart = () => {
                    console.log('🎤 Voice recognition started');
                    setIsListening(true);
                };
                
                recognitionInstance.onresult = (event) => {
                    try {
                        const transcript = event.results[0][0].transcript;
                        console.log('🎤 Voice recognized:', transcript);
                        setQuery(transcript);
                        setIsListening(false);
                        
                        // Automatically trigger search after voice recognition
                        setTimeout(() => {
                            if (transcript.trim()) {
                                if (searchMode === "ai") {
                                    navigate(`/ai-search/${transcript}`);
                                } else {
                                    navigate(`/search/${transcript}`);
                                }
                                setShowSearch(false);
                            }
                        }, 100);
                    } catch (error) {
                        console.error('Error processing speech result:', error);
                        setIsListening(false);
                    }
                };
                
                recognitionInstance.onerror = (event) => {
                    console.error('Speech recognition error:', event.error);
                    setIsListening(false);
                    
                    // Show user-friendly error messages
                    switch (event.error) {
                        case 'no-speech':
                            alert('No speech detected. Please try again.');
                            break;
                        case 'audio-capture':
                            alert('No microphone found. Please check your microphone.');
                            break;
                        case 'not-allowed':
                            alert('Microphone access denied. Please allow microphone access.');
                            break;
                        default:
                            alert(`Voice recognition error: ${event.error}`);
                    }
                };
                
                recognitionInstance.onend = () => {
                    console.log('🎤 Voice recognition ended');
                    setIsListening(false);
                };
                
                setRecognition(recognitionInstance);
                console.log('✅ Speech recognition initialized successfully');
            } catch (error) {
                console.error('Failed to initialize speech recognition:', error);
            }
        } else {
            console.warn('Speech recognition not supported in this browser');
        }
    }, []);

    // Test voice search support
    const testVoiceSupport = () => {
        console.log('🧪 Testing voice search support...');
        console.log('webkitSpeechRecognition available:', 'webkitSpeechRecognition' in window);
        console.log('SpeechRecognition available:', 'SpeechRecognition' in window);
        console.log('Recognition instance:', recognition);
        console.log('Is listening:', isListening);
        
        if (recognition) {
            console.log('✅ Voice search is ready');
        } else {
            console.log('❌ Voice search not available');
        }
    };

    const startVoiceSearch = () => {
        console.log('🎤 Voice search button clicked');
        console.log('🎤 Current recognition state:', recognition);
        console.log('🎤 Current isListening state:', isListening);
        testVoiceSupport();
        
        if (recognition) {
            try {
                console.log('🎤 Starting voice search...');
                setIsListening(true);
                recognition.start();
            } catch (error) {
                console.error('Error starting voice recognition:', error);
                setIsListening(false);
                alert('Failed to start voice recognition. Please try again.');
            }
        } else {
            console.error('❌ Voice search not available - recognition instance is null');
            alert('Voice search is not supported in your browser. Please use Chrome, Edge, or Safari.');
        }
    };

    const stopVoiceSearch = () => {
        if (recognition && isListening) {
            try {
                console.log('🎤 Stopping voice search...');
                recognition.stop();
                setIsListening(false);
            } catch (error) {
                console.error('Error stopping voice recognition:', error);
                setIsListening(false);
            }
        }
    };

    return (
        <header className={`header ${mobileMenu ? "mobileView" : ""} ${show}`}>
          <ContentWrapper>
            <div className="logo" onClick={()=> navigate("/")}>
              <img src={logo} alt="" />
            </div>
            <ul className="menuItems">
              <li className="menuItem" onClick={()=>{navigationHandler("movie")}}>Movies</li>
              <li className="menuItem" onClick={()=>{navigationHandler("tv")}}>TV Shows</li>
              <li className="menuItem" onClick={()=> navigate('/ai-search')}>
                <AiOutlineRobot />
                <span>AI Search</span>
              </li>
              <li className="menuItem">
                <HiOutlineSearch onClick={openSearch}/>
              </li>
            </ul>

            <div className="mobileMenuItems">
            <HiOutlineSearch onClick={openSearch}/>
            {mobileMenu ? (<VscChromeClose onClick={()=>{setMobileMenu(false)}}/>) : (<SlMenu onClick={openMobileMenu}/>)} 
            </div>
          </ContentWrapper>
         { showSearch && <div className="searchBar">
            <ContentWrapper>
            <div className="searchInput">
              <div className="searchModeToggle">
                <button 
                  className={`modeBtn ${searchMode === "normal" ? "active" : ""}`}
                  onClick={() => setSearchMode("normal")}
                >
                  Normal
                </button>
                <button 
                  className={`modeBtn ${searchMode === "ai" ? "active" : ""}`}
                  onClick={() => setSearchMode("ai")}
                >
                  🤖 AI
                </button>
              </div>
              <div className="inputWrapper">
                <input 
                  type="text" 
                  value={query}
                  placeholder={searchMode === "ai" ? 
                    'Describe what you\'re looking for... (e.g., "sci-fi movies like Blade Runner")' : 
                    'Search for movie or TV show..'
                  } 
                  onChange={(e)=> setQuery(e.target.value)} 
                  onKeyUp={searchQueryHandler}
                />
                <button 
                  className={`voiceSearchBtn ${isListening ? 'listening' : ''}`}
                  onClick={isListening ? stopVoiceSearch : startVoiceSearch}
                  title={isListening ? 'Stop voice search' : 'Start voice search'}
                  style={{ 
                    pointerEvents: 'auto',
                    display: 'flex',
                    opacity: 1,
                    visibility: 'visible'
                  }}
                >
                  {isListening ? <MdMicOff /> : <MdMic />}
                </button>
              </div>
              <VscChromeClose onClick={()=>{setShowSearch(false)}}/>
            </div>
            </ContentWrapper>
          </div>}
        </header>
    );
};

export default Header;