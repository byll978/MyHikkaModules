# ------------------------------------------------------------
# Module: RandomMemes
# Description: RandomMemes module with a 2 mode. 
# Author: @kmodules
# ------------------------------------------------------------
# Licensed under the GNU AGPLv3
# https:/www.gnu.org/licenses/agpl-3.0.html
# ------------------------------------------------------------
# Author: @MeKsenon
# Commands:
# scope: hikka_only
# meta developer: @kmodules
# ------------------------------------------------------------

from .. import loader, utils
from telethon.tl.functions.channels import JoinChannelRequest
import random

__version__ = (1, 0, 0)

@loader.tds
class RandomMemesModule(loader.Module):
    """2 mode random memes."""

    strings = {
        "name": "RandomMemes",
        "process": "<emoji document_id=5307675706283533118>🫥</emoji> <b>Forwarding random meme...</b>",
        "result": "<emoji document_id=5317003825494629922>😁</emoji> <b>Your random meme!</b>"
    }

    async def client_ready(self, client, db):
        self.client = client
        try:
            await client(JoinChannelRequest("kmodules"))
            await client(JoinChannelRequest("po_memes"))
            await client(JoinChannelRequest("prikoly_i_memy"))
        except Exception:
            pass

    async def _get_random_meme(self, channel):
        chat = await self.client.get_entity(channel)
        messages = await self.client.get_messages(chat, limit=300)
        media_messages = [msg for msg in messages if msg.media]
        
        if not media_messages:
            return None
            
        return random.choice(media_messages)

    @loader.command()
    async def rnmeme(self, message):
        """NSFW memes. """
        await utils.answer(message, self.strings["process"])
        
        random_msg = await self._get_random_meme("po_memes")
        
        if not random_msg:
            return await utils.answer(message, "<emoji document_id=5240241223632954241>🚫</emoji> <b>Error occured while getting random meme. How?</b>")
        
        await message.respond(file=random_msg.media, message=self.strings["result"])
        await message.delete()

    @loader.command()
    async def rmeme(self, message):
        """Safe memes."""
        await utils.answer(message, self.strings["process"])
        
        random_msg = await self._get_random_meme("prikoly_i_memy")
        
        if not random_msg:
            return await utils.answer(message, "<emoji document_id=5240241223632954241>🚫</emoji> <b>Error occured while getting random meme. How?</b>")
        
        await message.respond(file=random_msg.media, message=self.strings["result"])
        await message.delete()
      
