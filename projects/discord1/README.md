# Discord Prison Bot (v2.0)

A Discord bot written in pure SynthLang with zero Python adapters.

## Overview

This bot allows server administrators to manage a "prison" system for Discord users. Users can be sent to prison, assigned crimes, given sentences, and potentially granted parole.

## Architecture (v2.0 - Zero Bridge)

The bot follows a **zero-bridge architecture** where:
- **ONLY file needed**: `discord1.sl` - Run with `slang discord1.sl`
- **No Python adapters**: All FFI handled internally by SynthLang std modules
- **Standard library**: Uses `@python module "std/discord"` and `@python module "std/fs"`

## Commands

| Command | Description |
|---------|-------------|
| `!prison @user` | Send a user to prison (assigns cell) |
| `!free @user` | Release a user from prison |
| `!cell @user` | Show the cell number of a user |
| `!crime @user [crime_type]` | Assign a crime to a user |
| `!sentence @user [days]` | Set the sentence duration |
| `!parole @user` | Request parole (random approval) |
| `!execute @user` | Execute a user (admin only) |
| `!help` | Show all available commands |

## Setup (v2.0)

1. Install SynthLang:
   ```bash
   pip install synthlang
   ```

2. Install Discord.py:
   ```bash
   pip install discord.py
   ```

3. Set your Discord bot token in `.env`:
   ```
   DISCORD_TOKEN=your_bot_token_here
   ```

4. Run the bot:
   ```bash
   cd projects/discord1
   slang discord1.sl
   ```

**That's it!** No Python wrapper files needed.

## FFI Integration (v2.0)

The bot uses the unified FFI syntax:

```sl
@python module "std/discord" as discord
@python module "std/fs" as fs
@python module "std/crypto" as crypto

fn process_message(content, author):
    if content == "!help":
        return cmd_help()
    # ... routing logic

fn main():
    let token = discord.get_token()
    discord.run(token, process_message)
```

### Standard Library Functions

| Module | Function | Description |
|--------|----------|-------------|
| `std/discord` | `run(token, handler)` | Start Discord bot with message handler |
| `std/discord` | `get_token()` | Get DISCORD_TOKEN from environment |
| `std/fs` | `exists(path)` | Check if file exists |
| `std/fs` | `read_json(path)` | Read JSON file |
| `std/fs` | `write_json(path, data)` | Write JSON file |
| `std/crypto` | `random_int(min, max)` | Random integer for parole rolls |

## Data Storage

Prison data is stored in `prison_data.json` with structure:
```json
{
  "user_id": {
    "cell": 1,
    "crime": "theft",
    "sentence": 30,
    "parole_status": "denied"
  }
}
```

## SynthLang Features Demonstrated

- Universal FFI imports (`@python module "std/xxx"`)
- Function definitions with parameters
- Control flow (`if`/`else`, `for`)
- String and dictionary operations via std modules
- Native async support via persistent event loop

## License

MIT License - Part of the SynthLang project