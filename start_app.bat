@echo off
echo 🎬 Starting Movie Recommender System...
echo.
echo Make sure you have set your Gemini API key:
echo $env:GEMINI_API_KEY="your-api-key-here"
echo.
streamlit run ui/streamlit_app.py
