# KSU Esports Tournament - Game Day Guide


1. **Player Registration**
   - Players use the command: `/register`
   - Select which game they are registering for
   - They enter their game details (username and tagid)
   - Select rank (if applicable)


### 2. Running Matchmaking

1. **Start Matchmaking**
   - Use the commands: `/run_marvelrivals_matchmaking`, `/run_cod_matchmaking`, or `/run_league_matchmaking` depending on the game
   - Options:
     - `players_per_game`: Choose between players per game or use default for typical team size of the selected game
     - `sit_out_method`: How to select players if not divisible by 10 (`random`, `lowest_rank`, or `volunteer`)

2. **Review Initial Teams**
   - The bot will display the generated teams
   - Review player matchups and stats (tier, rank, role, kda, etc. This depends on the game selected)


### 3. Match Results and MVP Voting

1. **Record Match Results**
   - After matches complete: `/record_match_result`
   - Select the match ID
   - Select the winning team

2. **Initiate MVP Voting**
   - MVP voting will be offered automatically after recording results
   - Alternatively: `/start_mvp_voting`
   - Select the match ID

3. **Monitor and Close Voting**
   - Players vote using the dropdown in the tournament channel
   - Voting typically runs for 5 minutes
   - Optionally end mvp voting early using `/end_mvp_voting`
   - Results are announced automatically when voting closes

### 5. Tournament Seeding

1. **Seeding From Matchmaking**
   - Run one of the matchmaking commands: `/run_marvelrivals_matchmaking`, `/run_cod_matchmaking`, or `/run_league_matchmaking`
   - After matchmaking completes, run: `/seed_from_matchmaking`
      - This takes the latest matchmaking session and seeds a tournament bracket using the players from matchmaking.

2. **Seeding From Teams**
   - Players will create a team with: `/team_create`
      - Team owner will select a game for the team
      - A dropdown view will populate where you can select users in the server to invite to the game. 
      - The number of invites you are able to send depends on the max team size for the selected game (EX: League = owner + 4 invites, 5 players per team)
   - To create a tournament for a game using created teams use: `/seed_teams`
      - Select a game to start tournament seeding for
      - 


### Administrative Commands
- `/clear_db` - Removes or resets all data stored in the database
- `/record_match_result` - Record which team won
- `/start_mvp_voting` - Start MVP voting for a match
- `/list_players` - View all registered players
- `/insert_codtest_players` - creates test players registered for Call of Duty in the DB
- `/insert_marvelrivals_test_players` - creates test players registered for Marvel Rivals in the DB
- `/simulate_checkins` - creates test players registered for League of Legends in the DB
- `/create_fake_teams` - creates a fake team with test players (allows you to select which game the team is created for)
