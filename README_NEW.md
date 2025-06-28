# 🎬 CinemaAI Pro - AI-Powered Movie Recommendation System

A sophisticated movie recommendation system powered by artificial intelligence, featuring live TMDB API integration, AI-powered search, and a beautiful React frontend.

## ✨ Features

### 🤖 AI-Powered Recommendations
- **Gemini AI Integration**: Advanced movie recommendations using Google's Gemini AI
- **Smart Search**: AI-powered search with natural language queries
- **Intelligent Analysis**: Detailed AI explanations for recommendations

### 🎭 Live Movie Data
- **TMDB API Integration**: Real-time movie data from The Movie Database
- **Live Poster Images**: High-quality movie posters and backdrops
- **Up-to-date Information**: Latest movies, ratings, and metadata

### 🎨 Beautiful Frontend
- **React-based UI**: Modern, responsive web interface
- **Vertical Movie Layout**: Enhanced movie card display with rich information
- **Beautiful AI Response Formatting**: Styled AI analysis with proper indentation
- **Dark Theme**: Professional cinema-style design

### 🔍 Advanced Search Features
- **Multiple Search Modes**: Regular search and AI-powered search
- **Category Browsing**: Popular, trending, and top-rated movies
- **Detailed Movie Pages**: Comprehensive movie information
- **Smart Filtering**: AI-based movie filtering and recommendations

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 14+
- TMDB API Key
- Gemini AI API Key (optional, for AI features)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/CinemaAI-Pro.git
   cd CinemaAI-Pro
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup TMDB API Key**
   - Get your API key from [TMDB](https://www.themoviedb.org/settings/api)
   - Update the `TMDB_API_KEYS` list in `web_server.py` with your key

4. **Install Frontend dependencies**
   ```bash
   cd frontend
   npm install
   npm run build
   cd ..
   ```

5. **Run the application**
   ```bash
   python web_server.py
   ```

6. **Access the application**
   - Open your browser and go to `http://localhost:5000`

## 🛠️ Configuration

### TMDB API Setup
Replace the placeholder in `web_server.py`:
```python
TMDB_API_KEYS = [
    "your_tmdb_api_key_here",
    # Add more keys for redundancy
]
```

### Gemini AI Setup (Optional)
Set the environment variable:
```bash
export GEMINI_API_KEY="your_gemini_api_key_here"
```

## 📱 Usage

### Basic Search
- Navigate to the home page
- Browse popular, trending, or top-rated movies
- Click on any movie for detailed information

### AI-Powered Search
- Use the search bar with natural language queries
- Examples:
  - "Action movies with robots"
  - "Romantic comedies from the 90s"
  - "Latest sci-fi movies"
  - "Horror movies like The Exorcist"

### Movie Recommendations
- Get AI-powered recommendations for any movie
- Detailed analysis explaining why movies are recommended

## 🏗️ Architecture

### Backend (Flask)
- **web_server.py**: Main Flask application
- **src/ai/gemini.py**: Gemini AI integration
- **src/data_loader.py**: Data loading utilities
- **src/recommender.py**: Recommendation engine

### Frontend (React)
- **Responsive Design**: Works on desktop and mobile
- **Component-based**: Modular React components
- **State Management**: Redux for global state
- **Routing**: React Router for navigation

### APIs
- **TMDB API**: Live movie data and images
- **Gemini AI**: Advanced recommendations and analysis

## 🎯 Key Improvements Made

1. **Migrated from Static Dataset to Live TMDB API**
   - Real-time movie data instead of 2017 TMDB 5000 dataset
   - Live poster images and metadata
   - Up-to-date movie information

2. **Enhanced AI Search Interface**
   - Vertical movie layout for better browsing
   - Beautiful AI response formatting with proper indentation
   - Rich movie cards with overviews, ratings, and genres

3. **Improved User Experience**
   - Professional dark theme design
   - Responsive layout for all devices
   - Smooth animations and hover effects
   - Better error handling and loading states

4. **Technical Enhancements**
   - Multiple API key support for redundancy
   - Better error handling and fallbacks
   - Optimized API calls and caching
   - Modern React frontend with Vite build system

## 📊 Project Structure

```
CinemaAI-Pro/
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/          # Page components
│   │   ├── utils/          # Utilities and API calls
│   │   └── assets/         # Static assets
│   └── dist/               # Built frontend files
├── src/                     # Backend source code
│   ├── ai/                 # AI integration
│   ├── utils/              # Utility functions
│   └── recommender.py      # Recommendation engine
├── data/                    # Dataset files (optional)
├── artifacts/               # Model artifacts
├── web_server.py           # Main Flask application
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🔧 Development

### Running in Development Mode

1. **Backend development**
   ```bash
   python web_server.py
   ```

2. **Frontend development**
   ```bash
   cd frontend
   npm run dev
   ```

### Building for Production

1. **Build frontend**
   ```bash
   cd frontend
   npm run build
   ```

2. **Run production server**
   ```bash
   python web_server.py
   ```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [The Movie Database (TMDB)](https://www.themoviedb.org/) for providing the movie data API
- [Google Gemini AI](https://ai.google.dev/) for advanced AI capabilities
- Original movie recommendation system inspiration from various open-source projects

## 🔗 Links

- [TMDB API Documentation](https://developers.themoviedb.org/3)
- [Gemini AI Documentation](https://ai.google.dev/docs)
- [React Documentation](https://reactjs.org/docs)
- [Flask Documentation](https://flask.palletsprojects.com/)

---

**Built with ❤️ for movie enthusiasts everywhere!**
