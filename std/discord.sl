# Discord bot module (Pure SynthLang)
@python module "discord" as discord

fn run(token: str, handler: fn):
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
        let response = handler(content, str(author))
        if response:
            let channel = message.channel
            await channel.send(response)
            
    client.event(on_ready)
    client.event(on_message)
    client.run(token)

fn get_token():
    @python module "os" as os
    return os.environ.get("DISCORD_TOKEN", "")