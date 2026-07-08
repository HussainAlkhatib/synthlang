@python module "std/discord" as discord
@python module "os" as _os

fn main():
    token = _os.getenv("DISCORD_TOKEN")
    print("Discord bot starting with v2.0 FFI")
    if token == "" or token == null:
        print("Set DISCORD_TOKEN environment variable to run")
        return
    
    fn on_message(content, author):
        return "Received: " + content
    
    discord.run(token, on_message)
    print("Bot connected and ready!")