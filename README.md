
# Movie Recommendation System with Neo4j & Flask

An end-to-end **Movie Recommendation Engine** built using **Neo4j Graph Database** and **Flask Web Framework**.
This system leverages both **collaborative filtering** and **content-based filtering**, combined with a **hybrid recommendation strategy**, to deliver personalized movie suggestions for users.

It also supports **new user onboarding** where recommendations are generated based on selected **genres, actors, and directors**.

---

## Features

**User Management**

* Search for existing users.
* Create new users with custom preferences (genres, actors, directors).

**Recommendation Strategies**

* **Collaborative Filtering** → Based on similar users’ preferences.
* **Content-Based Filtering** → Based on user’s watched/rated movies.
* **Genre-Based Recommendations** → Personalized by favorite genres.
* **Hybrid Recommendations** → Combination of collaborative + content.
* **Interest-Based Recommendations** → For new users with no history.

**Neo4j Graph Database Integration**

* Stores movies, genres, actors, directors, and ratings.
* Graph queries written in **Cypher** for fast recommendations.

**Web UI (Flask + HTML/CSS/JS)**

* User-friendly interface.
* Drop-down menus for selecting preferences.
* Dynamic recommendation display.

**Logging & Monitoring**

* Full logging system (`outputs/logs/flask_app.log`) for debugging and tracking.

---

## Project Structure

```
├── app/
│   ├── app.py                
│   ├── recommender.py        
│   ├── new_user_recommend.py 
│   ├── cypher/               
│   │   ├── collaborative_filtering.cypher
│   │   ├── content_based.cypher
│   │   ├── hybrid_recommendation.cypher
│   │   ├── genre_based.cypher
│   │   └── ...
│   ├── templates/            
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── user.html
│   │   └── recommendations.html
│   └── static/               
│
├── outputs/
│   └── logs/                 
│
├── .env                      
├── requirements.txt          
├── README.md                 
└── setup_database.py         
```

---

## Installation & Setup

### 1 Clone the repository

```bash
git clone https://github.com/your-username/movie-recommender-neo4j.git
cd movie-recommender-neo4j/app
```

### 2 Create virtual environment & install dependencies

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

pip install -r requirements.txt
```

### 3 Configure environment variables (`.env`)

Create a `.env` file in the project root:

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=yourpassword
FLASK_SECRET_KEY=supersecretkey
```

### 4 Setup Neo4j Database

Run the setup script to load movies, genres, actors, directors, and ratings:

```bash
pytho test_neo4j.py
```

### 5 Start Flask App

```bash
python scripts/app.py
```

The app will run on:
**[http://localhost:5000](http://localhost:5000)**

---