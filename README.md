**🏆 KSU Esports Tournament Bot**

_Technical Documentation - Capstone Project, Spring 2026_

# **Overview**

A comprehensive Discord bot built to support competitive gaming operations for Kennesaw State University Esports. The bot is designed primarily for League of Legends tournament management, while also including early or extended support for Call of Duty, team utilities, seeding workflows, Google Sheets synchronization, and administrative tournament automation.

The system integrates Discord, SQLite, Riot Games API, Google Sheets, Docker, and optional AI-assisted seeding and matchmaking logic to automate tournament organization, player registration, skill tracking, matchmaking, results reporting, MVP voting, and team management.

This document provides a full technical reference for the KSU Esports Tournament Bot, covering architecture, features, commands, workflows, configuration, and deployment.

## **Setup Instructions**

## **1\. Clone the Repository**

git clone <https://github.com/AustinWG47/Capstone-Discord-eSportsBot-S26-T2.git>

cd Capstone-Discord-eSportsBot-S26-T2

## **2\. Create the Environment File**

macOS / Linux:

cp .env.template .env

Windows:

copy .env.template .env

Fill in all required values before proceeding.

## **3\. Create and Activate a Virtual Environment**

python -m venv venv

Windows:

venv\\Scripts\\activate

macOS / Linux:

source venv/bin/activate

## **4\. Install Dependencies**

pip install -r requirements.txt

## **5\. Configure Discord Bot Access**

In the Discord Developer Portal: create a bot application, copy the bot token into .env, enable required gateway intents (Message Content, Server Members), and invite the bot to the server with appropriate permissions.

## **6\. Configure the Riot API**

Obtain a Riot API development key and add it to the .env file under both API_KEY and RIOT_API_KEY.

## **7\. Configure Ollama (Optional for AI-assisted seeding)**

**Step 1 - Install Ollama**

**Download Ollama:**

<https://ollama.com/download>

- Install like a normal application
- Restart your terminal after installation

**Step 2 - Start Ollama**

Open a terminal / PowerShell and run:

ollama serve

You should see something like:

