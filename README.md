# MindfulScreen - AI-Powered Digital Wellness Analyzer

An intelligent web application that analyzes screen recording content using OpenAI's GPT-4 Vision to help users understand and improve their digital wellbeing.

## Features

- **AI-Powered Analysis**: Real-time screen content analysis using OpenAI GPT-4 Vision
- **Personality Quiz**: Comprehensive assessment based on Big Five and Enneagram models
- **Interactive Dashboard**: Rich visualizations of usage patterns and wellness metrics
- **Knowledge Graph**: Visual representation of user data and behavioral connections
- **Real-time Showcase**: Live demonstration mode for presentations
- **Multi-language Support**: Text extraction and translation in any language

## Tech Stack

- **Backend**: Flask, SQLAlchemy
- **AI**: OpenAI GPT-4 Vision, GPT-4o-mini
- **Frontend**: Bootstrap 5, Chart.js, Plotly, D3.js
- **Database**: SQLite
- **Security**: Bcrypt password hashing, Flask-Login

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Major
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
cp .env.example .env
```

5. Add your OpenAI API key to `.env`:
```
OPENAI_API_KEY=your-openai-api-key-here
FLASK_SECRET_KEY=your-secret-key-here
```

## Usage

1. Initialize the database and create demo data:
```bash
python run.py --init-demo
```

2. Run the application:
```bash
python run.py
```

3. Open browser and navigate to:
```
http://localhost:5000
```

4. Login with demo account:
- Email: demo@mindfulscreen.com
- Password: demo123

## Features Guide

### 1. Sign Up & Quiz
- Create account with basic demographics
- Complete 25-question personality assessment
- Get instant personality insights

### 2. Screen Analysis
- Click "Start Recording & Analysis"
- Grant screen and audio permissions
- AI analyzes frames every 2 seconds
- View real-time results
- Stop to generate complete session summary

### 3. Dashboard
- View wellness and productivity scores
- Explore app usage distribution
- Analyze sentiment trends
- Examine knowledge graph
- Click on apps for detailed analysis

### 4. Profile Management
- Update personal information
- Change password
- View personality type

### 5. Showcase Mode
- Live demonstration for presentations
- Real-time app detection
- Bounding boxes on detected objects
- Live statistics updates

## API Endpoints

- `POST /signup` - Create new user account
- `POST /login` - User authentication
- `GET /quiz/api/questions` - Get quiz questions
- `POST /quiz/api/submit` - Submit quiz responses
- `POST /analyzer/api/start-session` - Start analysis session
- `POST /analyzer/api/upload-frame` - Upload and analyze frame
- `POST /analyzer/api/complete-session/<id>` - Complete session
- `GET /dashboard/api/stats` - Get user statistics
- `GET /dashboard/api/knowledge-graph` - Get knowledge graph data

## Project Structure

```
Major/
├── app/
│   ├── models/           # Database models
│   ├── routes/           # Route handlers
│   ├── services/         # Business logic
│   ├── static/           # CSS, JS, images
│   ├── templates/        # HTML templates
│   └── utils/            # Helper functions
├── config/               # Configuration
├── data/                 # User data storage
├── requirements.txt      # Python dependencies
└── run.py               # Application entry point
```

## Security

- Passwords hashed with Bcrypt
- Secure session management with Flask-Login
- CSRF protection on all forms
- File upload validation
- Prepared SQL statements (SQLAlchemy ORM)

## Performance

- Frame extraction at 2-second intervals
- Asynchronous API calls to OpenAI
- Efficient database queries with indexes
- Client-side caching for dashboard data
- Optimized image compression (JPEG quality 80%)

## License

MIT License

## Contributors

Developed by CountZero for Digital Wellness Hackathon 2025

## Support

For issues or questions, please contact support@mindfulscreen.com
