# V2Ray Proxy Telegram Bot

## Overview
This project automatically collects and distributes Telegram proxy links via a Telegram channel.

## Features
- Fetches latest proxy links from online sources (defined in sources.json)
- Prioritizes proxies from Telegram channels over JSON sources
- Removes duplicate proxies
- Sends up to the first 1000 proxies to a Telegram channel (in batches)
- Persian (Jalali) calendar date in the Farsi summary message
- Automated updates via GitHub Actions
- Modular, maintainable codebase

## GitHub Actions Workflow

### Scheduled Updates
The workflow runs automatically every 4 hours to:
- Fetch the latest proxy links
- Remove duplicates
- Send updates to the Telegram channel
- Commit the updated `proxies.txt` to the repository

### Manual Trigger
You can also manually trigger the workflow from the GitHub Actions tab.

## Setup

### Prerequisites
- Python 3.9+
- Telegram Bot Token
- Telegram Channel ID

### Environment Variables
Set the following secrets in your GitHub repository settings:
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
- `TELEGRAM_CHANNEL_ID`: The ID of the Telegram channel to post proxies

## Local Development
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
   - Make sure you have [jdatetime](https://pypi.org/project/jdatetime/) installed for Persian calendar support.
3. Create a `.env` file with your Telegram credentials (see below)
4. Create or edit `sources.json` to define your proxy sources (see example below)
5. Run the bot: `python main.py`

### sources.json Example
```
{
  "json_urls": [
    "https://raw.githubusercontent.com/hookzof/socks5_list/master/tg/mtproto.json"
  ],
  "telegram_channels": [
    "https://t.me/s/HiProxy",
    "https://t.me/s/iRoProxy",
    "https://t.me/s/MProxy_ir",
    "https://t.me/s/ProxyHagh",
    "https://t.me/s/PyroProxy",
    "https://t.me/s/darkproxy",
    "https://t.me/s/proxyinwar",
    "https://t.me/s/MelliProxy",
    "https://t.me/s/Proxy_FreeL",
    "https://t.me/s/MTelProto",
    "https://t.me/s/Forall_Proxy",
    "https://t.me/s/WhAlE_ChAnEl",
    "https://t.me/s/v2raychidari",
    "https://t.me/s/BestSpeedProxy"
  ]
}
```

## Contributing
Contributions are welcome! Please open an issue or submit a pull request.

## License
[Specify your license here]

## Environment Configuration

### Creating .env File
1. Copy the `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your specific configuration:

#### Required Environment Variables
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token from BotFather
- `TELEGRAM_CHANNEL_ID`: The ID of the Telegram channel to post proxies

#### Optional Configuration Variables
- `LOG_LEVEL`: Logging verbosity (default: INFO)
  - Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
- `REQUEST_TIMEOUT`: HTTP request timeout in seconds (default: 30)
- `MAX_RETRIES`: Number of retry attempts for failed requests (default: 3)

### Obtaining Telegram Credentials
1. Create a bot using [BotFather](https://t.me/botfather)
2. Get your bot token
3. Add your bot to the target channel with admin rights

### GitHub Secrets
For GitHub Actions, set the following secrets in your repository settings:
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHANNEL_ID`

### Security Notes
- Never commit your `.env` file to version control
- Keep your bot token and channel ID confidential

## Running as GitHub Action

### Setup Steps
1. Fork this repository
2. Create a Telegram bot with [BotFather](https://t.me/botfather)
3. Add bot to your target Telegram channel with admin rights

### GitHub Repository Configuration
1. Go to repository Settings > Secrets and variables > Actions
2. Add two repository secrets:
   - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
   - `TELEGRAM_CHANNEL_ID`: Your Telegram channel ID

### Workflow Triggers
- **Scheduled**: Runs automatically every 4 hours
- **Manual**: Can be triggered from Actions tab

### How to Manually Trigger
1. Go to repository "Actions" tab
2. Select "Telegram Proxy Update" workflow
3. Click "Run workflow"
4. Choose branch and run

### Monitoring
- View workflow runs in the "Actions" tab
- Check detailed logs for any issues (see `bot.log` and workflow logs)

### Customization
- Edit `sources.json` to change proxy sources
- Edit `.github/workflows/proxy_update.yml` to change schedule frequency or workflow behavior

## Output
- The bot generates a single file: `proxies.txt` (one proxy per line, no header)
- Only the first 1000 proxies (prioritizing Telegram channels) are sent to the Telegram channel in each run
- The Farsi summary message uses the Persian (Jalali) calendar for the date 