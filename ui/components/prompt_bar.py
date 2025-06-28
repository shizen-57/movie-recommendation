"""
🎬 CinemaAI Pro - Prompt Bar Component
Modern UI/UX design following black/white theme with Roboto font
"""

import streamlit as st
from typing import Optional, Dict, Any

class PromptBar:
    """
    Prompt bar component implementing the design specifications:
    - Black/white only color scheme
    - Roboto font family
    - Bottom-centered positioning
    - Modern interaction patterns
    """
    
    def __init__(self):
        self.setup_styles()
    
    def setup_styles(self):
        """Apply custom CSS for the prompt bar component"""
        st.markdown("""
        <style>
        /* Import Roboto font */
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
        
        /* Prompt bar container - Instagram style */
        .prompt-bar-container {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(0, 0, 0, 0.95);
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            padding: 12px 16px;
            z-index: 1000;
            box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.3);
        }
        
        .search-container {
            max-width: 600px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        /* Input field styling - Instagram style */
        .stTextInput > div > div > input {
            background-color: rgba(255, 255, 255, 0.1) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 25px !important;
            color: #FFFFFF !important;
            font-family: 'Roboto', sans-serif !important;
            font-size: 16px !important;
            font-weight: 400 !important;
            padding: 12px 16px !important;
            outline: none !important;
            box-shadow: none !important;
            width: 100% !important;
        }
        
        .stTextInput > div > div > input::placeholder {
            color: rgba(255, 255, 255, 0.6) !important;
            font-family: 'Roboto', sans-serif !important;
            font-size: 16px !important;
            font-weight: 400 !important;
        }
        
        .stTextInput > div > div > input:focus {
            border: 1px solid #FFFFFF !important;
            box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.2) !important;
        }
        
        /* Quick action buttons - Instagram style */
        .action-buttons-row {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 8px;
        }
        
        .quick-action-btn {
            background: transparent;
            border: none;
            color: rgba(255, 255, 255, 0.8);
            font-family: 'Roboto', sans-serif;
            font-size: 24px;
            padding: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            border-radius: 50%;
        }
        
        .quick-action-btn:hover {
            color: #FFFFFF;
            background: rgba(255, 255, 255, 0.1);
            transform: scale(1.1);
        }
        
        /* Search button */
        .search-btn {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 50%;
            color: #FFFFFF;
            width: 44px;
            height: 44px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 18px;
        }
        
        .search-btn:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: scale(1.05);
        }
        
        /* Hide Streamlit default elements */
        .stTextInput > label {
            display: none !important;
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .prompt-bar-container {
                padding: 10px 12px;
            }
            
            .search-container {
                gap: 8px;
            }
            
            .quick-action-btn {
                font-size: 20px;
                padding: 6px;
            }
            
            .search-btn {
                width: 40px;
                height: 40px;
                font-size: 16px;
            }
            
            .action-buttons-row {
                gap: 16px;
            }
        }
        </style>
        """, unsafe_allow_html=True)
    
    def render(self) -> Optional[str]:
        """
        Render the Instagram-style prompt bar at bottom
        
        Returns:
            Optional[str]: User input query if provided
        """
        # Create the prompt bar container
        st.markdown('<div class="prompt-bar-container">', unsafe_allow_html=True)
        st.markdown('<div class="search-container">', unsafe_allow_html=True)
        
        # Main search input and button
        col1, col2 = st.columns([6, 1])
        
        with col1:
            query = st.text_input(
                "Search Movies",
                placeholder="Search movies... 🎬",
                label_visibility="hidden",
                key="instagram_movie_search",
                help="Search for movies, actors, genres, or describe your mood"
            )
        
        with col2:
            search_clicked = st.button(
                "🔍",
                help="Search for movies",
                key="search_btn",
                use_container_width=True,
                type="secondary"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close search-container
        
        # Quick action buttons row (Instagram-style bottom navigation)
        st.markdown('<div class="action-buttons-row">', unsafe_allow_html=True)
        
        action_col1, action_col2, action_col3, action_col4, action_col5 = st.columns(5)
        
        actions = {
            "🏠": ("Home", "home"),
            "🔍": ("Explore", "explore"),
            "🎯": ("AI Picks", "ai_picks_btn"), 
            "❤️": ("Favorites", "favorites"),
            "👤": ("Profile", "profile")
        }
        
        action_results = {}
        
        for i, (col, (icon, (label, key))) in enumerate(zip(
            [action_col1, action_col2, action_col3, action_col4, action_col5],
            actions.items()
        )):
            with col:
                if st.button(icon, help=label, key=key, use_container_width=True, type="secondary"):
                    action_results[key] = True
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close action-buttons-row
        st.markdown('</div>', unsafe_allow_html=True)  # Close prompt-bar-container
        
        # Return results
        result = {
            'query': query if query else None,
            'search_clicked': search_clicked,
            'actions': action_results
        }
        
        return result
    
    def render_loading_state(self):
        """Render loading state for the prompt bar"""
        st.markdown("""
        <div class="prompt-bar-container">
            <div style="text-align: center; color: rgba(255,255,255,0.7); font-family: 'Roboto', sans-serif;">
                🔍 Searching for movies...
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_results_preview(self, results_count: int):
        """Show quick results preview above prompt bar"""
        if results_count > 0:
            st.markdown(f"""
            <div style="
                position: fixed;
                bottom: 120px;
                left: 50%;
                transform: translateX(-50%);
                background: rgba(0, 0, 0, 0.8);
                color: #FFFFFF;
                padding: 8px 16px;
                border-radius: 20px;
                font-family: 'Roboto', sans-serif;
                font-size: 14px;
                z-index: 999;
            ">
                Found {results_count} movies ✨
            </div>
            """, unsafe_allow_html=True)
