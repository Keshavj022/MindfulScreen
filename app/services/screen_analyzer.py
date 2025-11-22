import os
import base64
from pathlib import Path
from datetime import datetime
import json
import re
from openai import OpenAI
from app import db
from app.models import FrameAnalysis
from app.utils.encryption import EncryptionService
from config import Config

class ScreenAnalyzerService:
    # Comprehensive app/website recognition database
    APP_DATABASE = {
        # Social Media
        'instagram': {'category': 'social_media', 'wellness_impact': 'moderate_risk', 'keywords': ['instagram', 'insta', '@']},
        'facebook': {'category': 'social_media', 'wellness_impact': 'moderate_risk', 'keywords': ['facebook', 'fb', 'meta']},
        'twitter': {'category': 'social_media', 'wellness_impact': 'moderate_risk', 'keywords': ['twitter', 'x.com', 'tweet']},
        'tiktok': {'category': 'social_media', 'wellness_impact': 'high_risk', 'keywords': ['tiktok', 'fyp', 'for you']},
        'snapchat': {'category': 'social_media', 'wellness_impact': 'moderate_risk', 'keywords': ['snapchat', 'snap']},
        'linkedin': {'category': 'professional', 'wellness_impact': 'positive', 'keywords': ['linkedin', 'connections']},
        'reddit': {'category': 'social_media', 'wellness_impact': 'moderate_risk', 'keywords': ['reddit', 'subreddit', 'r/']},
        'pinterest': {'category': 'social_media', 'wellness_impact': 'neutral', 'keywords': ['pinterest', 'pin']},
        'tumblr': {'category': 'social_media', 'wellness_impact': 'moderate_risk', 'keywords': ['tumblr']},
        'discord': {'category': 'messaging', 'wellness_impact': 'neutral', 'keywords': ['discord', 'server']},
        'threads': {'category': 'social_media', 'wellness_impact': 'moderate_risk', 'keywords': ['threads']},
        'mastodon': {'category': 'social_media', 'wellness_impact': 'neutral', 'keywords': ['mastodon', 'toot']},
        'bluesky': {'category': 'social_media', 'wellness_impact': 'neutral', 'keywords': ['bluesky', 'bsky']},

        # Video Streaming
        'youtube': {'category': 'video', 'wellness_impact': 'variable', 'keywords': ['youtube', 'yt', 'subscribe']},
        'netflix': {'category': 'entertainment', 'wellness_impact': 'moderate_risk', 'keywords': ['netflix', 'watch now']},
        'prime_video': {'category': 'entertainment', 'wellness_impact': 'moderate_risk', 'keywords': ['prime video', 'amazon video']},
        'disney_plus': {'category': 'entertainment', 'wellness_impact': 'neutral', 'keywords': ['disney+', 'disney plus']},
        'hulu': {'category': 'entertainment', 'wellness_impact': 'moderate_risk', 'keywords': ['hulu']},
        'hbo_max': {'category': 'entertainment', 'wellness_impact': 'moderate_risk', 'keywords': ['hbo', 'max']},
        'twitch': {'category': 'entertainment', 'wellness_impact': 'moderate_risk', 'keywords': ['twitch', 'stream', 'live']},
        'vimeo': {'category': 'video', 'wellness_impact': 'neutral', 'keywords': ['vimeo']},
        'crunchyroll': {'category': 'entertainment', 'wellness_impact': 'neutral', 'keywords': ['crunchyroll', 'anime']},

        # Messaging
        'whatsapp': {'category': 'messaging', 'wellness_impact': 'neutral', 'keywords': ['whatsapp', 'wa.me']},
        'telegram': {'category': 'messaging', 'wellness_impact': 'neutral', 'keywords': ['telegram', 't.me']},
        'messenger': {'category': 'messaging', 'wellness_impact': 'neutral', 'keywords': ['messenger', 'fb messenger']},
        'imessage': {'category': 'messaging', 'wellness_impact': 'neutral', 'keywords': ['imessage', 'messages']},
        'slack': {'category': 'work', 'wellness_impact': 'positive', 'keywords': ['slack', 'channel']},
        'teams': {'category': 'work', 'wellness_impact': 'positive', 'keywords': ['teams', 'microsoft teams']},
        'zoom': {'category': 'work', 'wellness_impact': 'positive', 'keywords': ['zoom', 'meeting']},
        'google_meet': {'category': 'work', 'wellness_impact': 'positive', 'keywords': ['google meet', 'meet.google']},
        'webex': {'category': 'work', 'wellness_impact': 'positive', 'keywords': ['webex', 'cisco']},
        'signal': {'category': 'messaging', 'wellness_impact': 'neutral', 'keywords': ['signal']},

        # Productivity & Work
        'gmail': {'category': 'work', 'wellness_impact': 'positive', 'keywords': ['gmail', 'inbox']},
        'outlook': {'category': 'work', 'wellness_impact': 'positive', 'keywords': ['outlook', 'microsoft outlook']},
        'google_docs': {'category': 'work', 'wellness_impact': 'positive', 'keywords': ['google docs', 'docs.google']},
        'google_sheets': {'category': 'work', 'wellness_impact': 'positive', 'keywords': ['google sheets', 'sheets.google']},
        'google_slides': {'category': 'work', 'wellness_impact': 'positive', 'keywords': ['google slides', 'slides.google']},
        'microsoft_word': {'category': 'work', 'wellness_impact': 'positive', 'keywords': ['word', 'microsoft word', '.docx']},
        'microsoft_excel': {'category': 'work', 'wellness_impact': 'positive', 'keywords': ['excel', 'spreadsheet', '.xlsx']},
        'microsoft_powerpoint': {'category': 'work', 'wellness_impact': 'positive', 'keywords': ['powerpoint', 'ppt', '.pptx']},
        'notion': {'category': 'work', 'wellness_impact': 'positive', 'keywords': ['notion', 'workspace']},
        'trello': {'category': 'work', 'wellness_impact': 'positive', 'keywords': ['trello', 'board']},
        'asana': {'category': 'work', 'wellness_impact': 'positive', 'keywords': ['asana', 'task']},
        'jira': {'category': 'work', 'wellness_impact': 'positive', 'keywords': ['jira', 'atlassian']},
        'confluence': {'category': 'work', 'wellness_impact': 'positive', 'keywords': ['confluence']},
        'monday': {'category': 'work', 'wellness_impact': 'positive', 'keywords': ['monday.com']},
        'evernote': {'category': 'work', 'wellness_impact': 'positive', 'keywords': ['evernote']},
        'dropbox': {'category': 'work', 'wellness_impact': 'positive', 'keywords': ['dropbox']},
        'google_drive': {'category': 'work', 'wellness_impact': 'positive', 'keywords': ['google drive', 'drive.google']},
        'onedrive': {'category': 'work', 'wellness_impact': 'positive', 'keywords': ['onedrive']},
        'figma': {'category': 'work', 'wellness_impact': 'positive', 'keywords': ['figma', 'design']},
        'canva': {'category': 'work', 'wellness_impact': 'positive', 'keywords': ['canva']},
        'airtable': {'category': 'work', 'wellness_impact': 'positive', 'keywords': ['airtable']},

        # Development
        'github': {'category': 'work', 'wellness_impact': 'positive', 'keywords': ['github', 'repository', 'commit']},
        'gitlab': {'category': 'work', 'wellness_impact': 'positive', 'keywords': ['gitlab']},
        'vscode': {'category': 'work', 'wellness_impact': 'positive', 'keywords': ['visual studio code', 'vscode']},
        'xcode': {'category': 'work', 'wellness_impact': 'positive', 'keywords': ['xcode']},
        'android_studio': {'category': 'work', 'wellness_impact': 'positive', 'keywords': ['android studio']},
        'terminal': {'category': 'work', 'wellness_impact': 'positive', 'keywords': ['terminal', 'command line', 'bash']},
        'stackoverflow': {'category': 'educational', 'wellness_impact': 'positive', 'keywords': ['stackoverflow', 'stack overflow']},
        'codepen': {'category': 'work', 'wellness_impact': 'positive', 'keywords': ['codepen']},
        'replit': {'category': 'educational', 'wellness_impact': 'positive', 'keywords': ['replit']},

        # Educational
        'coursera': {'category': 'educational', 'wellness_impact': 'positive', 'keywords': ['coursera', 'course']},
        'udemy': {'category': 'educational', 'wellness_impact': 'positive', 'keywords': ['udemy']},
        'khan_academy': {'category': 'educational', 'wellness_impact': 'positive', 'keywords': ['khan academy', 'khanacademy']},
        'edx': {'category': 'educational', 'wellness_impact': 'positive', 'keywords': ['edx']},
        'duolingo': {'category': 'educational', 'wellness_impact': 'positive', 'keywords': ['duolingo', 'language learning']},
        'quizlet': {'category': 'educational', 'wellness_impact': 'positive', 'keywords': ['quizlet', 'flashcards']},
        'wikipedia': {'category': 'educational', 'wellness_impact': 'positive', 'keywords': ['wikipedia', 'wiki']},
        'medium': {'category': 'educational', 'wellness_impact': 'positive', 'keywords': ['medium', 'read more']},
        'google_scholar': {'category': 'educational', 'wellness_impact': 'positive', 'keywords': ['google scholar', 'scholar.google']},
        'brilliant': {'category': 'educational', 'wellness_impact': 'positive', 'keywords': ['brilliant.org']},
        'skillshare': {'category': 'educational', 'wellness_impact': 'positive', 'keywords': ['skillshare']},
        'linkedin_learning': {'category': 'educational', 'wellness_impact': 'positive', 'keywords': ['linkedin learning']},

        # Shopping
        'amazon': {'category': 'shopping', 'wellness_impact': 'moderate_risk', 'keywords': ['amazon', 'buy now', 'add to cart']},
        'ebay': {'category': 'shopping', 'wellness_impact': 'moderate_risk', 'keywords': ['ebay', 'bid']},
        'etsy': {'category': 'shopping', 'wellness_impact': 'neutral', 'keywords': ['etsy', 'handmade']},
        'shopify': {'category': 'shopping', 'wellness_impact': 'moderate_risk', 'keywords': ['shopify']},
        'walmart': {'category': 'shopping', 'wellness_impact': 'moderate_risk', 'keywords': ['walmart']},
        'target': {'category': 'shopping', 'wellness_impact': 'moderate_risk', 'keywords': ['target']},
        'alibaba': {'category': 'shopping', 'wellness_impact': 'moderate_risk', 'keywords': ['alibaba', 'aliexpress']},
        'wish': {'category': 'shopping', 'wellness_impact': 'moderate_risk', 'keywords': ['wish.com']},

        # Gaming
        'steam': {'category': 'gaming', 'wellness_impact': 'moderate_risk', 'keywords': ['steam', 'store']},
        'epic_games': {'category': 'gaming', 'wellness_impact': 'moderate_risk', 'keywords': ['epic games', 'fortnite']},
        'roblox': {'category': 'gaming', 'wellness_impact': 'moderate_risk', 'keywords': ['roblox']},
        'minecraft': {'category': 'gaming', 'wellness_impact': 'neutral', 'keywords': ['minecraft']},
        'playstation': {'category': 'gaming', 'wellness_impact': 'moderate_risk', 'keywords': ['playstation', 'psn']},
        'xbox': {'category': 'gaming', 'wellness_impact': 'moderate_risk', 'keywords': ['xbox', 'game pass']},
        'nintendo': {'category': 'gaming', 'wellness_impact': 'neutral', 'keywords': ['nintendo', 'switch']},
        'blizzard': {'category': 'gaming', 'wellness_impact': 'moderate_risk', 'keywords': ['blizzard', 'battle.net']},
        'league_of_legends': {'category': 'gaming', 'wellness_impact': 'high_risk', 'keywords': ['league of legends', 'lol']},
        'valorant': {'category': 'gaming', 'wellness_impact': 'moderate_risk', 'keywords': ['valorant']},
        'genshin': {'category': 'gaming', 'wellness_impact': 'moderate_risk', 'keywords': ['genshin impact', 'genshin']},

        # News
        'cnn': {'category': 'news', 'wellness_impact': 'variable', 'keywords': ['cnn', 'breaking news']},
        'bbc': {'category': 'news', 'wellness_impact': 'variable', 'keywords': ['bbc', 'bbc news']},
        'nytimes': {'category': 'news', 'wellness_impact': 'variable', 'keywords': ['nytimes', 'new york times']},
        'washington_post': {'category': 'news', 'wellness_impact': 'variable', 'keywords': ['washington post', 'wapo']},
        'reuters': {'category': 'news', 'wellness_impact': 'neutral', 'keywords': ['reuters']},
        'ap_news': {'category': 'news', 'wellness_impact': 'neutral', 'keywords': ['ap news', 'associated press']},
        'guardian': {'category': 'news', 'wellness_impact': 'variable', 'keywords': ['guardian', 'theguardian']},
        'huffpost': {'category': 'news', 'wellness_impact': 'variable', 'keywords': ['huffpost', 'huffington']},
        'fox_news': {'category': 'news', 'wellness_impact': 'variable', 'keywords': ['fox news']},
        'google_news': {'category': 'news', 'wellness_impact': 'variable', 'keywords': ['google news', 'news.google']},

        # Health & Fitness
        'strava': {'category': 'health', 'wellness_impact': 'positive', 'keywords': ['strava', 'activity']},
        'fitbit': {'category': 'health', 'wellness_impact': 'positive', 'keywords': ['fitbit']},
        'myfitnesspal': {'category': 'health', 'wellness_impact': 'positive', 'keywords': ['myfitnesspal', 'calories']},
        'headspace': {'category': 'health', 'wellness_impact': 'positive', 'keywords': ['headspace', 'meditation']},
        'calm': {'category': 'health', 'wellness_impact': 'positive', 'keywords': ['calm', 'sleep', 'relax']},
        'peloton': {'category': 'health', 'wellness_impact': 'positive', 'keywords': ['peloton']},
        'apple_health': {'category': 'health', 'wellness_impact': 'positive', 'keywords': ['apple health', 'health app']},
        'nike_run': {'category': 'health', 'wellness_impact': 'positive', 'keywords': ['nike run', 'nike training']},

        # Finance
        'banking': {'category': 'finance', 'wellness_impact': 'neutral', 'keywords': ['bank', 'account', 'balance']},
        'robinhood': {'category': 'finance', 'wellness_impact': 'moderate_risk', 'keywords': ['robinhood', 'stocks']},
        'coinbase': {'category': 'finance', 'wellness_impact': 'moderate_risk', 'keywords': ['coinbase', 'crypto']},
        'paypal': {'category': 'finance', 'wellness_impact': 'neutral', 'keywords': ['paypal']},
        'venmo': {'category': 'finance', 'wellness_impact': 'neutral', 'keywords': ['venmo']},
        'mint': {'category': 'finance', 'wellness_impact': 'positive', 'keywords': ['mint', 'budget']},

        # Travel
        'google_maps': {'category': 'utility', 'wellness_impact': 'positive', 'keywords': ['google maps', 'maps.google', 'directions']},
        'uber': {'category': 'utility', 'wellness_impact': 'neutral', 'keywords': ['uber', 'ride']},
        'lyft': {'category': 'utility', 'wellness_impact': 'neutral', 'keywords': ['lyft']},
        'airbnb': {'category': 'travel', 'wellness_impact': 'neutral', 'keywords': ['airbnb']},
        'booking': {'category': 'travel', 'wellness_impact': 'neutral', 'keywords': ['booking.com']},
        'expedia': {'category': 'travel', 'wellness_impact': 'neutral', 'keywords': ['expedia']},
        'tripadvisor': {'category': 'travel', 'wellness_impact': 'neutral', 'keywords': ['tripadvisor']},

        # Food
        'doordash': {'category': 'food', 'wellness_impact': 'neutral', 'keywords': ['doordash']},
        'ubereats': {'category': 'food', 'wellness_impact': 'neutral', 'keywords': ['uber eats', 'ubereats']},
        'grubhub': {'category': 'food', 'wellness_impact': 'neutral', 'keywords': ['grubhub']},
        'instacart': {'category': 'food', 'wellness_impact': 'neutral', 'keywords': ['instacart']},
        'yelp': {'category': 'food', 'wellness_impact': 'neutral', 'keywords': ['yelp', 'reviews']},

        # Music
        'spotify': {'category': 'music', 'wellness_impact': 'positive', 'keywords': ['spotify', 'playlist']},
        'apple_music': {'category': 'music', 'wellness_impact': 'positive', 'keywords': ['apple music']},
        'soundcloud': {'category': 'music', 'wellness_impact': 'neutral', 'keywords': ['soundcloud']},
        'pandora': {'category': 'music', 'wellness_impact': 'positive', 'keywords': ['pandora']},
        'youtube_music': {'category': 'music', 'wellness_impact': 'positive', 'keywords': ['youtube music']},

        # Dating
        'tinder': {'category': 'dating', 'wellness_impact': 'moderate_risk', 'keywords': ['tinder', 'swipe']},
        'bumble': {'category': 'dating', 'wellness_impact': 'moderate_risk', 'keywords': ['bumble']},
        'hinge': {'category': 'dating', 'wellness_impact': 'moderate_risk', 'keywords': ['hinge']},
        'okcupid': {'category': 'dating', 'wellness_impact': 'moderate_risk', 'keywords': ['okcupid']},

        # AI Tools
        'chatgpt': {'category': 'ai_tools', 'wellness_impact': 'positive', 'keywords': ['chatgpt', 'openai']},
        'claude': {'category': 'ai_tools', 'wellness_impact': 'positive', 'keywords': ['claude', 'anthropic']},
        'midjourney': {'category': 'ai_tools', 'wellness_impact': 'neutral', 'keywords': ['midjourney']},
        'dalle': {'category': 'ai_tools', 'wellness_impact': 'neutral', 'keywords': ['dall-e', 'dalle']},
        'perplexity': {'category': 'ai_tools', 'wellness_impact': 'positive', 'keywords': ['perplexity']},
        'copilot': {'category': 'ai_tools', 'wellness_impact': 'positive', 'keywords': ['copilot', 'github copilot']},
    }

    # Content category definitions with wellness mappings
    CONTENT_CATEGORIES = {
        'social_media': {'description': 'Social networking content', 'default_impact': 'moderate_risk'},
        'video': {'description': 'Video content', 'default_impact': 'variable'},
        'entertainment': {'description': 'Entertainment and leisure', 'default_impact': 'moderate_risk'},
        'messaging': {'description': 'Communication and messaging', 'default_impact': 'neutral'},
        'work': {'description': 'Work and productivity', 'default_impact': 'positive'},
        'professional': {'description': 'Professional networking', 'default_impact': 'positive'},
        'educational': {'description': 'Learning and education', 'default_impact': 'positive'},
        'shopping': {'description': 'Online shopping', 'default_impact': 'moderate_risk'},
        'gaming': {'description': 'Gaming content', 'default_impact': 'moderate_risk'},
        'news': {'description': 'News and current events', 'default_impact': 'variable'},
        'health': {'description': 'Health and fitness', 'default_impact': 'positive'},
        'finance': {'description': 'Financial services', 'default_impact': 'neutral'},
        'utility': {'description': 'Utility apps', 'default_impact': 'neutral'},
        'travel': {'description': 'Travel planning', 'default_impact': 'neutral'},
        'food': {'description': 'Food delivery and dining', 'default_impact': 'neutral'},
        'music': {'description': 'Music streaming', 'default_impact': 'positive'},
        'dating': {'description': 'Dating apps', 'default_impact': 'moderate_risk'},
        'ai_tools': {'description': 'AI assistants and tools', 'default_impact': 'positive'},
        'other': {'description': 'Other content', 'default_impact': 'neutral'}
    }

    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.frames_dir = Config.FRAMES_FOLDER
        self.encryption_service = EncryptionService(Config.ENCRYPTION_KEY) if Config.ENCRYPT_FRAMES else None

    def analyze_frame(self, session_id, frame_number, timestamp, frame_data, audio_text=None):
        frame_path = self._save_frame(session_id, frame_number, frame_data)

        vision_analysis = self._analyze_with_gpt4_vision(frame_path)

        translated_text = None
        if vision_analysis.get('extracted_text'):
            detected_lang = vision_analysis.get('detected_language', 'en')
            if detected_lang != 'en':
                translated_text = self._translate_text(vision_analysis['extracted_text'], detected_lang)

        audio_analysis = None
        if audio_text:
            audio_analysis = self._analyze_audio_text(audio_text)

        sentiment_analysis = self._analyze_sentiment(
            vision_analysis.get('content_description', ''),
            translated_text or vision_analysis.get('extracted_text', ''),
            audio_analysis.get('translated_text') if audio_analysis else None
        )

        # Enhanced wellness impact with new indicators
        wellness_impact = self._determine_wellness_impact(
            vision_analysis.get('content_type'),
            sentiment_analysis['sentiment'],
            vision_analysis.get('app_detected'),
            vision_analysis.get('engagement_indicators'),
            vision_analysis.get('potential_concerns')
        )

        frame_analysis = FrameAnalysis(
            session_id=session_id,
            frame_number=frame_number,
            timestamp=timestamp,
            frame_path=str(frame_path),
            app_detected=vision_analysis.get('app_detected'),
            content_type=vision_analysis.get('content_type'),
            extracted_text=vision_analysis.get('extracted_text'),
            detected_language=vision_analysis.get('detected_language'),
            sentiment=sentiment_analysis['sentiment'],
            sentiment_score=sentiment_analysis['score'],
            objects_detected=vision_analysis.get('objects_detected', []),
            content_description=vision_analysis.get('content_description'),
            wellness_impact=wellness_impact
        )

        db.session.add(frame_analysis)
        db.session.commit()

        return {
            'frame_number': frame_number,
            'app': vision_analysis.get('app_detected'),
            'content_type': vision_analysis.get('content_type'),
            'sentiment': sentiment_analysis['sentiment'],
            'wellness_impact': wellness_impact,
            'extracted_text': vision_analysis.get('extracted_text', ''),
            'content_description': vision_analysis.get('content_description', ''),
            'engagement_indicators': vision_analysis.get('engagement_indicators', {}),
            'potential_concerns': vision_analysis.get('potential_concerns', [])
        }

    def _identify_app_from_content(self, detected_app, extracted_text, description):
        """Use the comprehensive app database to accurately identify the app/website"""
        detected_app_lower = (detected_app or '').lower()
        text_lower = (extracted_text or '').lower()
        desc_lower = (description or '').lower()
        combined = f"{detected_app_lower} {text_lower} {desc_lower}"

        best_match = None
        best_score = 0

        for app_name, app_info in self.APP_DATABASE.items():
            score = 0
            for keyword in app_info['keywords']:
                if keyword.lower() in combined:
                    # Higher weight for app name detection
                    if keyword.lower() in detected_app_lower:
                        score += 3
                    elif keyword.lower() in text_lower:
                        score += 2
                    else:
                        score += 1

            if score > best_score:
                best_score = score
                best_match = app_name

        if best_match and best_score >= 2:
            return best_match.replace('_', ' ').title(), self.APP_DATABASE[best_match]['category']

        return detected_app or 'Unknown', None

    def _analyze_with_gpt4_vision(self, frame_path):
        if self.encryption_service and str(frame_path).endswith('.enc'):
            image_bytes = self.encryption_service.decrypt_file(frame_path)
            image_data = base64.b64encode(image_bytes).decode('utf-8')
        else:
            with open(frame_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')

        # Enhanced prompt for better text extraction and categorization
        app_list = ', '.join([k.replace('_', ' ').title() for k in list(self.APP_DATABASE.keys())[:50]])
        category_list = ', '.join(self.CONTENT_CATEGORIES.keys())

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"""You are an expert screen content analyzer. Analyze this screen recording frame with extreme precision.

**CRITICAL: Extract ALL visible text** - Read every piece of text on the screen including:
- App/website names, titles, headers
- Navigation menus, buttons, tabs
- Posts, comments, messages
- Usernames, handles, profile names
- Timestamps, dates
- Any captions, subtitles
- URLs, links
- Notifications, badges

**App/Website Detection:**
Identify the specific app or website from this list or similar: {app_list}
Look for logos, UI patterns, color schemes, layout characteristics.

**Content Categorization:**
Categorize into one of: {category_list}
Consider the actual content being viewed, not just the platform.

**Return ONLY valid JSON with these exact keys:**
{{
    "app_detected": "Specific app/website name",
    "content_type": "category from the list above",
    "extracted_text": "ALL visible text, separated by | for different sections",
    "detected_language": "primary language code (en, hi, es, fr, de, zh, ja, ko, ar, pt, ru, etc.)",
    "content_description": "Detailed description of what's shown on screen",
    "objects_detected": ["list", "of", "UI elements", "and", "objects"],
    "engagement_indicators": {{
        "has_notifications": true/false,
        "has_comments": true/false,
        "has_likes": true/false,
        "is_video_playing": true/false,
        "is_scrollable_feed": true/false
    }},
    "content_tone": "positive/negative/neutral/mixed",
    "potential_concerns": ["list any concerning content like clickbait, FOMO, etc."]
}}"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000
        )

        try:
            content = response.choices[0].message.content
            # Clean up markdown code blocks if present
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0]
            elif '```' in content:
                content = content.split('```')[1].split('```')[0]

            result = json.loads(content.strip())

            # Use app database to enhance detection
            enhanced_app, enhanced_category = self._identify_app_from_content(
                result.get('app_detected'),
                result.get('extracted_text'),
                result.get('content_description')
            )

            if enhanced_category:
                result['app_detected'] = enhanced_app
                result['content_type'] = enhanced_category

            return result
        except Exception as e:
            print(f"Vision analysis error: {e}")
            return {
                'app_detected': 'Unknown',
                'content_type': 'other',
                'extracted_text': '',
                'detected_language': 'en',
                'content_description': 'Unable to analyze',
                'objects_detected': [],
                'engagement_indicators': {},
                'content_tone': 'neutral',
                'potential_concerns': []
            }

    def _translate_text(self, text, source_lang):
        if not text or len(text) < 3:
            return text

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": f"Translate this text from {source_lang} to English. Only return the translation, nothing else:\n\n{text}"
                    }
                ],
                max_tokens=200
            )
            return response.choices[0].message.content.strip()
        except:
            return text

    def _analyze_audio_text(self, audio_text):
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": f"""Analyze this audio transcription:
"{audio_text}"

Provide:
1. Detected language code
2. If not English, translate to English
3. Content category (conversation, educational, entertainment, news, other)

Return as JSON with keys: detected_language, translated_text, category"""
                }
            ],
            max_tokens=300
        )

        try:
            return json.loads(response.choices[0].message.content)
        except:
            return {
                'detected_language': 'en',
                'translated_text': audio_text,
                'category': 'other'
            }

    def _analyze_sentiment(self, description, text, audio_text):
        combined_content = f"Visual: {description}. Text: {text}."
        if audio_text:
            combined_content += f" Audio: {audio_text}"

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": f"""Analyze the sentiment and emotional impact of this content:
{combined_content}

Classify as: positive, negative, neutral, or mixed
Also provide a sentiment score from -1.0 (very negative) to 1.0 (very positive)

Return as JSON with keys: sentiment, score"""
                }
            ],
            max_tokens=100
        )

        try:
            result = json.loads(response.choices[0].message.content)
            return result
        except:
            return {'sentiment': 'neutral', 'score': 0.0}

    def _determine_wellness_impact(self, content_type, sentiment, app, engagement_indicators=None, potential_concerns=None):
        """
        Enhanced wellness impact determination using app database and content analysis
        Returns: 'positive', 'neutral', 'negative', or 'high_risk'
        """
        app_lower = (app or '').lower().replace(' ', '_')
        engagement = engagement_indicators or {}
        concerns = potential_concerns or []

        # Check app database for known wellness impacts
        app_impact = None
        for app_name, app_info in self.APP_DATABASE.items():
            if app_name in app_lower or app_lower in app_name:
                app_impact = app_info['wellness_impact']
                break

        # High risk indicators
        high_risk_indicators = [
            app_impact == 'high_risk',
            sentiment == 'negative' and engagement.get('is_scrollable_feed'),
            len(concerns) >= 3,
            'addiction' in str(concerns).lower(),
            'fomo' in str(concerns).lower()
        ]

        # Positive indicators
        positive_indicators = [
            content_type in ['educational', 'work', 'health', 'professional'],
            app_impact == 'positive',
            sentiment == 'positive' and content_type != 'social_media'
        ]

        # Negative indicators
        negative_indicators = [
            sentiment == 'negative',
            app_impact == 'moderate_risk' and engagement.get('is_scrollable_feed'),
            content_type in ['gaming', 'entertainment'] and engagement.get('is_video_playing'),
            len(concerns) >= 2
        ]

        # Calculate impact score
        if sum(high_risk_indicators) >= 2:
            return 'negative'
        elif sum(positive_indicators) >= 2:
            return 'positive'
        elif sum(negative_indicators) >= 2:
            return 'negative'
        elif app_impact == 'moderate_risk':
            return 'neutral'
        elif app_impact == 'positive':
            return 'positive'
        else:
            return 'neutral'

    def _save_frame(self, session_id, frame_number, frame_data):
        session_dir = self.frames_dir / str(session_id)
        session_dir.mkdir(parents=True, exist_ok=True)

        frame_path = session_dir / f"frame_{frame_number:04d}.jpg"
        frame_data.save(str(frame_path))

        if self.encryption_service:
            encrypted_path = self.encryption_service.encrypt_file(frame_path)
            return Path(encrypted_path)

        return frame_path

    def generate_session_summary(self, session_id):
        frames = FrameAnalysis.query.filter_by(session_id=session_id).all()

        if not frames:
            return {
                'total_frames': 0,
                'duration_seconds': 0,
                'wellness_score': 5.0,
                'productivity_score': 5.0,
                'sentiment_distribution': {},
                'app_usage': {},
                'content_categories': {}
            }

        sentiment_dist = {'positive': 0, 'negative': 0, 'neutral': 0, 'mixed': 0}
        app_usage = {}
        content_categories = {}
        wellness_impacts = {'positive': 0, 'negative': 0, 'neutral': 0}

        for frame in frames:
            sentiment_dist[frame.sentiment] = sentiment_dist.get(frame.sentiment, 0) + 1

            if frame.app_detected:
                app_usage[frame.app_detected] = app_usage.get(frame.app_detected, 0) + 1

            if frame.content_type:
                content_categories[frame.content_type] = content_categories.get(frame.content_type, 0) + 1

            wellness_impacts[frame.wellness_impact] = wellness_impacts.get(frame.wellness_impact, 0) + 1

        total_frames = len(frames)
        duration = max([f.timestamp for f in frames]) if frames else 0

        wellness_score = (
            (wellness_impacts['positive'] * 10 + wellness_impacts['neutral'] * 5) / total_frames
            if total_frames > 0 else 5.0
        )

        productive_types = ['work', 'educational']
        productive_frames = sum(content_categories.get(t, 0) for t in productive_types)
        productivity_score = min(10, (productive_frames / total_frames * 10) if total_frames > 0 else 5.0)

        return {
            'total_frames': total_frames,
            'duration_seconds': int(duration),
            'wellness_score': round(wellness_score, 2),
            'productivity_score': round(productivity_score, 2),
            'sentiment_distribution': sentiment_dist,
            'app_usage': app_usage,
            'content_categories': content_categories
        }
