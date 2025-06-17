# V2Ray Proxy Telegram Bot

## Overview
This project automatically collects and distributes Telegram proxy links via a Telegram channel.

## Features
- Fetches latest proxy links from online sources
- Removes duplicate proxies
- Sends proxies to a Telegram channel
- Automated updates via GitHub Actions

## GitHub Actions Workflow

### Scheduled Updates
The workflow runs automatically every 2 hours to:
- Fetch the latest proxy links
- Remove duplicates
- Send updates to the Telegram channel

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
3. Create a `.env` file with your Telegram credentials
4. Run the bot: `python run_bot.py`

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
- `MAX_PROXIES`: Maximum number of proxies to collect (default: 100)
- `PROXY_SOURCE_URL`: Custom proxy source URL
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