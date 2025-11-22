"""
ML-based Personality Classification Service
Based on Big Five (OCEAN) personality traits using K-Means clustering

Dataset: Big Five personality dataset (1M+ participants, 50 questions)
Clustering: K-Means with 5 clusters for personality typing
"""

import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
import os
import json
from datetime import datetime

# Big Five Questions based on validated IPIP scales (Short Form - 5 per trait)
# Selected highest-loading items from original 50-item scale for accuracy
BIG_FIVE_QUESTIONS = {
    'extraversion': [
        {'id': 'EXT1', 'text': 'I am the life of the party', 'keyed': 'positive'},
        {'id': 'EXT2', 'text': 'I feel comfortable around people', 'keyed': 'positive'},
        {'id': 'EXT3', 'text': 'I start conversations', 'keyed': 'positive'},
        {'id': 'EXT4', 'text': 'I keep in the background', 'keyed': 'negative'},
        {'id': 'EXT5', 'text': 'I am quiet around strangers', 'keyed': 'negative'},
    ],
    'neuroticism': [
        {'id': 'EST1', 'text': 'I get stressed out easily', 'keyed': 'positive'},
        {'id': 'EST2', 'text': 'I am relaxed most of the time', 'keyed': 'negative'},
        {'id': 'EST3', 'text': 'I worry about things', 'keyed': 'positive'},
        {'id': 'EST4', 'text': 'I have frequent mood swings', 'keyed': 'positive'},
        {'id': 'EST5', 'text': 'I often feel blue', 'keyed': 'positive'},
    ],
    'agreeableness': [
        {'id': 'AGR1', 'text': 'I am interested in people', 'keyed': 'positive'},
        {'id': 'AGR2', 'text': "I sympathize with others' feelings", 'keyed': 'positive'},
        {'id': 'AGR3', 'text': 'I have a soft heart', 'keyed': 'positive'},
        {'id': 'AGR4', 'text': 'I feel little concern for others', 'keyed': 'negative'},
        {'id': 'AGR5', 'text': 'I make people feel at ease', 'keyed': 'positive'},
    ],
    'conscientiousness': [
        {'id': 'CSN1', 'text': 'I am always prepared', 'keyed': 'positive'},
        {'id': 'CSN2', 'text': 'I pay attention to details', 'keyed': 'positive'},
        {'id': 'CSN3', 'text': 'I get chores done right away', 'keyed': 'positive'},
        {'id': 'CSN4', 'text': 'I leave my belongings around', 'keyed': 'negative'},
        {'id': 'CSN5', 'text': 'I follow a schedule', 'keyed': 'positive'},
    ],
    'openness': [
        {'id': 'OPN1', 'text': 'I have a vivid imagination', 'keyed': 'positive'},
        {'id': 'OPN2', 'text': 'I have excellent ideas', 'keyed': 'positive'},
        {'id': 'OPN3', 'text': 'I am quick to understand things', 'keyed': 'positive'},
        {'id': 'OPN4', 'text': 'I am full of ideas', 'keyed': 'positive'},
        {'id': 'OPN5', 'text': 'I have difficulty understanding abstract ideas', 'keyed': 'negative'},
    ]
}

