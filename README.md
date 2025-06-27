# 🎬 CinemaAI Pro - Advanced Movie Recommendation System

A cutting-edge movie recommendation system powered by Machine Learning and Google's Gemini AI, featuring a beautiful dark-themed UI with Pinterest-style masonry grid layout.

![CinemaAI Pro](https://img.shields.io/badge/CinemaAI-Pro-blue?style=for-the-badge&logo=movie)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Gemini AI](https://img.shields.io/badge/Gemini-AI-4285F4?style=for-the-badge&logo=google&logoColor=white)

## ✨ Features

### 🤖 AI-Powered Recommendations
- **Gemini AI Integration**: Natural language movie search and intelligent recommendations
- **Smart Content Filtering**: Advanced algorithms analyze movie preferences and viewing patterns
- **Personalized Suggestions**: AI learns from your favorites to provide tailored recommendations
- **Contextual Understanding**: Describe what you want in plain English

### 🎨 Modern UI/UX
- **Pinterest-Style Layout**: Beautiful masonry grid displaying movie posters
- **Pure Black Theme**: Elegant dark theme optimized for movie browsing
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Interactive Elements**: Hover effects, smooth transitions, and intuitive navigation

### 📊 Advanced Analytics
- **Movie Statistics**: Comprehensive database insights and trending analysis
- **Rating Systems**: Multiple rating sources (IMDb, user ratings, popularity scores)
- **Genre Analytics**: Detailed breakdowns by genre, year, and rating
- **Real-time Processing**: Pandas and NumPy for fast data processing

### 🔍 Smart Search & Discovery
- **Natural Language Search**: "Find me sci-fi movies like Blade Runner"
- **Multi-filter System**: Genre, year, rating, and custom filters
- **AI-Enhanced Results**: Gemini AI provides context and explanations
- **Instant Results**: Fast search with intelligent ranking

## 🚀 Quick Start

### Option 1: Easy Launch (Recommended)
```bash
# Clone the repository
git clone https://github.com/yourusername/CinemaAI-Pro.git
cd CinemaAI-Pro

# Run the startup script
./start_app.bat  # Windows
# or
python -m streamlit run ui/streamlit_app.py
```

### Option 2: Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set your Gemini API key (optional but recommended)
export GEMINI_API_KEY="your-api-key-here"

# Run the application
streamlit run ui/streamlit_app.py
```

## 🔧 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Google Gemini API key (optional, for AI features)

### Dependencies
```bash
# Core libraries
streamlit>=1.28.0
pandas>=1.5.0
numpy>=1.24.0
scikit-learn>=1.3.0

# AI integration
google-generativeai>=0.3.0

# Data processing
requests>=2.31.0
Pillow>=10.0.0

# Visualization
plotly>=5.15.0
matplotlib>=3.7.0
seaborn>=0.12.0
```

### Get Gemini API Key (Optional)
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Set it as environment variable: `GEMINI_API_KEY=your-key-here`

## 📁 Project Structure

```
CinemaAI-Pro/
├── ui/
│   └── streamlit_app.py          # Main UI application
├── src/
│   ├── data_loader.py            # Enhanced data loading and processing
│   ├── recommender.py            # Core recommendation algorithms
│   └── ai/
│       └── gemini.py             # Gemini AI integration
├── data/
│   ├── tmdb_5000_movies.csv      # Movie dataset (optional)
│   └── sample_data/              # Sample movie data
├── artifacts/
│   ├── movies_full.pkl           # Processed movie data
│   └── vectorizer.pkl            # ML model artifacts
├── demo/                         # Screenshots and demos
├── requirements.txt              # Python dependencies
├── start_app.bat                 # Quick startup script
├── AI_FEATURES_GUIDE.md          # Detailed AI features guide
└── README.md                     # This file
```

## 🎯 Key Features Showcase

### 1. AI-Powered Natural Language Search
```python
# Example searches that work:
"Movies like Inception with complex time travel plots"
"Feel-good comedies that will make me laugh out loud"  
"Dark psychological thrillers with unreliable narrators"
"Romantic movies that aren't too cheesy"
```

### 2. Pinterest-Style Movie Grid
- Masonry layout with dynamic heights
- Hover effects revealing movie details
- Responsive design (5 columns → 2 columns on mobile)
- Smooth animations and transitions

### 3. Advanced Filtering System
- **Genre-based filtering**: Action, Comedy, Drama, Horror, Romance, Sci-Fi, Thriller
- **Year range selection**: 1980-2024 with slider interface
- **Rating filters**: Minimum rating threshold
- **AI-enhanced results**: Context-aware recommendations

### 4. Movie Analytics Dashboard
- **Database Statistics**: Total movies, average ratings, latest releases
- **Trending Analysis**: Popular movies based on multiple factors
- **Genre Insights**: Distribution and performance by genre
- **Rating Correlations**: User vs. IMDb vs. popularity scores

## 🤖 AI Features Deep Dive

### Gemini AI Integration
The system uses Google's Gemini AI for:
- **Natural Language Understanding**: Converts user descriptions to movie preferences
- **Contextual Recommendations**: Provides explanations for why movies are recommended
- **Smart Filtering**: Understands nuanced requests like "not too cheesy romantic movies"
- **Movie Analysis**: Detailed breakdowns of individual movies

### Machine Learning Pipeline
1. **Data Processing**: Pandas/NumPy for efficient data manipulation
2. **Feature Engineering**: Genre analysis, rating normalization, popularity scoring
3. **Similarity Calculation**: Content-based filtering with multiple metrics
4. **AI Enhancement**: Gemini AI adds contextual understanding

## 🎨 UI/UX Design Philosophy

### Dark Theme Excellence
- **Pure Black Background**: Reduces eye strain during extended browsing
- **High Contrast Text**: Ensures readability and accessibility
- **Subtle Animations**: Enhances user experience without distraction
- **Pinterest Inspiration**: Grid layout optimized for visual content

### Responsive Design
- **Desktop**: 5-column masonry grid with detailed hover effects
- **Tablet**: 3-4 column layout with touch-friendly interactions
- **Mobile**: 2-column layout optimized for thumb navigation

## 📊 Performance & Scalability

### Optimizations
- **Streamlit Caching**: `@st.cache_resource` for model loading
- **Efficient Data Structures**: Pandas DataFrames with optimized indexing
- **Lazy Loading**: Movies load progressively as needed
- **API Rate Limiting**: Intelligent Gemini API usage

### Data Sources
- **TMDB Dataset**: 5000+ movies with rich metadata
- **Enhanced Sample Data**: 30+ carefully curated movies for demo
- **Synthetic Ratings**: Generated user preferences for cold-start scenarios
- **Real-time Processing**: Dynamic filtering and sorting

## 🛠️ Development & Customization

### Adding New Features
1. **Custom Filters**: Extend the sidebar filtering system
2. **New AI Prompts**: Customize Gemini AI interactions
3. **UI Themes**: Modify CSS for different color schemes
4. **Data Sources**: Add new movie databases or APIs

### Configuration Options
```python
# Environment variables
GEMINI_API_KEY=your-gemini-api-key
TMDB_API_KEY=your-tmdb-api-key  # Future enhancement
DEBUG_MODE=false
CACHE_TIMEOUT=3600
```

## 🚀 Deployment Options

### Local Development
```bash
streamlit run ui/streamlit_app.py --server.port 8501
```

### Streamlit Cloud
1. Push to GitHub
2. Connect to [Streamlit Cloud](https://streamlit.io/cloud)
3. Deploy with one click

### Docker (Future)
```dockerfile
# Dockerfile example for containerized deployment
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "ui/streamlit_app.py"]
```

## 📈 Future Roadmap

### Planned Features
- [ ] **User Accounts**: Personal movie lists and viewing history
- [ ] **Social Features**: Share recommendations and reviews
- [ ] **Advanced ML Models**: Deep learning recommendations
- [ ] **Real-time Data**: Live movie updates and trending analysis
- [ ] **Mobile App**: React Native or Flutter companion app
- [ ] **API Endpoints**: RESTful API for third-party integrations

### Technical Improvements
- [ ] **Database Integration**: PostgreSQL or MongoDB for persistence
- [ ] **Caching Layer**: Redis for improved performance
- [ ] **Microservices**: Separate AI, recommendation, and UI services
- [ ] **Testing Suite**: Comprehensive unit and integration tests
- [ ] **CI/CD Pipeline**: Automated testing and deployment

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Development Setup
```bash
# Clone and setup
git clone https://github.com/yourusername/CinemaAI-Pro.git
cd CinemaAI-Pro

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install development dependencies
pip install -r requirements.txt
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini AI**: For providing advanced AI capabilities
- **TMDB**: For comprehensive movie database
- **Streamlit**: For the excellent web app framework
- **scikit-learn**: For machine learning tools
- **pandas & NumPy**: For data processing capabilities

## 📞 Support & Contact

- **GitHub Issues**: [Report bugs or request features](https://github.com/yourusername/CinemaAI-Pro/issues)
- **Discussions**: [Community discussions and Q&A](https://github.com/yourusername/CinemaAI-Pro/discussions)

---

⭐ **Star this repository if you found it helpful!** ⭐

Made with ❤️ and powered by 🤖 Gemini AI
