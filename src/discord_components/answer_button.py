import discord
from log_components import *

from .modal import AnswerModal


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
        # self.disabled = True
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