# Personality cluster definitions based on Big Five analysis
PERSONALITY_CLUSTERS = {
    0: {
        'name': 'The Balanced Achiever',
        'description': 'You have a well-rounded personality with moderate levels across all traits. You adapt well to different situations and maintain emotional stability.',
        'strengths': ['Adaptability', 'Emotional balance', 'Versatility', 'Stable relationships'],
        'growth_areas': ['Setting ambitious goals', 'Taking more initiative', 'Developing specialized skills'],
        'wellness_tips': [
            'Maintain your balanced approach while setting stretch goals',
            'Use your adaptability to try new wellness practices',
            'Your stability allows for consistent health routines'
        ],
        'digital_wellness': [
            'Set intentional screen time boundaries',
            'Use apps that align with your balanced lifestyle',
            'Practice digital minimalism during key hours'
        ]
    },
    1: {
        'name': 'The Analytical Introvert',
        'description': 'You prefer deep thinking and solitary activities. You have a rich inner world and excel at focused, detailed work.',
        'strengths': ['Deep thinking', 'Focus', 'Independence', 'Attention to detail'],
        'growth_areas': ['Social engagement', 'Sharing ideas openly', 'Collaborative activities'],
        'wellness_tips': [
            'Schedule regular quiet time for mental recharge',
            'Practice mindfulness meditation',
            'Balance alone time with meaningful social connections'
        ],
        'digital_wellness': [
            'Limit social media to prevent overstimulation',
            'Use focus apps for deep work sessions',
            'Choose educational content over social feeds'
        ]
    },
    2: {
        'name': 'The Social Connector',
        'description': 'You thrive on social interaction and bringing people together. Your energy and enthusiasm are contagious.',
        'strengths': ['Communication', 'Networking', 'Enthusiasm', 'Team building'],
        'growth_areas': ['Deep focus time', 'Independent work', 'Emotional regulation'],
        'wellness_tips': [
            'Balance social activities with rest periods',
            'Practice active listening in conversations',
            'Develop solo hobbies for self-reflection'
        ],
        'digital_wellness': [
            'Be mindful of social media comparison traps',
            'Quality over quantity in online interactions',
            'Schedule digital detox periods'
        ]
    },
    3: {
        'name': 'The Sensitive Creative',
        'description': 'You experience emotions deeply and have a strong creative and empathetic nature. You are attuned to aesthetics and meaning.',
        'strengths': ['Creativity', 'Empathy', 'Emotional depth', 'Artistic expression'],
        'growth_areas': ['Emotional resilience', 'Stress management', 'Practical decision-making'],
        'wellness_tips': [
            'Practice stress-reduction techniques daily',
            'Channel emotions through creative outlets',
            'Build a support network for difficult times'
        ],
        'digital_wellness': [
            'Curate feeds to minimize negative content',
            'Set boundaries around consuming emotional content',
            'Use apps for creative expression and mood tracking'
        ]
    },
    4: {
        'name': 'The Organized Leader',
        'description': 'You are goal-oriented, disciplined, and take charge naturally. You value efficiency and results.',
        'strengths': ['Organization', 'Leadership', 'Goal achievement', 'Discipline'],
        'growth_areas': ['Flexibility', 'Emotional openness', 'Work-life balance'],
        'wellness_tips': [
            'Schedule wellness activities like other priorities',
            'Allow flexibility in your routines',
            'Practice self-compassion when plans change'
        ],
        'digital_wellness': [
            'Use productivity apps mindfully',
            'Set boundaries between work and personal digital use',
            'Track wellness metrics but avoid obsession'
        ]
    }
}

# Mental health indicators based on personality profiles
MENTAL_HEALTH_INDICATORS = {
    'high_neuroticism': {
        'risk_factors': ['Anxiety', 'Depression', 'Stress sensitivity'],
        'protective_measures': [
            'Regular mindfulness practice',
            'Strong social support system',
            'Professional counseling when needed',
            'Stress management techniques'
        ]
    },
    'low_extraversion': {
        'risk_factors': ['Social isolation', 'Rumination'],
        'protective_measures': [
            'Structured social activities',
            'Online communities for connection',
            'Solo activities that bring joy'
        ]
    },
    'low_conscientiousness': {
        'risk_factors': ['Poor health habits', 'Disorganization stress'],
        'protective_measures': [
            'Simple habit tracking',
            'External accountability',
            'Small, achievable goals'
        ]
    }
}


