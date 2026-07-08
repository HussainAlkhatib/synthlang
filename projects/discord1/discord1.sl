# discord1.sl - The Ultimate Zero-Bridge Discord Prison Bot  
# SynthLang v1.0.0 - All logic in SynthLang, no adapters needed

# ============================================================
# COMMAND HANDLERS (Pure SynthLang)
# ============================================================

fn cmd_help():
    return "Commands: !prison @user, !free @user, !cell @user, !help"

fn cmd_prison(user):
    let exists = false
    if not exists:
        let prisoner = {"cell": 1, "crime": "Unknown", "sentence": 0}
        return "User " + user + " has been sent to prison! Cell #1"
    return "User " + user + " is already in prison!"

fn cmd_free(user):
    return "User " + user + " has been released!"

fn cmd_cell(user):
    let data = {"test": {"cell": 5}}
    if user in data:
        let cell = data[user]["cell"]
        return "User " + user + " is in cell #" + str(cell)
    return "User " + user + " is not in prison."

# ============================================================
# MESSAGE ROUTER (Pure SynthLang)
# ============================================================

fn clean_user(user):
    let cleaned = user.replace("<", "")
    cleaned = cleaned.replace(">", "")
    cleaned = cleaned.replace("@", "")
    return cleaned

fn process_message(content, author):
    if content == "!help":
        return cmd_help()
    
    let parts = content.split(" ")
    let cmd_name = parts[0]
    let user = ""
    if len(parts) > 1:
        user = parts[1]
    user = clean_user(user)
    
    if cmd_name == "!prison":
        if user == "":
            return "Usage: !prison @user"
        return cmd_prison(user)
    
    if cmd_name == "!free":
        return cmd_free(user)
    
    if cmd_name == "!cell":
        return cmd_cell(user)
    
    return "Unknown command. Use !help."

# ============================================================
# MAIN ENTRY POINT - Test Mode (No Discord)
# ============================================================

fn main():
    print("=== SynthLang Discord Prison Bot v1.0.0 ===")
    print("Test mode - testing core functions...")
    
    print("\nTesting cmd_help:")
    print(cmd_help())
    
    print("\nTesting process_message:")
    print("!help ->", process_message("!help", "test"))
    print("!cell @test ->", process_message("!cell @test", "test"))
    print("!prison @test ->", process_message("!prison @test", "test"))
    
    print("\nBot initialized successfully!")

main()