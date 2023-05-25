![Banner][7]

Discord bot to attend omegaUp contest clarifications easily.

> **Warning**: This bot has been created at an accelerated pace of development to meet the OMI[PS] 2023 deadlines. In the near future, the bot will be refactored and integrated with *new Python 3 modules* to facilitate future development. Any current issues with the bot will be fixed after the upgrade, unless they are critical bugs that affect the bot's operation.

## Requirements

To get started with the bot, make sure you have the following environment variables set up:

- `$OMEGAUP_API_TOKEN`: This token is crucial for authenticating with the omegaUp API. If you don't have one yet, you can obtain it by following the instructions [here][1].

- `$HARMONY_TOKEN`: This is the Discord token specifically designed for bots, which Harmony will utilize to send messages and execute commands seamlessly.

If you haven't set up these environment variables yet, Harmony will prompt you for them during the initial setup process. You'll also be asked to provide additional information, such as the guild and channel IDs where the bot will communicate and the target contest.

This is just an example of how it looks like:
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

# License

<img align="right" src="https://user-images.githubusercontent.com/40130428/112392193-a253ae00-8cbe-11eb-8a27-729c23729923.png">

<p align="justify">
  <a href="https://github.com/Apocryphon-X/harmony">Apocryphon-X/harmony</a> is licensed under the MIT License. A short and simple permissive license with conditions only requiring preservation of copyright and license notices. Licensed works, modifications and larger works may be distributed under different terms and without source code.
More details can be found in the <a href="https://github.com/Apocryphon-X/harmony/blob/main/LICENSE"><code>LICENSE</code></a> file.
</p>

[1]: https://github.com/omegaup/omegaup/tree/main/frontend/server/src/Controllers#apiusercreateapitoken
[2]: https://github.com/Apocryphon-X/harmony/assets/40130428/3d50714d-eefb-47bf-85b9-ad5295b48f5d
[3]: https://github.com/Apocryphon-X/harmony/assets/40130428/e438bd40-68d3-41c9-b98a-3e5fff3cde52
[4]: https://github.com/Apocryphon-X/harmony/assets/40130428/d9f1fee1-ecad-4e24-b156-1eda9429f14d
[5]: https://github.com/Apocryphon-X/harmony/assets/40130428/1c69d2a8-508f-48f6-8366-5ede40423e0c
[6]: https://github.com/Apocryphon-X/harmony/assets/40130428/f0b81beb-3dc4-448c-b125-91d2208b3291
[7]: https://github.com/Apocryphon-X/harmony/assets/40130428/1706e9c8-50f4-4540-b910-72f47e445507