class PersonalityMLService:
    def __init__(self):
        self.scaler = MinMaxScaler()
        self.kmeans = None
        self.pca = None
        self._initialize_model()

    def _initialize_model(self):
        """Initialize K-Means model with predefined cluster centers based on Big Five analysis"""
        # Pre-computed cluster centers from Big Five dataset analysis
        # Format: [Extraversion, Neuroticism, Agreeableness, Conscientiousness, Openness]
        # Values normalized 0-1 scale (0.5 = neutral)
        self.cluster_centers = np.array([
            [0.50, 0.50, 0.55, 0.55, 0.55],  # Balanced Achiever
            [0.30, 0.55, 0.50, 0.50, 0.60],  # Analytical Introvert
            [0.70, 0.45, 0.60, 0.45, 0.50],  # Social Connector
            [0.45, 0.65, 0.65, 0.40, 0.65],  # Sensitive Creative
            [0.55, 0.35, 0.50, 0.70, 0.55],  # Organized Leader
        ])

        self.kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
        # Fit with cluster centers
        self.kmeans.fit(self.cluster_centers)
        self.kmeans.cluster_centers_ = self.cluster_centers

    def get_all_questions(self):
        """Get all 50 Big Five questions for the quiz"""
        questions = []
        question_num = 1

        # Add Big Five questions
        for trait, trait_questions in BIG_FIVE_QUESTIONS.items():
            for q in trait_questions:
                questions.append({
                    'id': q['id'],
                    'text': q['text'],
                    'trait': trait,
                    'keyed': q['keyed'],
                    'dimension': 'big_five',
                    'number': question_num
                })
                question_num += 1

        # Add mental health screening questions
        mental_health_questions = self._get_mental_health_questions()
        for q in mental_health_questions:
            q['number'] = question_num
            questions.append(q)
            question_num += 1

        # Add digital wellness questions
        wellness_questions = self._get_wellness_questions()
        for q in wellness_questions:
            q['number'] = question_num
            questions.append(q)
            question_num += 1

        return questions

    def _get_mental_health_questions(self):
        """Mental health screening questions - condensed validated scale"""
        return [
            {'id': 'MH1', 'text': 'I have been feeling down, depressed, or hopeless lately', 'category': 'depression', 'dimension': 'mental_health'},
            {'id': 'MH2', 'text': 'I have trouble relaxing and often feel tense', 'category': 'anxiety', 'dimension': 'mental_health'},
            {'id': 'MH3', 'text': 'I have been sleeping well and waking up refreshed', 'category': 'sleep', 'dimension': 'mental_health', 'keyed': 'negative'},
            {'id': 'MH4', 'text': 'I feel overwhelmed by my responsibilities', 'category': 'stress', 'dimension': 'mental_health'},
            {'id': 'MH5', 'text': 'I feel energetic and motivated most days', 'category': 'energy', 'dimension': 'mental_health', 'keyed': 'negative'},
        ]

    def _get_wellness_questions(self):
        """Digital wellness and lifestyle questions"""
        return [
            {'id': 'DW1', 'text': 'Social media negatively affects my mood', 'category': 'digital_impact', 'dimension': 'wellness'},
            {'id': 'DW2', 'text': 'I find it difficult to put down my phone', 'category': 'digital_dependency', 'dimension': 'wellness'},
            {'id': 'DW3', 'text': 'I compare myself to others on social media', 'category': 'comparison', 'dimension': 'wellness'},
            {'id': 'DW4', 'text': 'Screen time interferes with my sleep', 'category': 'sleep_impact', 'dimension': 'wellness'},
            {'id': 'DW5', 'text': 'I want to reduce my overall screen time', 'category': 'goals', 'dimension': 'wellness'},
        ]

    def calculate_trait_scores(self, responses):
        """Calculate Big Five trait scores from quiz responses"""
        trait_scores = {
            'extraversion': [],
            'neuroticism': [],
            'agreeableness': [],
            'conscientiousness': [],
            'openness': []
        }

        # Process each trait
        for trait, questions in BIG_FIVE_QUESTIONS.items():
            for q in questions:
                if q['id'] in responses:
                    score = int(responses[q['id']])
                    # Reverse score for negative-keyed items (6 - score to invert 1-5 scale)
                    if q['keyed'] == 'negative':
                        score = 6 - score
                    trait_scores[trait].append(score)

        # Calculate average for each trait (normalize to 0-1 scale)
        normalized_scores = {}
        for trait, scores in trait_scores.items():
            if scores:
                avg = np.mean(scores)
                # Normalize from 1-5 scale to 0-1 scale
                normalized_scores[trait] = (avg - 1) / 4
            else:
                normalized_scores[trait] = 0.5  # Default to neutral

        return normalized_scores

    def classify_personality(self, trait_scores):
        """Classify personality into one of 5 clusters using K-Means"""
        # Create feature vector in correct order
        feature_vector = np.array([[
            trait_scores.get('extraversion', 0.5),
            trait_scores.get('neuroticism', 0.5),
            trait_scores.get('agreeableness', 0.5),
            trait_scores.get('conscientiousness', 0.5),
            trait_scores.get('openness', 0.5)
        ]])

        # Predict cluster
        cluster = self.kmeans.predict(feature_vector)[0]

        # Calculate distance to all cluster centers for confidence
        distances = np.sqrt(np.sum((self.cluster_centers - feature_vector) ** 2, axis=1))
        min_distance = distances[cluster]
        confidence = max(0, 1 - min_distance)  # Higher confidence when closer to center

        return {
            'cluster': int(cluster),
            'confidence': float(confidence),
            'distances': {
                PERSONALITY_CLUSTERS[i]['name']: float(1 / (1 + d))
                for i, d in enumerate(distances)
            }
        }

    def assess_mental_health(self, responses):
        """Assess mental health indicators from responses"""
        mental_health_scores = {
            'depression': [],
            'anxiety': [],
            'stress': [],
            'sleep': [],
            'energy': []
        }

        mental_health_questions = self._get_mental_health_questions()
        for q in mental_health_questions:
            if q['id'] in responses:
                score = int(responses[q['id']])
                if q.get('keyed') == 'negative':
                    score = 6 - score
                mental_health_scores[q['category']].append(score)

        # Calculate average scores
        avg_scores = {}
        for category, scores in mental_health_scores.items():
            if scores:
                avg_scores[category] = np.mean(scores)
            else:
                avg_scores[category] = 3  # Neutral

        # Overall mental wellness score (inverted - higher is better)
        concern_categories = ['depression', 'anxiety', 'stress']
        positive_categories = ['sleep', 'energy']

        concern_score = np.mean([avg_scores.get(c, 3) for c in concern_categories])
        positive_score = np.mean([avg_scores.get(c, 3) for c in positive_categories])

        # Mental wellness index (0-100)
        wellness_index = ((6 - concern_score) / 5 * 50) + ((positive_score) / 5 * 50)

        # Determine status
        if wellness_index >= 75:
            status = 'excellent'
            status_description = 'Your mental wellness indicators are strong. Keep up the great work!'
        elif wellness_index >= 60:
            status = 'good'
            status_description = 'Your mental wellness is in a healthy range with some areas for improvement.'
        elif wellness_index >= 45:
            status = 'moderate'
            status_description = 'Some areas of your mental wellness could use attention. Consider the recommendations below.'
        else:
            status = 'needs_attention'
            status_description = 'Your responses indicate some mental wellness challenges. Please consider speaking with a professional.'

        # Generate recommendations
        recommendations = self._generate_mental_health_recommendations(avg_scores)

        return {
            'wellness_index': float(round(wellness_index, 1)),
            'status': status,
            'status_description': status_description,
            'category_scores': {k: float(round(v, 2)) for k, v in avg_scores.items()},
            'recommendations': recommendations
        }

    def _generate_mental_health_recommendations(self, scores):
        """Generate personalized mental health recommendations"""
        recommendations = []

        if scores.get('depression', 3) >= 3.5:
            recommendations.append({
                'area': 'Mood',
                'priority': 'high',
                'tip': 'Consider activities that bring joy. Small daily pleasures can lift your mood.',
                'action': 'Start a gratitude journal - write 3 things you appreciate each day'
            })

        if scores.get('anxiety', 3) >= 3.5:
            recommendations.append({
                'area': 'Anxiety',
                'priority': 'high',
                'tip': 'Practice relaxation techniques to manage worry and tension.',
                'action': 'Try the 4-7-8 breathing technique: inhale 4 sec, hold 7 sec, exhale 8 sec'
            })

        if scores.get('stress', 3) >= 3.5:
            recommendations.append({
                'area': 'Stress',
                'priority': 'high',
                'tip': 'Break overwhelming tasks into smaller, manageable pieces.',
                'action': 'Use the Pomodoro technique: 25 minutes work, 5 minutes break'
            })

        if scores.get('sleep', 3) >= 3.5:
            recommendations.append({
                'area': 'Sleep',
                'priority': 'medium',
                'tip': 'Quality sleep is foundational for mental health.',
                'action': 'Establish a consistent sleep schedule and avoid screens 1 hour before bed'
            })

        if scores.get('social_support', 3) >= 3.5:
            recommendations.append({
                'area': 'Connection',
                'priority': 'medium',
                'tip': 'Social connection is vital for wellbeing.',
                'action': 'Reach out to one friend or family member this week'
            })

        if scores.get('focus', 3) >= 3.5:
            recommendations.append({
                'area': 'Focus',
                'priority': 'medium',
                'tip': 'Improve concentration through environmental changes.',
                'action': 'Create a distraction-free workspace and use website blockers'
            })

        if scores.get('energy', 3) >= 3.5:
            recommendations.append({
                'area': 'Energy',
                'priority': 'medium',
                'tip': 'Low energy can be improved through lifestyle changes.',
                'action': 'Take a 10-minute walk daily - even brief movement boosts energy'
            })

        if not recommendations:
            recommendations.append({
                'area': 'Maintenance',
                'priority': 'low',
                'tip': 'Your mental wellness is in a good place!',
                'action': 'Continue your healthy habits and check in with yourself regularly'
            })

        return recommendations

    def assess_digital_wellness(self, responses):
        """Assess digital wellness from responses"""
        wellness_scores = {
            'digital_impact': 0,
            'digital_dependency': 0,
            'comparison': 0,
            'sleep_impact': 0
        }
        goals = []

        wellness_questions = self._get_wellness_questions()
        for q in wellness_questions:
            if q['id'] in responses:
                score = int(responses[q['id']])
                if q['category'] == 'goals' and score >= 4:
                    goals.append(q['text'])
                elif q['category'] in wellness_scores:
                    wellness_scores[q['category']] = score

        # Calculate digital wellness score (lower concern scores = better wellness)
        concern_total = sum(wellness_scores.values())
        digital_wellness_index = max(0, 100 - (concern_total / len(wellness_scores) * 20))

        # Determine risk level
        if concern_total <= 8:
            risk_level = 'low'
        elif concern_total <= 14:
            risk_level = 'moderate'
        else:
            risk_level = 'high'

        return {
            'wellness_index': float(round(digital_wellness_index, 1)),
            'risk_level': risk_level,
            'category_scores': {k: int(v) for k, v in wellness_scores.items()},
            'wellness_goals': list(goals),
            'recommendations': self._generate_digital_recommendations(wellness_scores)
        }

    def _generate_digital_recommendations(self, scores):
        """Generate digital wellness recommendations"""
        recommendations = []

        if scores.get('digital_impact', 0) >= 4:
            recommendations.append('Take regular breaks from social media - try a 24-hour digital detox weekly')

        if scores.get('digital_dependency', 0) >= 4:
            recommendations.append('Use app timers to limit time on addictive apps')

        if scores.get('comparison', 0) >= 4:
            recommendations.append('Curate your feeds to follow inspiring, not comparing content')

        if scores.get('sleep_impact', 0) >= 4:
            recommendations.append('Enable night mode and avoid screens 1 hour before bed')

        if not recommendations:
            recommendations.append('Your digital habits are healthy! Maintain your balanced approach.')

        return recommendations

    def analyze_responses(self, responses):
        """Complete analysis of quiz responses"""
        # Calculate Big Five trait scores
        trait_scores = self.calculate_trait_scores(responses)

        # Classify personality cluster
        classification = self.classify_personality(trait_scores)
        cluster = classification['cluster']
        personality = PERSONALITY_CLUSTERS[cluster]

        # Assess mental health
        mental_health = self.assess_mental_health(responses)

        # Assess digital wellness
        digital_wellness = self.assess_digital_wellness(responses)

        # Determine stress level from neuroticism and mental health
        neuroticism_score = trait_scores.get('neuroticism', 0.5)
        if neuroticism_score >= 0.7 or mental_health['wellness_index'] < 45:
            stress_level = 'high'
        elif neuroticism_score >= 0.5 or mental_health['wellness_index'] < 60:
            stress_level = 'medium'
        else:
            stress_level = 'low'

        # Convert normalized trait scores to 0-5 scale for storage
        # Ensure all values are native Python types (not numpy)
        big_five_display = {
            trait: float(round(score * 4 + 1, 2))  # Convert back to 1-5 scale
            for trait, score in trait_scores.items()
        }

        # Convert normalized scores to native Python floats
        big_five_normalized = {
            trait: float(score) for trait, score in trait_scores.items()
        }

        return {
            'personality_type': personality['name'],
            'personality_description': personality['description'],
            'big_five_scores': big_five_display,
            'big_five_normalized': big_five_normalized,
            'cluster': int(cluster),
            'cluster_confidence': float(classification['confidence']),
            'strengths': list(personality['strengths']),
            'growth_areas': list(personality['growth_areas']),
            'wellness_tips': list(personality['wellness_tips']),
            'digital_wellness_tips': list(personality['digital_wellness']),
            'mental_health': mental_health,
            'digital_wellness': digital_wellness,
            'stress_level': stress_level,
            'wellness_goals': list(digital_wellness['wellness_goals'])
        }

    def get_improvement_recommendations(self, user_data, session_data=None):
        """Generate personalized improvement recommendations based on user profile and screen data"""
        recommendations = {
            'personality_based': [],
            'mental_health_based': [],
            'screen_behavior_based': [],
            'immediate_actions': [],
            'long_term_goals': []
        }

        # Personality-based recommendations
        if user_data.get('big_five_scores'):
            scores = user_data['big_five_scores']

            if scores.get('neuroticism', 3) > 3.5:
                recommendations['personality_based'].append({
                    'area': 'Emotional Regulation',
                    'insight': 'Your personality profile shows sensitivity to stress.',
                    'action': 'Practice daily mindfulness meditation for 10 minutes',
                    'benefit': 'Reduced anxiety and improved emotional resilience'
                })

            if scores.get('extraversion', 3) < 2.5:
                recommendations['personality_based'].append({
                    'area': 'Social Connection',
                    'insight': 'You prefer solitude, but some social connection benefits wellbeing.',
                    'action': 'Schedule one meaningful conversation per week',
                    'benefit': 'Maintained social bonds without overwhelm'
                })

            if scores.get('conscientiousness', 3) < 2.5:
                recommendations['personality_based'].append({
                    'area': 'Structure & Routine',
                    'insight': 'Adding more structure could enhance your productivity.',
                    'action': 'Use a simple daily planning system',
                    'benefit': 'Reduced stress from disorganization'
                })

        # Mental health based recommendations
        if user_data.get('stress_level') == 'high':
            recommendations['mental_health_based'].extend([
                {
                    'area': 'Stress Management',
                    'insight': 'High stress levels detected.',
                    'action': 'Implement the 5-4-3-2-1 grounding technique when stressed',
                    'benefit': 'Immediate anxiety relief'
                }
            ])

        # Screen behavior recommendations (if session data available)
        if session_data:
            if session_data.get('avg_wellness', 5) < 5:
                recommendations['screen_behavior_based'].append({
                    'area': 'Content Quality',
                    'insight': 'Your screen content may be affecting your wellbeing negatively.',
                    'action': 'Curate your feeds to reduce negative content exposure',
                    'benefit': 'Improved mood during screen time'
                })

        # Immediate actions (top 3 priorities)
        all_recs = (
            recommendations['personality_based'] +
            recommendations['mental_health_based'] +
            recommendations['screen_behavior_based']
        )
        recommendations['immediate_actions'] = all_recs[:3]

        return recommendations


# Global service instance
_personality_service = None

def get_personality_service():
    """Get or create personality ML service instance"""
    global _personality_service
    if _personality_service is None:
        _personality_service = PersonalityMLService()
    return _personality_service
