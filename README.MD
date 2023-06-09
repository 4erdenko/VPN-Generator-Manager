# VPN Bot Manager

![Python](https://img.shields.io/badge/python-v3.9-blue)
![Docker](https://img.shields.io/badge/docker-latest-blue)
[![Build Status](https://img.shields.io/endpoint.svg?url=https%3A%2F%2Factions-badge.atrox.dev%2F4erdenko%2FMischievousBednorz%2Fbadge&style=flat)](https://actions-badge.atrox.dev/4erdenko/MischievousBednorz/goto)

This is a Telegram bot for managing VPN servers that you've received from the free VPN distribution service in Russia [VPNgen](https://vpngen.org/ru/#generator). If you're a VPN server manager (brigadier) from VPNgen, you can use this bot to manage your server users directly from Telegram.

The bot runs inside a Docker container, and it can be automatically deployed using a GitHub Actions CI/CD pipeline.

## Features

- Manage users of your VPN server
- Get a list of users
- Perform actions on user accounts
- Check user activity
- Receive notifications about server status
- Use either as a standalone application or inside a Docker container

![Bot Demo](https://i.imgur.com/G0p6rmI.png)

## Requirements

- Python 3.9+
- Docker (for container deployment)
- A VPN server from VPNgen
- A Wireguard `wg0.conf` file from the VPN server
- A Telegram bot API token

## Quickstart

Clone this repository to your machine:

```bash
git clone https://github.com/username/repo.git
cd repo
```

### Running Locally

If you want to run the bot on your local machine, follow these steps:

1. Install the necessary packages:

    ```bash
    pip install -r requirements.txt
    ```

2. Create a `.env` file in the project's root directory with the following content:

    ```text
    BOT_API=your_bot_token
    CHAT_ID=your_chat_id
    START_MSG=your_welcome_message
    ```

3. Run the bot:

    ```bash
    python main.py
    ```

### Running in Docker

To run the bot inside a Docker container, make sure Docker is installed and running on your machine:

1. Build the Docker image:

    ```bash
    docker build -t vpnbot .
    ```

2. Create a `.env` file as described above.

3. Run the Docker container:

    ```bash
    docker run --env-file .env -v $(pwd)/wireguard:/app/wireguard vpnbot
    ```

Here, we are mounting the `wireguard` directory from your local machine into the Docker container, so that the bot can access the `wg0.conf` file.

## Automatic Deployment with GitHub Actions

You can also set up automatic deployment of your bot using the provided GitHub Actions CI/CD pipeline. You will need to add the following secrets to your GitHub repository:

- `HOST`: The IP address or hostname of your server.
- `USER`: The username to use for SSH.
- `SSH_KEY`: Your private SSH key for accessing the server.
- `SSH_PASSPHRASE`: The passphrase for your SSH key, if any.
- `PROJECT_PATH`: The path on your server where the bot will be deployed.
- `BOT_API`: Your Telegram bot API token.
- `CHAT_ID`: The chat ID where your bot will operate.
- `START_MSG`: The start message for your bot.
- `WG0_CONF`: The content of your `wg0.conf` file.

Once these secrets are set up, the bot will automatically be deployed to your server whenever you push to the `master` branch.

## Contribution

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)