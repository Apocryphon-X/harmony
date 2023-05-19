import os

from datetime import datetime
from dataclasses import dataclass

import discord
import requests
import rich.traceback

from discord.ext import tasks

from rich.console import Console
from rich.control import Control

rich.traceback.install(show_locals=True)
console = Console()

banner = """
   __
  / /  ___ _ ____ __ _  ___   ___  __ __ [blink red]*[/blink red]
 / _ \/ _ `// __//  ' \/ _ \ / _ \/ // /
/_//_/\_,_//_/  /_/_/_/\___//_//_/\_, /
                                 /___/
      Created by: [u]@Apocryphon-X[/u]
"""


@dataclass
class Prompts:
    client = "[white on #5b5b5b]$CLIENT[/]"
    omegaup = "[white on #5588dd]OMEGAUP[/]"
    discord = "[white on #404eed]DISCORD[/]"


@dataclass
class Bars:
    error = "[red]▌[/]"
    critical_error = "[blink red]▌[/]"
    info = "[cyan]▌[/]"
    success = "[green]▌[/]"
    warning = "[yellow]▌[/]"


@dataclass
class Icons:
    at_sign = "https://emoji.gg/assets/emoji/8859-discord-roles-from-vega.png"


class HarmonyBot(discord.Bot):
    OMEGAUP_API_ENTRYPOINT = "https://omegaup.com/api"
    pending_clarifications = set()

    async def _get_discord_object(self, fetch_method, object_name):
        valid_id = False
        final_object = None
        while not valid_id:
            extracted_id = console.input(
                f"[cyan](?)[/] Please provide the target {object_name} id: "
            )
            try:
                final_object = await fetch_method(extracted_id)
            except (discord.errors.NotFound, discord.errors.HTTPException):
                console.control(Control.move_to_column(0, -1))
                console.log(
                    f"{Bars.error}{Prompts.discord} That id is not working. Please verify the data you provided."
                )
            else:
                valid_id = True
        return final_object

    async def _check_omegaup_profile(self):
        api_data = self.omegaup_client.get(
            f"{self.OMEGAUP_API_ENTRYPOINT}/user/profile"
        ).json()
        if "error" in api_data:
            console.log(
                f"{Bars.critical_error}{Prompts.omegaup} Message error found: '{api_data['errorname']}'."
            )
            console.log(
                f"{Bars.info}{Prompts.client} Probably a bad API TOKEN was provided."
            )
            console.log(f"{Bars.warning}{Prompts.client} Aborting.")
            await self.close()
            return

        console.log(
            f"{Bars.success}{Prompts.omegaup} Logged in as: "
            f"[green]{api_data['name']}[/] [magenta]({api_data['username']})[/]"
        )

    def set_omegaup_token(self, api_token):
        self.omegaup_client = requests.Session()
        self.omegaup_client.headers["Authorization"] = f"token {api_token}"

    async def on_error(self, event_method, *args, **kwargs):
        console.log(
            f"{Bars.error}{Prompts.client} Ignoring exception in [yellow]`{event_method}`[/]:"
        )
        console.print_exception(show_locals=True)

    async def on_ready(self):
        await self._check_omegaup_profile()
        console.log(
            f"{Bars.success}{Prompts.discord} Logged in as: "
            f"[green]{self.user}[/] [magenta]({self.user.id})[/]"
        )

        self.main_guild = await self._get_discord_object(self.fetch_guild, "guild")
        console.control(Control.move_to_column(0, -1))
        console.log(f"{Bars.success}{Prompts.client} Guild was fetched successfully.")

        self.main_channel = await self._get_discord_object(
            self.fetch_channel, "channel"
        )
        console.control(Control.move_to_column(0, -1))
        console.log(f"{Bars.success}{Prompts.client} Channel was fetched successfully.")

        self.main_guild = self

        valid_alias = False
        self.target_contest = None

        while not valid_alias:
            self.target_contest = console.input(
                "[cyan](?)[/] Please provide the target contest alias: "
            )

            api_data = self.omegaup_client.get(
                url=f"{self.OMEGAUP_API_ENTRYPOINT}/contest/details",
                params={"contest_alias": self.target_contest},
            ).json()

            if "error" in api_data:
                console.control(Control.move_to_column(0, -1))
                console.log(
                    f"{Bars.error}{Prompts.omegaup} That alias is not valid. Please verify the data you provided."
                )
            else:
                valid_alias = True

        console.control(Control.move_to_column(0, -1))
        console.log(
            f"{Bars.success}{Prompts.client} Contest alias was stored successfully."
        )
        self.clarifications_monitor.start()

    @tasks.loop(seconds=10)
    async def clarifications_monitor(self):
        api_data = self.omegaup_client.get(
            url=f"{self.OMEGAUP_API_ENTRYPOINT}/contest/clarifications",
            params={"contest_alias": self.target_contest},
        ).json()

        if "error" in api_data:
            console.log(
                f"{Bars.error}{Prompts.omegaup} Message error found: '{api_data['errorname']}'."
            )
            return

        filtered_response = filter(
            lambda c: c["clarification_id"] not in self.pending_clarifications
            and c["answer"] is None,
            api_data["clarifications"],
        )

        for pending in filtered_response:
            notification_embed = discord.Embed()
            notification_embed.set_author(
                name=f"{pending['author']} clarification:", icon_url=Icons.at_sign
            )
            notification_embed.add_field(
                name="Problem alias:",
                value=f"`{pending['problem_alias']}`",
                inline=True,
            )

            notification_embed.add_field(
                name="Clarification id:",
                value=f"`#{pending['clarification_id']}`",
                inline=True,
            )

            notification_embed.add_field(
                name="Content:",
                value=f"```\n{pending['message']}\n```",
                inline=False,
            )

            notification_embed.timestamp = datetime.fromtimestamp(pending["time"])

            await self.main_channel.send(embed=notification_embed)
            self.pending_clarifications.add(pending["clarification_id"])


def get_token(name):
    token_value = os.getenv(name)
    if token_value is None:
        console.print(f"[red](!)[/] Environment variable [green]${name}[/] not found.")
        token_value = console.input(
            "[cyan](?)[/] Please provide your token: ", password=True
        )
    return token_value


if __name__ == "__main__":
    console.clear()

    OMEGAUP_TOKEN = get_token("OMEGAUP_API_TOKEN")
    DISCORD_TOKEN = get_token("HARMONY_TOKEN")

    console.print(f"[b #40c1f3]{banner}[/]")
    console.print("[cyan](i)[/] Establishing connections...")

    bot = HarmonyBot()
    bot.set_omegaup_token(OMEGAUP_TOKEN)
    bot.run(DISCORD_TOKEN)
    console.print("[cyan](i)[/] Sayōnara!")
