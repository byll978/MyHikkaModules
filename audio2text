# ------------------------------------------------------------
# Module: Audio2Text
# Description: Модуль для распознования текста из аудио.
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
import requests
import asyncio
from telethon.tl.functions.channels import JoinChannelRequest

@loader.tds
class Audio2TextMod(loader.Module):
    """Модуль для распознования текста из аудио."""

    strings = {
        "name": "Audio2Text",
        "processing": "<emoji document_id=5332600281970517875>🫥</emoji> <b>Распознаю текст из аудио...</b>",
        "success": "<emoji document_id=5897554554894946515>🎤</emoji> <b>Текст распознан!</b>\n\n<emoji document_id=6048354593279053992>🗣</emoji> <code>{}</code>",
        "no_reply": "Ответьте на аудиосообщение!",
        "error": "Произошла ошибка!"
    }

    async def client_ready(self, client, db):
        self.client = client
        try:
            await client(JoinChannelRequest("kmodules"))
        except Exception:
            pass

    @loader.command()
    async def audio2text(self, message):
        """Преобразовать аудио в текст (ответом на аудиосообщение)"""
        reply = await message.get_reply_message()
        if not reply or not reply.media:
            await utils.answer(message, self.strings["no_reply"])
            return

        await utils.answer(message, self.strings["processing"])

        try:
            audio_data = await reply.download_media(bytes)
            
            files = {'audio': ('audio.mp3', audio_data, 'audio/mp3')}
            response = requests.post(
                "http://theksenon.pro/api/audio2text/generate",
                files=files
            )

            if response.status_code == 200:
                result = response.json()
                if 'text' in result:
                    await utils.answer(
                        message,
                        self.strings["success"].format(result['text'])
                    )
                else:
                    await utils.answer(message, self.strings["error"])
            else:
                await utils.answer(message, self.strings["error"])
                
        except Exception as e:
            await utils.answer(message, f"{self.strings['error']}: {str(e)}")
