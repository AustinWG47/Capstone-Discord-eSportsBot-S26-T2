## **Setup Guide**

## **1\. Clone the Repository**

git clone <https://github.com/AustinWG47/Capstone-Discord-eSportsBot-S26-T2.git>

cd Capstone-Discord-eSportsBot-S26-T2

## **2\. Create the Environment File**

- Copy the provided `.env.template` file to a new file named `.env`:

macOS / Linux:

cp .env.template .env

Windows:

copy .env.template .env

Fill in all required values before proceeding:

```
# Discord Configuration
DISCORD_APITOKEN=your_discord_bot_token_here
DISCORD_GUILD=your_discord_server_id_here

# Database Configuration
DATABASE_NAME=tournament.db

# Channel IDs
TOURNAMENT_CH=tournament_general
FEEDBACK_CH=feedback_channel
# CHANNEL_CONFIG must be a valid JSON string with this structure:
# Format: {"Category": {"channel_name": {"role_key": "RoleName"}, ...}}
# Use actual role names that exist in your Discord server (like "Admin" or "Moderator")
# You can use "@everyone" for the default role that everyone can see
CHANNEL_CONFIG={"Tournament": {"announcements": {"admin": "Admin", "everyone": "@everyone"}, "registration": {"everyone": "@everyone"}, "team-info": {"everyone": "@everyone"}, "results": {"everyone": "@everyone"}, "admin": {"admin": "Admin"}}}
CHANNEL_PLAYER=t_announcement
PRIVATE_CH=admin_channel

# Webhook Configuration
WEBHOOK_URL=your_webhook_url_here

# Riot Games API
API_KEY=your_riot_api_key_here
API_URL=https://na1.api.riotgames.com/lol
RIOT_API_KEY=your_riot_api_key_here  # Can be the same as API_KEY

# API Task Control (Optional)
STOP_API_TASK=false
START_API_TASK=true

# OpenAI Configuration (Optional - for advanced team matchmaking)
OPEN_AI_KEY=your_openai_api_key_here
prompt="Your OpenAI prompt for team matchmaking here"

# Google Sheets Integration (Optional)
GOOGLE_SHEET_ID=your_google_sheet_id_here
CELL_RANGE=Sheet1
LOL_SERVICE_PATH=./service_account.json
```

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

- Go to the [Discord Developer Portal](https://discord.com/developers/applications)
- Create a new application > Bot tab > Reset Token > Copy token
- Enable "Server Members Intent" under Privileged Gateway Intents
- Paste the token into `.env` as DISCORD_APITOKEN

## **6\. Obtain Server (Guild) ID**
- Enable Developer Mode in Discord settings
- Right-click your server > Copy ID > Add to `.env` as DISCORD_GUILD

## **7\. Configure the Riot API**

Obtain a Riot API development key and add it to the .env file under both API_KEY and RIOT_API_KEY.
- Visit [Riot Developer Portal](https://developer.riotgames.com)
- Register for a personal key 
- Add the key to `.env` as API_KEY

## **8\. Configure Ollama (Optional for AI-assisted seeding)**

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

## **9\. Configure Google Sheets (Optional)**

Add your Google Sheet ID and service account credentials path to .env to enable the import/export feature.

## **10\. Run the Bot**

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