Listening on [http://localhost:11434](http://localhost:11434/)

This means Ollama is running correctly

**Step 3 - Download the AI Model**

Run:

ollama run mistral

- This will download the **Mistral model** (first time only)
- After first time download this will run the **Mistral model**

**Step 4 - Keep Ollama Running**

Make sure this is running **before starting the Discord bot**:

ollama serve

**Step 5 - Verify It Works**

Open a browser and go to:

[http://localhost:11434](http://localhost:11434/)

If Ollama is running, you should NOT see a connection error.

**Step 6 - Run Discord Bot**

Now start the Discord bot:

python tournament.py

## **8\. Configure Google Sheets (Optional)**

Add your Google Sheet ID and service account credentials path to .env to enable the import/export feature.

## **9\. Run the Bot**

python tournament.py

On successful startup, the bot logs in, loads all controller cogs, syncs slash commands, and begins accepting input in the configured server.

**Deployment**

## **Local Deployment**

The simplest deployment path is running the application directly with Python after configuring the .env file.

## **Docker Deployment**

The repository includes a Dockerfile and dedicated Docker documentation in docs/docker_deployment.md.

### **Build**

docker build -t ksu-esports-bot .

### **Run**

docker run --env-file .env ksu-esports-bot

**Features**

## **Core Tournament Features**

- Discord slash command-driven tournament workflow
- Team creation and team management commands
- Player registration linked to Riot account information
- Matchmaking and team balancing for League of Legends
- Sequential match tracking and match result recording
- Team display and team announcement tools
- MVP voting workflow after match completion
- Toxicity tracking for player behavior monitoring
- Google Sheets import and export for player records
- Expanded SQLite data persistence and match tracking
- Tournament seeding utilities
- Optional Docker deployment support
- Automated background tier update task (Riot API)

## **Advanced Features**

- Genetic algorithm-based matchmaking for improved team balance
- Role preference-aware team generation
- Discord UI components including buttons, dropdowns, and interactive views
- Image-based team announcement generation
- Multi-controller modular architecture
- Unit and integration test coverage

## **Extended / Experimental Modules**

- Call of Duty matchmaking support
- Marvel Rivals matchmaking controller present in project structure
- OpenAI and Ollama integration for AI-assisted team formation and seeding
- Real-time background API and player data refresh workflows

**Quick Start**

The following is the high-level game day sequence. Full setup and deployment instructions are covered in the Setup Instructions section.

- Register players using /register.
- Run matchmaking with /run_league_matchmaking.
- Record match outcomes with /record_match_result or /record_match_results.
- Start MVP voting with /start_mvp_voting after each match.
- Export or review player data as needed with /export_players or /stats.

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

# **Command Reference**

All commands are Discord slash commands unless otherwise noted. Commands are organized by functional area.

## **Player Registration and Basic Player Features**

| **Command**  | **Purpose**                                                            |
| ------------ | ---------------------------------------------------------------------- |
| /register    | Registers a user as a player in the tournament system.                 |
| /stats       | Displays detailed player stats and rank information from the database. |
| /team_create | Creates a team and invites specified users.                            |
| /team_leave  | Allows a user to leave their current team.                             |

## **Player Management and Admin Review**

| **Command**   | **Purpose**                                                         |
| ------------- | ------------------------------------------------------------------- |
| /list_players | Lists all registered players and their details.                     |
| /toxicity     | Adds a toxicity point to a specified league of legends player.      |
| /get_toxicity | Displays the current toxicity total for a league of legends player. |

## **Check-In and Matchmaking**

| **Command**                       | **Purpose**                                                             |
| --------------------------------- | ----------------------------------------------------------------------- |
| /simulate_checkins                | Simulates player check-ins for league games testing or admin workflows. |
| /run_league_matchmaking           | Runs League of Legends matchmaking for checked-in players.              |
| /insert_codtest_players           | Inserts test players for Call of Duty functionality testing.            |
| /run_cod_matchmaking              | Runs Call of Duty matchmaking for registered players.                   |
| /insert_marvelrivals_test_players | Inserts test players for Marvel Rivals functionality testing.           |
| /run_marvelrivals_matchmaking     | Runs Marvel Rivals matchmaking for registered players.                  |

## **Match Results and MVP Voting**

| **Command**            | **Purpose**                                       |
| ---------------------- | ------------------------------------------------- |
| /record_match_result   | Records the outcome of a single match.            |
| /start_mvp_voting      | Starts MVP voting for a selected match.           |
| /end_mvp_voting        | Ends an active MVP voting session early.          |
| /vote_mvp              | Allows a player to cast their MVP vote.           |
| /view_mvp_results      | Shows MVP vote results for a selected match.      |
| /list_active_mvp_votes | Lists all currently open voting sessions.         |
| /view_player_mvps      | Displays the total MVP awards earned by a player. |

## **Google Sheets Integration**

| **Command**     | **Purpose**                                                |
| --------------- | ---------------------------------------------------------- |
| /export_players | Exports all player data to a configured Google Sheet.      |
| /import_players | Imports player data from a Google Sheet into the database. |

## **Seeding and Tournament Start**

| **Command**            | **Purpose**                                 |
| ---------------------- | ------------------------------------------- |
| /seed_demo             | Runs the seeding algorithm using demo data. |
| /seed_from_matchmaking | Builds seeding from matchmaking output.     |

## **Giveaway Command**

The \$giveaway command is the only prefix-style command in the codebase. It accepts a prize description and winner count as parameters. This inconsistency with the slash command interface is a known limitation and is a candidate for future standardization.

| **Command**                      | **Purpose**                                                                |
| -------------------------------- | -------------------------------------------------------------------------- |
| \$giveaway (prize, # of winners) | Runs a giveaway. Accepts prize description and winner count as parameters. |

**Matchmaking System**

The matchmaking system is one of the project's primary technical contributions. It goes beyond simple rank sorting to produce genuinely balanced teams.

## **League Matchmaking**

League of Legends matchmaking is handled across three files: league_matchmaking_controller.py, league_match_making.py, and league_genetic_match_making.py. The system supports:

- Role-aware team balancing
- Player skill tier consideration
- Sit-out logic when total player counts do not divide evenly
- Match ID generation and tracking
- Result storage for future reporting

## **Genetic Algorithm Matchmaking**

The genetic algorithm module searches across a large space of possible team compositions to find the most balanced outcome. It evaluates compositions using a fitness function that considers:

- Player tier and effective skill level
- Role preference satisfaction
- Overall team balance
- Relative performance and win rate
- Manual tier overrides set by administrators

This approach is significantly more sophisticated than greedy or round-robin assignment and represents a meaningful algorithmic contribution to the project.

## **Multi-Match Support**

The system tracks multiple simultaneous matches using unique match IDs. This allows administrators to independently display, announce, record results for, and start MVP voting on each match without interference.

## **Marvel Rivals Matchmaking & Call of Duty Matchmaking**

These matchmaking systems use a snaking algorithm that ensures the 'value' of each team is as close to fair as possible depending on the selection of sample size.

Marvel Rivals is based on the Tier & Rank of each player. A value is assigned to each player based on those factors. Call of Duty assigns the value of the player equal to their overall KDA.

Once values are assigned, the first team will get the best player, then the next team will pick the next best players until their value is equal or higher. This then repeats until both teams are filled.

# **Check-In Workflow**

The game day check-in process is designed to streamline match formation before matchmaking begins.

## **General Flow**

- Players register with the Discord UI and select their stats/ranks.
- If the pool is oversized, volunteer sit-out logic is applied.
- Matchmaking is run on the finalized player pool.
- Teams are generated, stored, and displayed or announced.
- Match results are recorded after play.
- MVP voting begins automatically upon match completion.

This gives the bot a complete tournament or matchmaking lifecycle rather than a set of isolated commands.

# **MVP Voting System**

The MVP system adds a post-match engagement feature to the full tournament flow.

## **MVP Features**

- Start voting for a specific match with /start_mvp_voting
- End voting manually if needed with /end_mvp_voting
- Allow players to vote interactively through Discord UI
- View vote results with /view_mvp_results
- Track cumulative MVP counts per player with /view_player_mvps
- List all active voting sessions with /list_active_mvp_votes

Vote records are stored persistently in the database, meaning MVP history can be reviewed at any time even after the Discord messages from the voting session are gone.

# **Toxicity Tracking System**

The repository includes a dedicated toxicity documentation file and command support in player_management.py. This subsystem allows administrators to track negative player behavior over time.

## **Capabilities**

- Increment toxicity points for a player using /toxicity
- View current toxicity totals using /get_toxicity
- Integrate behavior data into the broader player management model

This is useful for community moderation and ensuring fair tournament administration across sessions.

**Google Sheets Integration**

The project supports bidirectional synchronization between the bot's SQLite database and a configured Google Sheet.

## **Export**

/export_players exports all player information to a Google Sheet, enabling bulk editing and external record-keeping outside Discord.

## **Import**

/import_players imports spreadsheet data back into the SQLite database, allowing player records edited externally to be synced back into the bot.

## **Required Configuration**

- GOOGLE_SHEET_ID
- CELL_RANGE
- Path to the service account credentials JSON file

Supporting documentation is available in google_export.md and docs/export_import.md.

# **AI and Seeding Features**

The project includes AI-assisted and seeding-related modules:

- controller/openAi_teamup.py - OpenAI-assisted team formation
- common/ollama_seeding.py - Ollama-based experimental seeding
- controller/seeding_controller.py - Seeding command interface

These components demonstrate the system's extensibility and research potential, moving beyond basic automation into smarter bracket generation and AI-assisted tournament organization.

# **Multi-Game Support**

Although the bot is primarily centered on League of Legends, the repository includes support or groundwork for additional titles:

- League of Legends - Full support across registration, matchmaking, check-in, results, and voting
- Call of Duty - Matchmaking support with dedicated test player tooling
- Marvel Rivals - Matchmaking controller scaffold present; in early development

This means the architecture is not locked to a single game and can be expanded into a broader esports management platform over time.

**Environment Configuration**

All sensitive values and deployment parameters are stored in a .env file loaded at startup. The .env.template file in the repository root provides a complete reference. Key variables include:

DISCORD_APITOKEN=your_discord_bot_token_here

DISCORD_GUILD=your_discord_server_id_here

DATABASE_NAME=tournament.db

TOURNAMENT_CH=tournament_general

FEEDBACK_CH=feedback_channel

CHANNEL_PLAYER=t_announcement

PRIVATE_CH=admin_channel

API_KEY=your_riot_api_key_here

RIOT_API_KEY=your_riot_api_key_here

STOP_API_TASK=false

START_API_TASK=true

OPEN_AI_KEY=your_openai_api_key_here

prompt=your_openai_prompt_for_matchmaking

GOOGLE_SHEET_ID=your_google_sheet_id_here

CELL_RANGE=Sheet1

Using environment variables prevents sensitive credentials from being committed to the repository and makes deployment consistent across local, testing, and production environments.

## **GitHub Actions and Docker Hub**

The project supports automated Docker image builds and pushes to Docker Hub via GitHub Actions. This improves deployment repeatability and demonstrates familiarity with modern DevOps practices.

**Testing**

The project contains both unit tests and integration tests, demonstrating mature software engineering practices beyond feature development alone.

## **Unit Testing (unit_testing/)**

Unit tests cover the following areas:

- API behavior and response handling
- Individual command logic
- Database functions
- Event handling
- Matchmaking algorithms
- Role assignment logic
- Bot initialization
- Background task behavior

## **Integration Testing (integration_testing/)**

Integration tests validate broader application behavior, including end-to-end tournament flow scenarios. These tests confirm that the bot's components work correctly in combination, not just in isolation.

## **Significance**

Having both unit and integration tests demonstrates that the project applied real software engineering discipline. Test coverage supports regression protection and is a strong indicator of project maturity.

**Documentation Map**

The repository contains a comprehensive set of supporting documents for setup, deployment, and feature-specific workflows:

- docs/design_document.md - System design and architectural decisions
- docs/setup_guide.md - Detailed environment and configuration setup
- docs/game_day_guide.md - Step-by-step operations guide for tournament days
- docs/export_import.md - Google Sheets integration reference
- docs/docker_deployment.md - Docker build and deployment instructions
- docs/test_documentation.md - Testing strategy, coverage, and instructions
- docs/toxicity_system.md - Toxicity tracking design and usage
- google_export.md - Google Sheets setup notes (repository root)

**Strengths of the Project**

## **Strong Modularity**

The project is cleanly divided into controller, model, view, config, and common layers. Each layer has a well-defined responsibility, reducing coupling and making the codebase easier to maintain and extend.

## **Complete Tournament Lifecycle**

This is not a collection of isolated commands. The bot manages the full arc of a tournament event: registration, matchmaking, team display, result recording, MVP voting, and player tracking.

## **Technical Breadth**

The project integrates a wide range of technologies:

- Discord bot development with slash commands and interactive UI
- External API integration (Riot Games, Google Sheets, OpenAI)
- SQLite database management with a custom model layer
- Background task scheduling
- Unit and integration test coverage
- Docker containerization and GitHub Actions CI/CD
- Experimental AI-assisted seeding modules

## **Extensible Design**

The presence of Call of Duty, Marvel Rivals, seeding, and AI modules demonstrates that the system was designed as a general esports operations platform, not a one-off tool for a single game.

**Known Limitations**

## **1\. SQLite Concurrency Limits**

SQLite is lightweight and easy to use, but it can become a bottleneck under heavy simultaneous write loads. A migration to PostgreSQL would be recommended for any multi-server or high-traffic deployment.

## **2\. External API Dependency**

Riot API features depend on API key validity, rate limits, and network connectivity. Key expiration or API changes could disrupt player registration and rank-related features.

## **3\. Mixed Command Styles**

Most features use slash commands, but the giveaway feature still uses a legacy prefix command (\$giveaway). This inconsistency in the user interface is a known issue and a candidate for future standardization.

## **4\. Uneven Multi-Game Support**

League of Legends is clearly the primary supported title. Call of Duty and Marvel Rivals modules are less fully integrated and are more experimental in nature.

## **5\. Configuration Complexity**

The optional features (Google Sheets, Riot API, Docker, AI) add meaningful capability but also increase the complexity of initial setup and deployment.

# **Future Improvements**

- Migrate from SQLite to PostgreSQL for improved scalability and concurrent write support
- Standardize all commands to slash commands, replacing \$giveaway
- Complete and fully document non-League game support
- Build a web dashboard for administrative control and match analytics
- Add bracket generation and visualization tooling
- Improve match history analytics and reporting
- Implement role-based permissions within the bot beyond the current admin flag
- Improve logging and observability across all modules
- Expand CI pipelines to include automated test execution on pull requests
- Develop AI-assisted team formation and seeding modules beyond experimental status

**Conclusion**

The KSU Esports Tournament Bot is a well-structured, feature-rich Discord application built to automate real competitive gaming operations at Kennesaw State University. It covers the complete tournament lifecycle-from player registration and skill-based matchmaking through team display, result recording, MVP voting, and player data management.

The project demonstrates strong engineering practices: a clean MVC architecture, genetic algorithm-based matchmaking, integration of five distinct external systems, both unit and integration test coverage, Docker and CI/CD support, and a comprehensive internal documentation ecosystem. The multi-game scaffold and AI-assisted seeding modules further show that the system was designed to grow beyond its initial scope.