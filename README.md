![image](https://github.com/Apocryphon-X/harmony/assets/40130428/532993d8-4798-4eb8-9fa2-d9288d2c91d3)

Discord bot to attend omegaUp contest clarifications easily.

> **Warning**: This bot has been created at an accelerated pace of development to meet the OMI[PS] 2023 deadlines. In the near future, the bot will be refactored and integrated with *new Python 3 modules* to facilitate future development. Any current issues with the bot will be fixed after the upgrade, unless they are critical bugs that affect the bot's operation.

## Requirements

To get started with the bot, make sure you have the following environment variables set up:

- `$OMEGAUP_API_TOKEN`: This token is crucial for authenticating with the omegaUp API. If you don't have one yet, you can obtain it by following the instructions [here][1].

- `$HARMONY_TOKEN`: This is the Discord token specifically designed for bots, which Harmony will utilize to send messages and execute commands seamlessly.

If you haven't set up these environment variables yet, Harmony will prompt you for them during the initial setup process. You'll also be asked to provide additional information, such as the guild and channel IDs where the bot will communicate and the target contest.

![Log Example][6]


## Quickstart
Once the bot has been properly configured, it will start listening for incoming clarifications from the specified contest. This will happen automatically every 10 seconds (please note that API Tokens have a **limit of 1000 requests per hour**, so if the 10-second delay is decreased, the limit may be reached very quickly). 

On every Harmony notification will apear some buttons as shown below:

|Notification| Modal Form |Final Message|
|:----------:|:----------:|:-----------:|
| ![IMG][3]  | ![IMG][4]  |  ![IMG][5]  |

In addition, the bot features an `/announce` slash command. You can use this command to send a public clarification with a specified message about the selected problem.

![Slash Command][2]

If you have any questions or concerns about Harmony, please let me know.

[1]: https://github.com/omegaup/omegaup/tree/main/frontend/server/src/Controllers#apiusercreateapitoken
[2]: https://github.com/Apocryphon-X/harmony/assets/40130428/a93536b1-7c4c-456f-90ce-bd6584f602fe
[3]: https://github.com/Apocryphon-X/harmony/assets/40130428/ed7bb4be-e1b2-460a-9e8e-ab63ca64df02
[4]: https://github.com/Apocryphon-X/harmony/assets/40130428/3ba7d9ef-6313-4ec2-b912-05810c9a0c79
[5]: https://github.com/Apocryphon-X/harmony/assets/40130428/c2255e94-d470-49e4-beda-d505f3c6a3cc
[6]: https://github.com/Apocryphon-X/harmony/assets/40130428/0ebea953-a172-4da4-b8c1-c31818a18d18
