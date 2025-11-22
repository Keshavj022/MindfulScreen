"""
Quiz Service - Uses ML-based personality classification
"""

from app.services.personality_ml import get_personality_service


class QuizService:
    def __init__(self):
        self.personality_service = get_personality_service()

    def _load_questions(self):
        """Load all quiz questions using the ML personality service"""
        return self.personality_service.get_all_questions()

    def get_all_questions(self):
        """Get all questions organized by sections"""
        questions = self._load_questions()

        # Organize by dimension for the UI
        organized = {
            'big_five': [],
            'mental_health': [],
            'wellness': []
        }

        for q in questions:
            dimension = q.get('dimension', 'big_five')
            if dimension in organized:
                organized[dimension].append(q)

        return {
            'questions': questions,
            'sections': [
                {
                    'id': 'big_five',
                    'title': 'Personality Assessment',
                    'description': 'These questions help us understand your personality traits based on the scientifically validated Big Five model.',
                    'questions': organized['big_five']
                },
                {
                    'id': 'mental_health',
                    'title': 'Mental Wellness Check',
                    'description': 'Help us understand your current mental wellness state so we can provide personalized support.',
                    'questions': organized['mental_health']
                },
                {
                    'id': 'wellness',
                    'title': 'Digital Wellness',
                    'description': 'Tell us about your digital habits and goals.',
                    'questions': organized['wellness']
                }
            ],
            'total_questions': len(questions)
        }

    def analyze_responses(self, responses):
        """Analyze quiz responses using ML-based classification"""
        results = self.personality_service.analyze_responses(responses)
        return results

    def get_questions_flat(self):
        """Get flat list of questions for simple quiz rendering"""
        return self._load_questions()
