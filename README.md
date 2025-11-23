# MindfulScreen

**AI-Powered Digital Wellness Analyzer**

MindfulScreen is an intelligent digital wellness platform that leverages OpenAI's GPT-4 Vision to analyze screen activity and provide personalized insights for improving digital wellbeing. The application combines real-time screen analysis with personality assessments based on the Big Five (OCEAN) model to deliver tailored recommendations for healthier digital habits.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Deployment](#deployment)
- [Demo Account](#demo-account)

---

## Overview

MindfulScreen addresses the growing need for digital wellness management by providing:

- **Real-time Screen Analysis**: Captures and analyzes screen content using AI to understand app usage patterns
- **Personality-Based Insights**: Uses the Big Five personality model to deliver personalized recommendations
- **Wellness Tracking**: Monitors mental health and digital wellness metrics over time
- **Knowledge Graph Visualization**: Maps behavioral patterns and app usage relationships
- **Periodic Assessments**: Weekly and monthly check-ins to track progress and improvements

---

## Features

### Core Functionality

| Feature | Description |
|---------|-------------|
| **Screen Recording & Analysis** | Real-time screen capture with AI-powered analysis using GPT-4 Vision |
| **Personality Assessment** | 25-question quiz based on validated IPIP scales for Big Five personality traits |
| **Interactive Dashboard** | Comprehensive visualization of wellness metrics, app usage, and trends |
| **AI-Powered Insights** | Personalized recommendations based on screen data and personality type |
| **Knowledge Graph** | Visual representation of behavioral patterns and app relationships |
| **Periodic Assessments** | Weekly (8 questions) and monthly (10 questions) wellness check-ins |

### Security & Privacy

- Bcrypt password hashing
- CSRF protection on all forms
- Secure session cookies (HTTPS, HTTPOnly, SameSite)
- SQL injection prevention via SQLAlchemy ORM
- Data encryption for frames and analysis data
- Rate limiting on authentication endpoints
- Auto-delete frames after 30 days

### Analysis Capabilities

- Detection of 150+ apps and websites with wellness classifications
- Content type classification (productive, entertainment, social, etc.)
- Sentiment analysis (positive, negative, neutral, mixed)
- Text extraction and language detection
- Wellness impact scoring per frame
- Session-level aggregated metrics

---

## Technology Stack

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11.6 | Runtime environment |
| Flask | >=3.0.0 | Web framework |
| Flask-SQLAlchemy | >=3.1.1 | Database ORM |
| Flask-Bcrypt | >=1.0.1 | Password hashing |
| Flask-Login | >=0.6.3 | User session management |
| Flask-WTF | >=1.2.1 | CSRF protection |
| Gunicorn | >=21.2.0 | Production WSGI server |

### Database

| Technology | Purpose |
|------------|---------|
| SQLite | Local development database |
| PostgreSQL | Production database |
| SQLAlchemy >=2.0.0 | SQL toolkit and ORM |
| psycopg2-binary >=2.9.9 | PostgreSQL adapter |

### AI & Machine Learning

| Technology | Version | Purpose |
|------------|---------|---------|
| OpenAI API | >=1.12.0 | GPT-4 Vision for screen analysis |
| scikit-learn | >=1.4.0 | K-Means clustering for personality classification |
| NumPy | >=1.26.3 | Numerical computing |
| Pandas | >=2.2.0 | Data manipulation and analysis |

### Image Processing

| Technology | Version | Purpose |
|------------|---------|---------|
| Pillow | >=10.2.0 | Image manipulation |
| OpenCV | >=4.9.0.80 | Computer vision and frame extraction |

### Visualization

| Technology | Purpose |
|------------|---------|
| NetworkX >=3.2.1 | Knowledge graph analysis |
| Matplotlib >=3.8.2 | Data visualization |
| Plotly >=5.18.0 | Interactive charts |
| Chart.js | Frontend interactive charts |
| D3.js | Advanced data visualization |

### Frontend

| Technology | Purpose |
|------------|---------|
| Bootstrap 5 | UI framework |
| Jinja2 | Template engine |
| WebRTC | Screen capture API |

### Security

| Technology | Version | Purpose |
|------------|---------|---------|
| Cryptography | >=42.0.0 | Data encryption |
| python-dotenv | >=1.0.0 | Environment variable management |

---

## Project Structure

```
MindfulScreen/
├── app/
│   ├── __init__.py                 # Flask app factory and initialization
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py                 # User profile and wellness data model
│   │   ├── session.py              # Screen session and frame analysis models
│   │   ├── quiz.py                 # Quiz response model
│   │   ├── assessment.py           # Periodic assessment model
│   │   ├── knowledge_graph.py      # Knowledge graph model
│   │   └── audit_log.py            # Audit logging model
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py                 # Authentication endpoints
│   │   ├── main.py                 # Landing page and profile management
│   │   ├── quiz.py                 # Personality quiz endpoints
│   │   ├── analyzer.py             # Screen analysis endpoints
│   │   ├── dashboard.py            # Dashboard and analytics endpoints
│   │   ├── assessment.py           # Periodic assessment endpoints
│   │   └── privacy.py              # Privacy policy and terms
│   ├── services/
│   │   ├── __init__.py
│   │   ├── screen_analyzer.py      # AI frame analysis (OpenAI integration)
│   │   ├── ai_insights.py          # Personalized AI insights generation
│   │   ├── quiz_service.py         # Quiz question logic and analysis
│   │   ├── personality_ml.py       # ML clustering for personality types
│   │   ├── analytics.py            # Data analytics and trend calculation
│   │   ├── knowledge_graph.py      # Graph data visualization
│   │   ├── email_service.py        # Email/SMTP functionality
│   │   └── data_visualization.py   # Chart and visualization data
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css           # Main stylesheet
│   │   ├── js/
│   │   │   ├── analyzer.js         # Screen recording UI logic
│   │   │   ├── dashboard.js        # Dashboard interactivity
│   │   │   ├── profile.js          # Profile management
│   │   │   └── showcase.js         # Live showcase mode
│   │   ├── images/
│   │   │   ├── logo.png
│   │   │   └── transparent-logo.png
│   │   └── favicon.png
│   ├── templates/
│   │   ├── base.html               # Base template with navigation
│   │   ├── main/
│   │   │   ├── landing.html        # Homepage
│   │   │   ├── profile.html        # User profile page
│   │   │   └── showcase.html       # Live demo showcase
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   ├── signup.html
│   │   │   ├── verify_email.html
│   │   │   ├── resend_verification.html
│   │   │   └── forgot_password.html
│   │   ├── quiz/
│   │   │   └── quiz.html           # 25-question personality assessment
│   │   ├── analyzer/
│   │   │   └── analyzer.html       # Screen recording interface
│   │   ├── dashboard/
│   │   │   ├── dashboard.html      # Main dashboard
│   │   │   ├── insights.html       # AI-powered insights
│   │   │   └── progress.html       # Progress tracking
│   │   ├── assessment/
│   │   │   ├── weekly.html         # Weekly wellness check-in
│   │   │   ├── monthly.html        # Monthly assessment
│   │   │   └── history.html        # Assessment history
│   │   └── privacy/
│   │       ├── policy.html
│   │       ├── terms.html
│   │       └── data_settings.html
│   └── utils/
│       ├── __init__.py
│       ├── demo_data.py            # Demo user and sample data generation
│       └── encryption.py           # Data encryption utilities
├── config/
│   ├── __init__.py
│   └── settings.py                 # Configuration management
├── data/                           # Runtime data directory
│   ├── uploads/                    # Uploaded files
│   ├── frames/                     # Extracted frames
│   └── knowledge_graphs/           # Generated graphs
├── run.py                          # Application entry point
├── start.sh                        # Production startup script
├── setup_and_test.sh               # Development setup script
├── requirements.txt                # Python dependencies
├── runtime.txt                     # Python version specification
├── Procfile                        # Heroku deployment configuration
├── render.yaml                     # Render.com deployment configuration
├── .env.example                    # Environment variables template
└── .gitignore                      # Git ignore patterns
```

---

## Prerequisites

- **Python**: 3.11.6 or higher
- **pip**: Latest version
- **OpenAI API Key**: Required for screen analysis functionality
- **PostgreSQL** (optional): For production deployment
- **SMTP Server** (optional): For email verification features

---

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/MindfulScreen.git
cd MindfulScreen
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

```bash
cp .env.example .env
```

Edit the `.env` file with your configuration (see [Configuration](#configuration) section).

### Step 5: Initialize Database with Demo Data

```bash
python run.py --init-demo
```

### Automated Setup (Alternative)

```bash
chmod +x setup_and_test.sh
./setup_and_test.sh
```

---

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Security Keys (Required)
FLASK_SECRET_KEY=your-secret-key-here
ENCRYPTION_KEY=your-32-character-encryption-key

# Database Configuration
DATABASE_URL=sqlite:///data/mindfulscreen.db    # Development
# DATABASE_URL=postgresql://user:pass@host/db   # Production

# OpenAI API (Required for screen analysis)
OPENAI_API_KEY=sk-your-openai-api-key

# Email/SMTP Configuration (Optional - for email verification)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# OTP Settings
OTP_EXPIRY_MINUTES=10
OTP_MAX_ATTEMPTS=3

# Environment
FLASK_ENV=development
FLASK_DEBUG=True

# Demo Data Initialization
INIT_DEMO_DATA=false
```

### Application Settings

Key configuration values in `config/settings.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `MAX_CONTENT_LENGTH` | 500MB | Maximum upload size |
| `FRAME_EXTRACTION_RATE` | 2 seconds | Interval between frame captures |
| `MAX_FRAMES_PER_SESSION` | 300 | Maximum frames per recording session |
| `ENCRYPT_FRAMES` | True | Enable frame file encryption |
| `ENCRYPT_ANALYSIS_DATA` | True | Enable analysis data encryption |
| `AUTO_DELETE_FRAMES_AFTER_DAYS` | 30 | Auto-cleanup period for frames |
| `MAX_LOGIN_ATTEMPTS` | 5 | Rate limit for login attempts |
| `RATE_LIMIT_WINDOW` | 15 minutes | Window for rate limiting |

---

## Running the Application

### Development Mode

```bash
python run.py
```

Access the application at `http://localhost:5000`

### Initialize with Demo Data

```bash
python run.py --init-demo
```

### Production Mode

Using the startup script:

```bash
./start.sh
```

Using Gunicorn directly:

```bash
gunicorn run:app --bind 0.0.0.0:5000 --workers 2 --threads 4 --timeout 120
```

---

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/login` | User login |
| POST | `/auth/signup` | User registration |
| POST | `/auth/verify-email` | Email verification |
| POST | `/auth/resend-verification` | Resend verification email |
| POST | `/auth/forgot-password` | Password reset request |
| GET | `/auth/logout` | User logout |

### Profile Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/profile` | Get user profile |
| PUT | `/api/profile` | Update profile information |
| POST | `/api/change-password` | Change password |
| POST | `/api/wellness-goals` | Add wellness goal |
| DELETE | `/api/wellness-goals/<id>` | Remove wellness goal |

### Personality Quiz

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/quiz/start` | Quiz page |
| GET | `/quiz/api/questions` | Get 25 quiz questions |
| POST | `/quiz/api/submit` | Submit quiz responses |

### Screen Analyzer

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/analyzer/api/start-session` | Start recording session |
| POST | `/analyzer/api/upload-frame` | Upload and analyze frame |
| POST | `/analyzer/api/complete-session/<id>` | Complete session |
| GET | `/analyzer/api/sessions` | Get user's sessions |

### Dashboard & Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/dashboard/` | Dashboard main page |
| GET | `/dashboard/insights` | AI insights page |
| GET | `/dashboard/progress` | Progress tracking page |
| GET | `/dashboard/api/stats` | Get user statistics |
| GET | `/dashboard/api/app-usage` | App usage breakdown |
| GET | `/dashboard/api/content-analysis` | Content analysis data |
| GET | `/dashboard/api/sentiment-timeline` | Sentiment trends |
| GET | `/dashboard/api/wellness-trends` | Wellness score trends |
| GET | `/dashboard/api/knowledge-graph` | Knowledge graph data |
| GET | `/dashboard/api/app-details/<app>` | Detailed app analysis |
| GET | `/dashboard/api/ai-insights` | Comprehensive AI insights |
| GET | `/dashboard/api/quick-insights` | Quick summary insights |

### Assessments

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/assessment/weekly` | Weekly assessment page |
| POST | `/assessment/weekly/submit` | Submit weekly assessment |
| GET | `/assessment/monthly` | Monthly assessment page |
| POST | `/assessment/monthly/submit` | Submit monthly assessment |
| GET | `/assessment/history` | Assessment history |

---

## Deployment

### Render.com (Recommended)

The application includes a `render.yaml` configuration file for easy deployment:

1. Push your code to GitHub
2. Connect your Render account to the repository
3. Render automatically detects `render.yaml` and provisions:
   - Web service (Python 3.11.6)
   - PostgreSQL database
4. Add environment variables in Render dashboard:
   - `OPENAI_API_KEY`
   - `FLASK_SECRET_KEY`
   - `ENCRYPTION_KEY`
5. Deploy

### Heroku

The application includes a `Procfile` for Heroku deployment:

```bash
heroku create your-app-name
heroku addons:create heroku-postgresql:hobby-dev
heroku config:set OPENAI_API_KEY=your-key
heroku config:set FLASK_SECRET_KEY=your-secret
heroku config:set ENCRYPTION_KEY=your-encryption-key
git push heroku main
```

### Docker

```dockerfile
FROM python:3.11.6-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "run:app", "--bind", "0.0.0.0:5000", "--workers", "2"]
```

---

## Demo Account

For testing purposes, initialize the application with demo data:

```bash
python run.py --init-demo
```

**Demo Credentials:**
- **Email**: demo@mindfulscreen.com
- **Password**: demo123

The demo account includes:
- Pre-populated personality assessment results
- Sample screen sessions with analysis data
- Historical wellness metrics
- Knowledge graph data

---

## How It Works

### Screen Analysis Workflow

```
1. User grants screen/audio permissions via browser
          │
          ▼
2. Client captures frames every 2 seconds using WebRTC
          │
          ▼
3. Frames compressed to JPEG (quality 80%) and sent to server
          │
          ▼
4. Each frame analyzed by OpenAI GPT-4 Vision API
   - App/website detection (150+ supported)
   - Content type classification
   - Text extraction & language detection
   - Sentiment analysis
   - Wellness impact scoring
          │
          ▼
5. Results stored in database for aggregation
          │
          ▼
6. Session summary generated on completion
          │
          ▼
7. Dashboard updated with new insights and metrics
```

### Personality Assessment System

The 25-question personality quiz is based on the Big Five (OCEAN) model:

| Trait | Description |
|-------|-------------|
| **Openness** | Creativity, curiosity, and openness to new experiences |
| **Conscientiousness** | Organization, dependability, and self-discipline |
| **Extraversion** | Sociability, assertiveness, and positive emotions |
| **Agreeableness** | Cooperation, trust, and altruism |
| **Neuroticism** | Emotional instability and negative emotions |

The system uses K-Means clustering (5 clusters) to classify users into personality types:

- **Cluster 0**: The Balanced Individual
- **Cluster 1**: The Conscientious Achiever
- **Cluster 2**: The Social Connector
- **Cluster 3**: The Creative Explorer
- **Cluster 4**: The Analytical Thinker

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Client Browser                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │
│  │  Dashboard  │  │  Analyzer   │  │    Quiz     │                  │
│  │  (Chart.js) │  │  (WebRTC)   │  │  (Forms)    │                  │
│  └─────────────┘  └─────────────┘  └─────────────┘                  │
└────────────────────────────┬────────────────────────────────────────┘
                             │ HTTPS
┌────────────────────────────▼────────────────────────────────────────┐
│                         Flask Application                            │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                        Routes Layer                           │   │
│  │  auth.py │ main.py │ quiz.py │ analyzer.py │ dashboard.py    │   │
│  └──────────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                       Services Layer                          │   │
│  │  screen_analyzer │ ai_insights │ quiz_service │ analytics    │   │
│  │  personality_ml  │ knowledge_graph │ email_service           │   │
│  └──────────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                        Models Layer                           │   │
│  │  User │ ScreenSession │ FrameAnalysis │ Quiz │ Assessment    │   │
│  └──────────────────────────────────────────────────────────────┘   │
└────────────────────────────┬───────────────────────�────────────────┘
                             │                       │
              ┌──────────────▼──────┐    ┌───────────▼────────┐
              │     PostgreSQL      │    │    OpenAI API      │
              │   (SQLite Dev)      │    │   (GPT-4 Vision)   │
              └─────────────────────┘    └────────────────────┘
```

---

## User Guide

### 1. Sign Up & Personality Quiz

1. Create an account with email and password
2. Complete the 25-question personality assessment
3. Receive instant personality insights and type classification
4. View strengths and growth areas based on your profile

### 2. Screen Recording & Analysis

1. Navigate to the Analyzer page
2. Click "Start Recording & Analysis"
3. Grant screen and audio permissions when prompted
4. AI analyzes frames every 2 seconds in real-time
5. View live analysis results as they appear
6. Click "Stop" to end the session and generate summary

### 3. Dashboard Exploration

1. View overall wellness and productivity scores
2. Explore app usage distribution charts
3. Analyze sentiment trends over time
4. Examine the interactive knowledge graph
5. Click on individual apps for detailed analysis
6. Access AI-powered personalized insights

### 4. Periodic Assessments

1. Complete weekly check-ins (8 questions)
2. Complete monthly assessments (10 questions)
3. Track progress over time
4. View historical trends and improvements

### 5. Profile Management

1. Update personal information
2. Change password securely
3. Manage wellness goals
4. View personality type and scores

---

## Performance Optimization

| Feature | Implementation |
|---------|----------------|
| Frame extraction | 2-second intervals to balance detail and performance |
| Image compression | JPEG quality 80% for optimal size/quality ratio |
| Database queries | Indexed columns and efficient ORM queries |
| Client-side caching | Dashboard data cached for faster loads |
| Connection pooling | SQLAlchemy pool management for database connections |
| Asynchronous analysis | Frame analysis processed efficiently |

---

## Support

For issues and feature requests, please open an issue on the GitHub repository.
