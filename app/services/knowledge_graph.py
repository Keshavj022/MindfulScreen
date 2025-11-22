import networkx as nx
from app import db
from app.models import User, KnowledgeGraph, ScreenSession, FrameAnalysis
from sqlalchemy import func

class KnowledgeGraphService:
    def create_or_update_graph(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return None

        G = nx.DiGraph()

        G.add_node('User', type='person', label=user.name)

        if user.age:
            age_group = 'Young Adult' if user.age < 30 else 'Adult' if user.age < 50 else 'Senior'
            G.add_node(age_group, type='demographic')
            G.add_edge('User', age_group, relationship='belongs_to')

        if user.gender:
            G.add_node(user.gender, type='demographic')
            G.add_edge('User', user.gender, relationship='identified_as')

        if user.occupation:
            G.add_node(user.occupation, type='occupation')
            G.add_edge('User', user.occupation, relationship='works_as')

        if user.location:
            G.add_node(user.location, type='location')
            G.add_edge('User', user.location, relationship='lives_in')

        if user.personality_type:
            G.add_node(user.personality_type, type='personality')
            G.add_edge('User', user.personality_type, relationship='has_personality')

        if user.big_five_scores:
            for trait, score in user.big_five_scores.items():
                trait_level = 'High' if score > 3.5 else 'Low'
                trait_node = f"{trait.capitalize()} ({trait_level})"
                G.add_node(trait_node, type='trait', score=score)
                G.add_edge(user.personality_type or 'User', trait_node, relationship='exhibits')

        if user.stress_level:
            stress_node = f"Stress Level: {user.stress_level.capitalize()}"
            G.add_node(stress_node, type='wellness')
            G.add_edge('User', stress_node, relationship='experiences')

        sessions = ScreenSession.query.filter_by(user_id=user_id, status='completed').all()

        app_usage = {}
        content_types = {}
        total_wellness = 0
        total_productivity = 0

        for session in sessions:
            if session.wellness_score:
                total_wellness += session.wellness_score
            if session.productivity_score:
                total_productivity += session.productivity_score

            if session.app_usage:
                for app, count in session.app_usage.items():
                    app_usage[app] = app_usage.get(app, 0) + count

            if session.content_categories:
                for cat, count in session.content_categories.items():
                    content_types[cat] = content_types.get(cat, 0) + count

        if sessions:
            avg_wellness = total_wellness / len(sessions)
            avg_productivity = total_productivity / len(sessions)

            wellness_node = f"Avg Wellness: {avg_wellness:.1f}/10"
            G.add_node(wellness_node, type='metric', value=avg_wellness)
            G.add_edge('User', wellness_node, relationship='has_metric')

            productivity_node = f"Avg Productivity: {avg_productivity:.1f}/10"
            G.add_node(productivity_node, type='metric', value=avg_productivity)
            G.add_edge('User', productivity_node, relationship='has_metric')

        for app, count in sorted(app_usage.items(), key=lambda x: x[1], reverse=True)[:5]:
            G.add_node(app, type='app', usage_count=count)
            G.add_edge('User', app, relationship='uses')

        for content, count in sorted(content_types.items(), key=lambda x: x[1], reverse=True)[:5]:
            content_node = f"{content.replace('_', ' ').title()} Content"
            G.add_node(content_node, type='content', count=count)
            G.add_edge('User', content_node, relationship='consumes')

        if user.wellness_goals:
            for goal in user.wellness_goals[:3]:
                goal_short = goal[:50] + '...' if len(goal) > 50 else goal
                G.add_node(goal_short, type='goal')
                G.add_edge('User', goal_short, relationship='pursues')

        graph_data = {
            'nodes': [
                {
                    'id': node,
                    'label': node,
                    'type': G.nodes[node].get('type', 'unknown'),
                    **{k: v for k, v in G.nodes[node].items() if k != 'type'}
                }
                for node in G.nodes()
            ],
            'edges': [
                {
                    'source': edge[0],
                    'target': edge[1],
                    'relationship': G.edges[edge].get('relationship', 'connected_to')
                }
                for edge in G.edges()
            ]
        }

        kg = KnowledgeGraph.query.filter_by(user_id=user_id).first()
        if kg:
            kg.graph_data = graph_data
        else:
            kg = KnowledgeGraph(user_id=user_id, graph_data=graph_data)
            db.session.add(kg)

        db.session.commit()

        return graph_data

    def get_user_graph(self, user_id):
        kg = KnowledgeGraph.query.filter_by(user_id=user_id).first()
        if kg:
            return kg.graph_data
        return self.create_or_update_graph(user_id)

    def update_user_graph(self, user_id):
        return self.create_or_update_graph(user_id)
