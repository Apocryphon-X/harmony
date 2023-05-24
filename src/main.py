# NOTE: This code will be refactored someday (probably soon).
# I know it's kinda* messy, but in the end deadlines are deadlines.

import os

from datetime import datetime
from dataclasses import dataclass

import discord
import requests
import rich.traceback

from discord.ext import tasks

from rich.console import Console
from rich.control import Control
from rich.panel import Panel
from rich.pretty import Pretty

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


class AlternateButton(discord.ui.Button):
    def __init__(
        self,
        parent_view,
        omegaup_client,
        clarification_id,
    ):
        super().__init__(label="Make Public", style=discord.ButtonStyle.danger)
        self.will_make_public = True
        self.parent_view = parent_view
        self.omegaup_client = omegaup_client
        self.clarification_id = clarification_id

    async def callback(self, interaction: discord.Interaction):
        console.log(f"{Bars.info}{Prompts.discord} Interaction received:")
        console.log(Panel(Pretty(interaction.to_dict(), indent_guides=True)))
        self.omegaup_client.post(
            "https://omegaup.com/api/clarification/update",
            data={
                "clarification_id": self.clarification_id,
                "public": str(self.will_make_public).lower(),
            },
        )
        message = "public" if self.will_make_public else "private"

        self.will_make_public = not self.will_make_public
        if self.will_make_public:
            self.label = "Make Public"
            self.style = discord.ButtonStyle.danger
        else:
            self.label = "Make Private"
            self.style = discord.ButtonStyle.green

        console.log(
            f"{Bars.success}{Prompts.omegaup} Clarification #{self.clarification_id} is now {message}."
        )
        await interaction.message.edit(view=self.parent_view)
        await interaction.response.send_message(
            f"Clarification #{self.clarification_id} is now {message}.",
            ephemeral=True,
            delete_after=5,
        )


class AnswerModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs):
        self.parent_view = kwargs.pop("parent_view")
        self.omegaup_client = kwargs.pop("omegaup_client")
        self.clarification_id = kwargs.pop("clarification_id")
        self.answer_button = kwargs.pop("answer_button")
        super().__init__(*args, **kwargs)
        self.add_item(
            discord.ui.InputText(
                label="What will your answer be?", style=discord.InputTextStyle.long
            )
        )

    async def callback(self, interaction: discord.Interaction):
        console.log(
            f"{Bars.success}{Prompts.omegaup} Sending clarification #{self.clarification_id} answer."
        )
        self.answer_button.label = "Update answer"
        self.answer_button.disabled = False

        modal_answer = self.children[0].value
        self.omegaup_client.post(
            "https://omegaup.com/api/clarification/update",
            data={"clarification_id": self.clarification_id, "answer": modal_answer},
        )
        await interaction.response.send_message(
            content="Answer sent.", delete_after=3.0, ephemeral=True
        )
        new_embed = interaction.message.embeds[0]
        new_embed.colour = 0x2B2D31

        # Last index twice, not sure if works with -1 (untested)
        new_embed.remove_field(3)
        new_embed.remove_field(3)

        new_embed.add_field(
            name="Answer:",
            value=f"```\n{modal_answer}\n```",
            inline=False,
        )
        new_embed.add_field(
            name="Responded by:",
            value=interaction.user.mention,
        )
        if not self.parent_view.has_alternate_button:
            self.parent_view.add_item(
                AlternateButton(
                    self.parent_view,
                    self.omegaup_client,
                    self.clarification_id,
                )
            )
            self.parent_view.has_alternate_button = True
        await interaction.message.edit(embed=new_embed, view=self.parent_view)


class AnswerButton(discord.ui.Button):
    def __init__(
        self,
        parent_view,
        omegaup_client,
        clarification_id,
    ):
        super().__init__(label="Respond", style=discord.ButtonStyle.blurple)
        self.parent_view = parent_view
        self.omegaup_client = omegaup_client
        self.clarification_id = clarification_id

    async def callback(self, interaction: discord.Interaction):
        console.log(f"{Bars.info}{Prompts.discord} Interaction received:")
        console.log(Panel(Pretty(interaction.to_dict(), indent_guides=True)))
        self.disabled = True
        await interaction.message.edit(view=self.parent_view)
        await interaction.response.send_modal(
            AnswerModal(
                parent_view=self.parent_view,
                omegaup_client=self.omegaup_client,
                clarification_id=self.clarification_id,
                answer_button=self,
                title="Answer submission",
            )
        )
        await interaction.message.edit(view=self.parent_view)


class HarmonyBot(discord.Bot):
    OMEGAUP_API_ENTRYPOINT = "https://omegaup.com/api"
    pending_clarifications = set()
    has_target_data = False
    target_contest = ...
    omegaup_username = ...
    # omegaup_client = ... # This needs to be static. Defined on `set_omegaup_token()`

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

        # self.__class__.omegaup_client = self.omegaup_client

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

            self.__class__.target_contest = self.target_contest

            console.control(Control.move_to_column(0, -1))
            console.log(
                f"{Bars.success}{Prompts.client} Contest alias was stored successfully."
            )
            self.clarifications_monitor.start()

    @tasks.loop(seconds=10)
    async def clarifications_monitor(self):
        console.log(
            f"{Bars.info}{Prompts.client} Looking for pending [u]UNREGISTERED[/] clarifications..."
        )
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
            and c["answer"] is None
            and c["author"] != c["receiver"],
            api_data["clarifications"],
        )
        pending_counter = 0
        for pending in filtered_response:
            pending_counter += 1

            notification_embed = discord.Embed(colour=0x40C1F3)
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
    console.clear()

    OMEGAUP_TOKEN = get_token("OMEGAUP_API_TOKEN")
    DISCORD_TOKEN = get_token("HARMONY_TOKEN")

    console.print(f"[b #40c1f3]{banner}[/]")
    console.print("[cyan](i)[/] Establishing connections...")

    bot = HarmonyBot()
    bot.set_omegaup_token(OMEGAUP_TOKEN)

    async def available_problems(ctx: discord.AutocompleteContext):
        api_response = bot.omegaup_client.get(
            f"{bot.OMEGAUP_API_ENTRYPOINT}/contest/problems",
            params={"contest_alias": HarmonyBot.target_contest},
        ).json()

        if "error" in api_response:
            return []

        return [problem["alias"] for problem in api_response["problems"]]

    @bot.slash_command(
        description="Sends a new public clarification with the given message."
    )
    async def announce(
        ctx,
        problem_alias: discord.Option(
            str, autocomplete=discord.utils.basic_autocomplete(available_problems)
        ),
        content: str,
    ):
        bot.omegaup_client.post(
            f"{HarmonyBot.OMEGAUP_API_ENTRYPOINT}/clarification/create",
            params={
                "contest_alias": HarmonyBot.target_contest,
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


# ... This code hurts me in so many ways
