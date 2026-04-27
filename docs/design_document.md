# Design Details

**Project Structure**

Capstone-Discord-eSportsBot-S26-T2/

├── common/ # Shared services, API logic, caching, DB utilities, tasks

│ ├── cached_details.py

│ ├── common_scripts.py

│ ├── database_connection.py

│ ├── ollama_seeding.py

│ ├── riot_api.py

│ ├── tasks.py

│ └── tournament_runner.py

├── config/ # Configuration and environment variable loading

│ └── settings.py

├── controller/ # Discord bot commands and business logic

│ ├── admin_controller.py

│ ├── api.py

│ ├── callofduty_matchmaking.py

│ ├── checkin_controller.py

│ ├── events.py

│ ├── export_import.py

│ ├── giveaway_cog.py

│ ├── league_genetic_match_making.py

│ ├── league_match_making.py

│ ├── league_matchmaking_controller.py

│ ├── marvelrivals_matchmaking.py

│ ├── match_results_controller.py

│ ├── mvp_voting_controller.py

│ ├── openAi_teamup.py

│ ├── player_commands.py

│ ├── player_management.py

│ ├── player_signup.py

│ ├── seeding_controller.py

│ ├── signup_shared_logic.py

│ ├── stats_controller.py

│ ├── team_display_controller.py

│ ├── team_swap_controller.py

│ ├── teams_controller.py

│ └── tier_management.py

├── docs/ # Internal project documentation

├── integration_testing/ # Integration tests

├── unit_testing/ # Unit tests

├── model/ # Database models and state objects

├── view/ # Discord UI and visual output components

├── .env.template # Environment variable template

├── Dockerfile # Docker build definition

├── README.md # Main repository documentation

├── google_export.md # Google Sheets setup notes

├── requirements.txt # Python dependencies

├── tournament.py # Main application entry point

├── tournament_dbc # SQLite database file

└── web_server.py # Optional web server / viewer

# **System Architecture**

The bot follows a Model-View-Controller (MVC) architecture, separating concerns into discrete layers that can be developed and tested independently.

## **Model Layer**

The model/ directory contains the database schema and data persistence classes. These classes manage player data, game records, check-in state, MVP votes, and giveaway state.

## **View Layer**

The view/ directory contains Discord UI logic and presentation utilities, including buttons, dropdowns, embeds, confirmation views, MVP vote interfaces, and announcement image generation.

## **Controller Layer**

The controller/ directory contains the core command logic. Each feature area is separated into its own cog or controller file, which improves maintainability and allows the bot to scale as features are added.

## **Common Services Layer**

The common/ directory acts as a shared service layer. It includes Riot API calls, database connection helpers, scheduled tasks, caching utilities, seeding logic, and tournament execution logic.

## **Configuration Layer**

The config/settings.py file loads all environment variables, channel settings, API keys, logging configuration, and runtime constants from the .env file at startup.

**Main Modules and Responsibilities**

## **tournament.py**

This is the main entry point of the application. On startup it:

- Configures Discord intents
- Creates the bot client
- Initializes the SQLite database and creates required tables
- Loads all controller cogs dynamically from the controller/ directory
- Syncs slash commands to configured guilds
- Handles global command errors
- Starts the bot runtime

## **config/settings.py**

Centralizes all environment-driven configuration, including:

- Discord token and guild ID
- Database name
- Riot API key
- Google Sheets settings
- Channel configuration
- Logging behavior
- Tier update thresholds

## **common/database_connection.py**

Provides shared access to the application database and supports data operations across all controllers.

## **common/riot_api.py**

Handles all Riot API interactions, including account validation, player data lookup, and rank data retrieval.

## **common/tasks.py**

Implements background scheduled tasks. The primary purpose is automatic player tier updates, governed by environment-configured thresholds:

- MIN_GAME_PLAYED
- MIN_GAME_WINRATE
- MAX_GAME_LOST

## **common/tournament_runner.py**

Supports overall tournament execution flow and orchestration logic shared across controllers.

## **web_server.py**

Provides a lightweight server component for viewing or interfacing with tournament data outside the Discord bot context.

**Bot Initialization Flow**

When tournament.py is executed, the bot follows this startup sequence:

- Discord intents are configured.
- The bot client is created.
- The SQLite database is initialized; all required tables are created if they do not already exist.
- The bot connects to Discord.
- Channels are created or retrieved from cache based on CHANNEL_CONFIG.
- All controller cog files in the controller/ directory are loaded automatically via dynamic discovery.
- Slash commands are synced to the configured guilds.
- The bot is marked as fully initialized and ready for use.

This dynamic loading approach means new feature modules can be added by placing a controller file in the controller/ directory without modifying tournament.py.

**Database Design**

The project uses SQLite as its persistence layer. SQLite is well-suited for the single-server, low-concurrency context of a university esports club. A migration to PostgreSQL would be recommended if the system were scaled to multi-server or high-traffic deployments.

## **Core Database Objects**

### **Player**

Stores player identity and account data: Discord user ID, in-game name, game tag, and administrator status.

### **Game Table (For each game, currently League of Legends, Marvel Rivals, and Call of Duty)**

Stores game-specific statistics and preferences: current tier, rank and division, preferred roles, win and loss counts, win rate, and manual tier override flag.

### **Matches**

Stores match history and participation data: match ID, team assignments, match outcomes, date played, and per-player participation records.

### **MVP Votes**

Stores voting records related to post-match MVP selection, persisted to the database so history remains queryable after Discord messages are deleted.

### **Player Game Info**

Stores additional per-game detail data beyond the core Game record.

### **Check-in and Supporting State**

Additional state is tracked through checkin_model.py, button_state.py, and giveaway_model.py.

## **Database Initialization**

At startup, the application automatically creates all required tables if they do not exist, including: the player table, game table, matches table, match results table, MVP votes table, player game info table, and the Call of Duty player table.