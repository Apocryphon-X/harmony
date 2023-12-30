# NOTE: This code will be refactored someday (probably soon).
# I know it's kinda* messy, but in the end deadlines are deadlines.

import os

from datetime import datetime

import discord
import requests

from discord.ext import tasks

from discord_components import AlternateButton, AnswerButton
from discord_components import AnswerModal

import rich.traceback
from log_components import *


banner = """
    __
   / /  ___ _ ____ __ _  ___   ___  __ __ [blink red]*[/blink red]
  / _ \/ _ `// __//  ' \/ _ \ / _ \/ // /
 /_//_/\_,_//_/  /_/_/_/\___//_//_/\_, /
                                  /___/
       Created by: [u]@Apocryphon-X[/u]
"""


@dataclass
class Icons:
    at_sign = "https://emoji.gg/assets/emoji/8859-discord-roles-from-vega.png"


class HarmonyBot(discord.Bot):
    OMEGAUP_API_ENTRYPOINT = "https://omegaup.com/api"
    pending_clarifications = set()
    has_target_data = False
    target_contests = ...
    omegaup_username = ...

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

        self.omegaup_username = api_data["username"]
        self.__class__.omegaup_username = self.omegaup_username

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
        if not self.has_target_data:
            self.has_target_data = True
            await self._check_omegaup_profile()
            console.log(
                f"{Bars.success}{Prompts.discord} Logged in as: "
                f"[green]{self.user}[/] [magenta]({self.user.id})[/]"
            )

            self.main_guild = await self._get_discord_object(self.fetch_guild, "guild")
            console.control(Control.move_to_column(0, -1))
            console.log(
                f"{Bars.success}{Prompts.client} Guild was fetched successfully."
            )

            self.main_channel = await self._get_discord_object(
                self.fetch_channel, "channel"
            )
            console.control(Control.move_to_column(0, -1))
            console.log(
                f"{Bars.success}{Prompts.client} Channel was fetched successfully."
            )

            self.main_guild = self

            valid_alias = False
            self.target_contests = None

            while not valid_alias:
                target_contests_input = console.input(
                    "[cyan](?)[/] Please provide the alias(es) of the contest(s) you wish to monitor. You can specify multiple values by separating them with commas: "
                )

                self.target_contests = target_contests_input.replace(" ", "").split(",")

                found_error = False
                for alias in self.target_contests:
                    api_data = self.omegaup_client.get(
                        url=f"{self.OMEGAUP_API_ENTRYPOINT}/contest/details",
                        params={"contest_alias": self.target_contests},
                    ).json()

                    if "error" in api_data:
                        console.control(Control.move_to_column(0, -1))
                        console.log(
                            f"{Bars.error}{Prompts.omegaup} That alias is not valid. Please verify the data you provided."
                        )

                        found_error = True
                        break

                if not found_error:
                    valid_alias = True

            self.__class__.target_contests = self.target_contests

            console.control(Control.move_to_column(0, -1))
            console.log(
                f"{Bars.success}{Prompts.client} Contest alias was stored successfully."
            )

            self.contest_problems = []
            self.clarifications_monitor.start()
            self.fetch_problems_task.start()

    # This can not only be fetched on start.
    # Reason: What will happen if some problems are added after that?
    # (They will not appear in the autocomplete options)
    @tasks.loop(minutes=10)
    async def fetch_problems_task(self):
        message = await self.main_channel.send(
            "Fetching some data from omegaUp... This should not take long.\n"
            "Functions will be locked during this process."
        )

        console.log(
            f"{Bars.info}{Prompts.client} Fetching omegaUp contest data "
            "to enable autocompletion on [green]/announce[/]..."
        )

        console.log(
            f"{Bars.warning}{Prompts.client} [b u]BOT WILL BE LOCKED DURING THIS "
            "PROCESS.[/] (Even Ctrl-C will not work) [dim]Sorry about that...[/]"
        )

        console.log(
            f"{Bars.warning}{Prompts.client} [b]Unformatted errors [white on red]"
            "MAY APPEAR[/white on red] after this.[/b]"
        )

        # We really need an asynchronous omegaUp client, this request blocks the entire thing
        # causing malfunctions in the bot and the Ctrl-C SIGINT signal capture.

        self.contest_problems = {}

        for alias in self.target_contests:
            api_response = bot.omegaup_client.get(
                f"{bot.OMEGAUP_API_ENTRYPOINT}/contest/problems",
                params={"contest_alias": alias},
            ).json()

            if "error" in api_response:
                break

            self.contest_problems[alias] = [
                problem["alias"] for problem in api_response["problems"]
            ]

        # ^^^^ 99% sure this will behave properly if I use AIOHTTP instead
        # (I'm out of time to implement that right now)

        await message.delete()
        await self.main_channel.send(
            "Fetching completed. We are online!", delete_after=10
        )

        if "error" in api_response:
            console.log(
                f"{Bars.error}{Prompts.omegaup} Fetching failed: '{api_response['errorname']}'."
            )
            self.contest_problems = {}
            return

        console.log(
            f"{Bars.success}{Prompts.client} Fetching completed without errors."
        )

    @tasks.loop(seconds=10)
    async def clarifications_monitor(self):
        console.log(
            f"{Bars.info}{Prompts.client} Looking for pending [u]UNREGISTERED[/] clarifications..."
        )

        for alias in self.target_contests:
            api_data = self.omegaup_client.get(
                url=f"{self.OMEGAUP_API_ENTRYPOINT}/contest/clarifications",
                params={"contest_alias": alias},
            ).json()

            if "error" in api_data:
                console.log(
                    f"{Bars.error}{Prompts.omegaup} Message error found: '{api_data['errorname']}'."
                )
                continue

            filtered_response = filter(
                lambda c: c["clarification_id"] not in self.pending_clarifications
                and c["answer"] is None
                and c["author"] != c["receiver"],
                api_data["clarifications"],
            )

            pending_counter = 0
            for pending in filtered_response:
                pending_counter += 1

                notification_embed = discord.Embed(colour=0x40C1F3)
                notification_embed.set_author(
                    name=f"{pending['author']}'s clarification:", icon_url=Icons.at_sign
                )

                notification_embed.add_field(
                    name="Contest:",
                    value=f"`{alias}`",
                    inline=False,
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
                view = discord.ui.View(timeout=None)
                view.has_alternate_button = False
                view.add_item(
                    AnswerButton(
                        view,
                        self.omegaup_client,
                        pending["clarification_id"],
                    )
                )
                await self.main_channel.send(embed=notification_embed, view=view)
                self.pending_clarifications.add(pending["clarification_id"])
            if pending_counter > 0:
                console.log(
                    f"{Bars.info}{Prompts.client} Found {pending_counter} clarification{'s' if pending_counter > 1 else ''}."
                )
            else:
                console.log(f"{Bars.info}{Prompts.client} No clarifications found.")


def get_token(name):
    token_value = os.getenv(name)
    if token_value is None:
        console.print(f"[red](!)[/] Environment variable [green]${name}[/] not found.")
        token_value = console.input(
            "[cyan](?)[/] Please provide your token: ", password=True
        )
    return token_value


if __name__ == "__main__":
    rich.traceback.install(show_locals=True)
    console.clear()

    OMEGAUP_TOKEN = get_token("OMEGAUP_API_TOKEN")
    DISCORD_TOKEN = get_token("HARMONY_TOKEN")

    console.print(f"[b #40c1f3]{banner}[/]")
    console.print("[cyan](i)[/] Establishing connections...")

    bot = HarmonyBot()
    bot.set_omegaup_token(OMEGAUP_TOKEN)

    async def available_problems(ctx: discord.AutocompleteContext):
        console.log(
            f"{Bars.info}{Prompts.discord} Command [green]/announce[/] autocompletion was triggered. Data:"
        )
        console.log(Panel(Pretty(ctx.interaction.to_dict(), indent_guides=True)))

        if len(bot.contest_problems) == 0:
            return []

        if ctx.interaction.channel_id != bot.main_channel.id:
            return []

        if ctx.options["contest_alias"] not in bot.contest_problems:
            return []

        return bot.contest_problems[ctx.options["contest_alias"]]

    async def available_contests(ctx: discord.AutocompleteContext):
        return bot.target_contests

    @bot.slash_command(
        description="Sends a new public clarification with the given message."
    )
    async def announce(
        ctx,
        contest_alias: discord.Option(
            str, autocomplete=discord.utils.basic_autocomplete(available_contests)
        ),
        problem_alias: discord.Option(
            str, autocomplete=discord.utils.basic_autocomplete(available_problems)
        ),
        content: str,
    ):
        console.log(
            f"{Bars.info}{Prompts.discord} Slash command was invoked. Interaction data:"
        )
        console.log(Panel(Pretty(ctx.interaction.to_dict(), indent_guides=True)))

        # Just in case ~
        if ctx.channel_id != bot.main_channel.id:
            await ctx.respond(
                "You can not do that here.", ephemeral=True, delete_after=3.0
            )

        bot.omegaup_client.post(
            f"{HarmonyBot.OMEGAUP_API_ENTRYPOINT}/clarification/create",
            params={
                "contest_alias": contest_alias,
                "message": content,
                "problem_alias": problem_alias,
                "username": HarmonyBot.omegaup_username,  # This makes it public automatically.
            },
        )

        await ctx.respond(
            f"{ctx.user.mention} has just made an announcement about `{problem_alias}`:\n```\n{content}\n```",
            allowed_mentions=discord.AllowedMentions.none(),
        )

    bot.run(DISCORD_TOKEN)
    console.print("[cyan](i)[/] Sayōnara!")


# ... This code hurts me in so many ways (but at least it works!)
