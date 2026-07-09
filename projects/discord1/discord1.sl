# discord1.sl - SynthLang Discord Prison Bot v1.0
# Pure SynthLang - Powered by native async/await and keywords FFI
#
# Usage: slang projects/discord1/discord1.sl

@python module "builtins" as builtins
@python module "discord" as discord
@python module "json" as json
@python module "os" as os

# ============================================================
# PRISON DATA MANAGEMENT
# ============================================================

let prison_data = {}
let data_path = "projects/discord1/prison_data.json"

fn read_data_file():
    let f = builtins.open(data_path, "r")
    let content = f.read()
    f.close()
    prison_data = json.loads(content)

fn load_prison_data():
    if os.path.exists(data_path):
        try read_data_file():
        handle err:
            prison_data = {}
    else:
        prison_data = {}

fn write_data_file():
    let f = builtins.open(data_path, "w")
    let content = json.dumps(prison_data)
    f.write(content)
    f.close()

fn save_prison_data():
    try write_data_file():
    handle err:
        print("Failed to save prison data")

# ============================================================
# COMMAND LOGIC
# ============================================================

fn cmd_prison(user):
    if user in prison_data:
        let cell = prison_data[user]["cell"]
        return user + " is already in prison! Cell #" + str(cell)
        
    let cell = len(prison_data) + 1
    let prisoner = {"cell": cell, "crime": "Unknown", "sentence": 0}
    prison_data[user] = prisoner
    save_prison_data()
    return user + " has been sent to prison! Cell #" + str(cell)

fn cmd_free(user):
    if user in prison_data:
        del prison_data[user]
        save_prison_data()
        return user + " has been released from prison!"
    return user + " is not in prison."

fn cmd_cell(user):
    if user in prison_data:
        let cell = prison_data[user]["cell"]
        let crime = prison_data[user]["crime"]
        return user + " is in Cell #" + str(cell) + " | Crime: " + crime
    return user + " is not in prison."

fn cmd_crime(user, crime):
    if user in prison_data:
        prison_data[user]["crime"] = crime
        save_prison_data()
        return user + "'s crime has been set to: " + crime
    return user + " is not in prison."

fn cmd_list():
    if len(prison_data) == 0:
        return "The prison is empty!"
    let roster = "=== Prison Roster ==="
    for user, data in prison_data:
        let cell = data["cell"]
        let crime = data["crime"]
        roster = roster + "\n  " + user + " | Cell #" + str(cell) + " | Crime: " + crime
    return roster

# ============================================================
# MESSAGE ROUTER
# ============================================================

fn clean_user(user):
    let cleaned = user.replace("<", "")
    cleaned = cleaned.replace(">", "")
    cleaned = cleaned.replace("@", "")
    cleaned = cleaned.replace("!", "")
    return cleaned

fn process_command(content, author):
    if content == "!help":
        return "**SynthLang Prison Bot v1.0**\nCommands:\n  `!prison @user` - Send user to prison\n  `!free @user` - Release user\n  `!cell @user` - Check cell\n  `!crime @user <crime>` - Set crime\n  `!list` - List prisoners\n  `!ping` - Check latency"
        
    let parts = content.split(" ")
    let cmd = parts[0]
    
    if cmd == "!prison":
        if len(parts) < 2:
            return "Usage: !prison @user"
        let user = clean_user(parts[1])
        return cmd_prison(user)
        
    if cmd == "!free":
        if len(parts) < 2:
            return "Usage: !free @user"
        let user = clean_user(parts[1])
        return cmd_free(user)
        
    if cmd == "!cell":
        if len(parts) < 2:
            return "Usage: !cell @user"
        let user = clean_user(parts[1])
        return cmd_cell(user)
        
    if cmd == "!crime":
        if len(parts) < 3:
            return "Usage: !crime @user <crime>"
        let user = clean_user(parts[1])
        let crime = parts[2]
        return cmd_crime(user, crime)
        
    if cmd == "!list":
        return cmd_list()
        
    if cmd == "!ping":
        return "Pong! Bot is alive."
        
    return None

# ============================================================
# MAIN ENTRY POINT
# ============================================================

fn main():
    print("=== SynthLang Discord Prison Bot v1.0 ===")
    print("Starting client...")
    
    load_prison_data()
    print("Prison data loaded.")

    # Get token from projects/discord1/.env
    let token = ""
    let env_path = "projects/discord1/.env"
    if os.path.exists(env_path):
        let f = builtins.open(env_path, "r")
        let lines = f.readlines()
        f.close()
        for line in lines:
            if line.startswith("DISCORD_TOKEN="):
                token = line.replace("DISCORD_TOKEN=", "").strip()
                
    if token == "":
        token = os.environ.get("DISCORD_TOKEN", "")
        
    if token == "":
        print("ERROR: DISCORD_TOKEN not found!")
        return None

    # Start the bot
    let intents = discord.Intents.all()
    let client = discord.Client(intents=intents)

    async fn on_ready():
        let user = client.user
        print("Logged in as " + str(user))

    async fn on_message(message):
        let author = message.author
        let bot_user = client.user
        if author == bot_user:
            return None

        let content = message.content
        if content.startswith("!"):
            let response = process_command(content, str(author))
            if response:
                let channel = message.channel
                await channel.send(response)

    client.event(on_ready)
    client.event(on_message)
    client.run(token)

main()