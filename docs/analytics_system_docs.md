# Module Documentation: analytics_system
The `analytics_system` is the high-level API of the project. It converts numerical predictions from the ML pipeline into strategic insights.

## Components
- **chatbot.py**: Natural Language Interface. Uses spaCy to extract players/maps/agents and routes queries.
- **analysis.py**: The core intelligence. Handles team auditing, role distribution, and prescriptive recommendations.
- **prediction.py**: A bridge between raw ML models and the analysis system.
- **utils.py**: Data loading and mapping utilities.

## Key Workflows
- **Match Query**: `process_match_query()` $\rightarrow$ Analyzes both teams, predicts win prob, suggests counters, and optimizes composition.
- **Player Query**: `process_player_query()` $\rightarrow$ Generates a full profile including strengths, weaknesses, and agent recommendations.
