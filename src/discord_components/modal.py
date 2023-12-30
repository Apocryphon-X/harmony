import discord
from log_components import *

from .alternate_button import AlternateButton


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
        # self.answer_button.disabled = False

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

        # Remove the last index twice, not sure if it works with -1 (untested)
        new_embed.remove_field(4)
        new_embed.remove_field(4)

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
