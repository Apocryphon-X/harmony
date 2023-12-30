import discord
from log_components import *


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

        self.console.log(
            f"{Bars.success}{Prompts.omegaup} Clarification #{self.clarification_id} is now {message}."
        )
        await interaction.message.edit(view=self.parent_view)
        await interaction.response.send_message(
            f"Clarification #{self.clarification_id} is now {message}.",
            ephemeral=True,
            delete_after=5,
        )

