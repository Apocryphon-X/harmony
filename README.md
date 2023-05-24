# harmony
Discord bot to attend omegaUp contest clarifications easily.

> **Warning**: This bot has been created at an accelerated pace of development to meet the OMI[PS] 2023 deadlines. In the near future, the bot will be refactored and integrated with *new Python 3 modules* to facilitate future development. Any current issues with the bot will be fixed after the upgrade, unless they are critical bugs that affect the bot's operation.

## Requirements

To get started with the bot, make sure you have the following environment variables set up:

- `$OMEGAUP_API_TOKEN`: This token is crucial for authenticating with the OmegaUp API. If you don't have one yet, you can obtain it by following the instructions [here][1].

- `$HARMONY_TOKEN`: This is the Discord token specifically designed for bots, which Harmony will utilize to send messages and execute commands seamlessly.

If you haven't set up these environment variables yet, Harmony will prompt you for them during the initial setup process. You'll also be asked to provide additional information, such as the guild and channel IDs where the bot will communicate and the target contest.

## Quickstart
Once the bot has been properly configured, it will start listening for incoming clarifications from the specified contest. This will happen automatically every 10 seconds (please note that API Tokens have a **limit of 1000 requests per hour**, so if the 10-second delay is decreased, the limit may be reached very quickly).

In addition, the bot features an `/announce` slash command. You can use this command to send a public clarification with a specified message about the selected problem.

If you have any questions or concerns about Harmony, please let me know.


[1]: https://github.com/omegaup/omegaup/tree/main/frontend/server/src/Controllers#apiusercreateapitoken
