from model.dbc_model import Tournament_DB, Player, Game

def main():
    # Create DB + tables
    db = Tournament_DB()
    Player.createTable(db)
    Game.createTable(db)

    # Fake discord user id + linked LoL name (just a label for now)
    user_id = 111111111111111111
    summoner_name = "ExampleSummoner"

    # Store the link in player table
    db.cursor.execute(
        "INSERT OR REPLACE INTO player(user_id, game_name, game_id, tag_id, isAdmin, mvp_count, toxicity_points) "
        "VALUES(?,?,?,?,0,0,0)",
        (user_id, "League of Legends", None, summoner_name)
    )
    db.connection.commit()

    # Mock stats (this is what Riot API would normally return)
    tier = "GOLD"
    rank = "II"
    wins = 25
    losses = 20

    # Save into game table using the existing helper
    Game().update_player_API_info(user_id, tier, rank, wins, losses)

    # Verify saved row
    db.cursor.execute(
        "SELECT user_id, game_name, tier, rank, wins, losses, wr FROM game "
        "WHERE user_id=? ORDER BY game_date DESC LIMIT 1",
        (user_id,)
    )
    row = db.cursor.fetchone()
    print("Saved row:", row)

if __name__ == "__main__":
    main()