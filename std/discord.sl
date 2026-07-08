@python module "discord" as _discord
@python module "os" as _os

let client = null

fn run(token: str, handler: fn):
    global client
    
    if client == null:
        client = _discord.Client()
    
    fn on_message(message):
        if message.author == client.user:
            return
        let content = message.content
        let user_id = str(message.author.id)
        let response = handler(content, user_id)
        if response != "":
            _discord.send_message(message.channel, response)
    
    client.event(on_message)
    client.run(token)
    return true

fn get_token():
    return _os.getenv("DISCORD_TOKEN")

fn on_ready():
    if client:
        return "Bot is ready"
    return "No client initialized"

fn send_message(channel, content: str):
    return channel.send(content)