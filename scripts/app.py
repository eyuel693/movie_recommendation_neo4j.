import sys
import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash
from recommender import RecommendationEngine
from new_user_recommend import Neo4jRecommender
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ensure log directory exists
os.makedirs('outputs/logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    filename='outputs/logs/flask_app.log',
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler('outputs/logs/flask_app.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates')
)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")

# Neo4j credentials
neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
neo4j_user = os.getenv("NEO4J_USER", "neo4j")
neo4j_password = os.getenv("NEO4J_PASSWORD", "password")

# Global instances
rec_engine = None
new_user_rec = None

def init_recommenders():
    global rec_engine, new_user_rec
    try:
        rec_engine = RecommendationEngine()
        new_user_rec = Neo4jRecommender(neo4j_uri, neo4j_user, neo4j_password)
        logger.info("Neo4j connection established successfully")
    except Exception as e:
        logger.error(f"Failed to connect to Neo4j: {e}")
        raise

# ------------------- Helper -------------------
def get_dropdown_options():
    try:
        with rec_engine.driver.session() as session:
            genres = session.run("MATCH (g:Genre) RETURN g.name AS name ORDER BY g.name")
            actors = session.run("MATCH (a:Actor) RETURN a.name AS name ORDER BY a.name LIMIT 100")
            directors = session.run("MATCH (d:Director) RETURN d.name AS name ORDER BY d.name LIMIT 100")
            options = {
                'genres': [dict(r)['name'] for r in genres],
                'actors': [dict(r)['name'] for r in actors],
                'directors': [dict(r)['name'] for r in directors]
            }
            logger.debug(f"Dropdown options: {options}")
            return options
    except Exception as e:
        logger.error(f"Error fetching dropdown options: {e}")
        flash(f"Database error: {str(e)}", 'error')
        return {'genres': [], 'actors': [], 'directors': []}

# ------------------- Routes -------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search_user', methods=['POST'])
def search_user():
    try:
        user_id = request.form.get('user_id', type=int)
        if not user_id:
            flash("User ID is required", "error")
            return redirect(url_for('index'))
        
        if not rec_engine.check_user_exists(user_id):
            flash(f"User {user_id} not found. Please create a new user.", "error")
            return redirect(url_for('index'))
        
        logger.info(f"User {user_id} found, redirecting to recommendations")
        return redirect(url_for('recommendations', user_id=user_id))
    except Exception as e:
        logger.error(f"Error searching for user: {e}")
        flash(f"Error: {str(e)}", "error")
        return redirect(url_for('index'))

@app.route('/user', methods=['GET', 'POST'])
def user():
    if request.method == 'POST':
        try:
            user_id = request.form.get('user_id', type=int)
            if not user_id:
                raise ValueError("User ID is required")
            name = request.form.get('name') or None
            genres = request.form.getlist('genres')
            actors = request.form.getlist('actors')
            directors = request.form.getlist('directors')

            new_user_rec.create_user(user_id, name)
            new_user_rec.add_interests(user_id, genres if genres else None, actors if actors else None, directors if directors else None)
            logger.info(f"Created user {user_id} with interests: genres={genres}, actors={actors}, directors={directors}")

            flash('User created successfully!', 'success')
            return redirect(url_for('recommendations', user_id=user_id, strategy='interest'))
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            flash(f"Error: {str(e)}", 'error')

    options = get_dropdown_options()
    return render_template('user.html', options=options)

@app.route('/recommendations/<int:user_id>', methods=['GET', 'POST'])
def recommendations(user_id):
    default_strategy = request.args.get('strategy', 'hybrid') if request.method == 'GET' else request.form.get('strategy', 'hybrid')
    strategy = request.form.get('strategy', default_strategy) if request.method == 'POST' else default_strategy

    strategy_files = {
        "collaborative": "cypher/collaborative_filtering.cypher",
        "content": "cypher/content_based.cypher",
        "hybrid": "cypher/Hybrid_Recommendation.cypher",
        "genre": "cypher/Genre_Based.cypher",
        "interest": None
    }

    try:
        if not rec_engine.check_user_exists(user_id):
            flash(f"User {user_id} not found.", "error")
            return redirect(url_for('index'))

        user_data = rec_engine.validate_user_data(user_id)
        if user_data.get("rated_shows", 0) == 0 and strategy != "interest":
            flash(f"User {user_id} has no rated shows. Try Interest-Based strategy or add ratings.", "warning")

        if strategy == 'interest':
            recs = new_user_rec.recommend_from_interests(user_id, limit=10)
        else:
            recs = rec_engine.get_recommendations(strategy_files[strategy], user_id, limit=10)

        logger.debug(f"Recommendations for user {user_id} (strategy: {strategy}): {recs}")
        if not recs:
            flash(f"No recommendations found for {strategy.replace('_', ' ').title()} strategy. Try another strategy or add more data.", "warning")
        return render_template(
            'recommendations.html',
            user_id=user_id,
            recommendations=recs,
            strategy=strategy
        )
    except Exception as e:
        logger.error(f"Error generating recommendations for user {user_id} (strategy: {strategy}): {e}")
        flash(f"Error generating recommendations: {str(e)}", 'error')
        return render_template('recommendations.html', user_id=user_id, recommendations=[], strategy=strategy)

if __name__ == "__main__":
    init_recommenders()
    try:
        app.run(debug=True, host="0.0.0.0", port=5000)
    finally:
        if rec_engine:
            rec_engine.close()
        if new_user_rec:
            new_user_rec.close()
        logger.info("Neo4j connections closed on shutdown")