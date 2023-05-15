import os

from dataclasses import dataclass

import discord
import requests
import rich.traceback

from rich.console import Console


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

class HarmonyBot(discord.Bot):
    OMEGAUP_API_ENTRYPOINT = "https://omegaup.com/api"

    def set_omegaup_token(self, api_token):
        self.omegaup_client = requests.Session()
        self.omegaup_client.headers["Authorization"] = f"token {api_token}"

    async def check_omegaup_profile(self):
        api_data = self.omegaup_client.get(f"{self.OMEGAUP_API_ENTRYPOINT}/user/profile").json()
        if "error" in api_data:
            console.log(f"{Bars.critical_error}{Prompts.omegaup} Message error found: '{api_data['error']}'")
            console.log(f"{Bars.info}{Prompts.client} Probably a bad API TOKEN was provided.")
            console.log(f"{Bars.warning}{Prompts.client} Aborting.")
            await self.close()
            return

        console.log(
            f"{Bars.success}{Prompts.omegaup} Logged in as: "
            f"[green]{api_data['name']}[/] [magenta]({api_data['username']})[/]"
        )

    async def on_error(self, event_method, *args, **kwargs):
        console.log(f"{Bars.error}{Prompts.client} Ignoring exception in [yellow]`{event_method}`[/]:")
        console.print_exception(show_locals=True)

    async def on_ready(self):
        await self.check_omegaup_profile()
        console.log(
            f"{Bars.success}{Prompts.discord} Logged in as: "
            f"[green]{self.user}[/] [magenta]({self.user.id})[/]"
        )


def get_token(name):
    token_value = os.getenv(name)
    if token_value is None:
        console.print(f"[red](!)[/] Environment variable [green]${name}[/] not found.")
        token_value = console.input("[cyan](?)[/] Please provide your token: ", password=True)
        console.clear()
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
    console.print("\n[cyan](i)[/] Sayōnara!")
