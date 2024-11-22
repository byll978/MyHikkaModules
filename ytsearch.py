# ------------------------------------------------------------
# Module: YTSearch
# Description: Поиск видео в YouTube.
# Author: @kmodules
# ------------------------------------------------------------
# Licensed under the GNU AGPLv3
# https:/www.gnu.org/licenses/agpl-3.0.html
# ------------------------------------------------------------
# Author: @MeKsenon
# Commands: .ytsearch
# scope: hikka_only
# meta developer: @kmodules
# ------------------------------------------------------------

from .. import loader, utils
import requests
import io
import re
from telethon.tl.functions.channels import JoinChannelRequest

@loader.tds
class YouTubeSearchMod(loader.Module):
    """🎬 Модуль для поиска видео на YouTube"""
    
    strings = {
        "name": "YTSearch",
        "no_query": "🐣кажите поисковый запрос.",
        "no_results": "Ничего не найдено.",
        "processing": "<emoji document_id=5258274739041883702>🔍</emoji> <b>Ищу видео в YouTube...</b>"
    }
    
    async def client_ready(self, client, db):
        self.client = client
        await client(JoinChannelRequest("kmodules"))
    
    @loader.command()
    async def ytsearch(self, message):
        """ Поиск видео на YouTube. Использование: .ytsearch <запрос>"""
        
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings["no_query"])
            return

        await utils.answer(message, self.strings["processing"])
        
        try:
            search_url = f"https://www.youtube.com/results?search_query={args}"
            html = requests.get(search_url).text
            video_ids = re.findall(r"watch\?v=(\S{11})", html)
            
            if not video_ids:
                await utils.answer(message, self.strings["no_results"])
                return
                
            video_id = video_ids[0]
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            api_url = f"https://noembed.com/embed?url={video_url}"
            video_info = requests.get(api_url).json()
            
            title = video_info.get("title", "Название недоступно")
            author = video_info.get("author_name", "Автор недоступен")
            
            thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
            thumb_response = requests.get(thumbnail_url)
            if thumb_response.status_code == 404:
                thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
                thumb_response = requests.get(thumbnail_url)
                
            thumb_content = io.BytesIO(thumb_response.content)
            thumb_content.name = "thumbnail.jpg"
            
            caption = (
                f"<emoji document_id=5967816500415827773>💻</emoji> <b>{title}</b>\n"
                f"<emoji document_id=5879770735999717115>👤</emoji> <b>{author}</b>\n\n"
                f"<emoji document_id=5879883461711367869>⬇️</emoji> <b>URL: </b><code>{video_url}</code>"
            )
            
            await message.client.send_file(
                message.chat_id,
                thumb_content,
                caption=caption,
                parse_mode="html"
            )
            await message.delete()
            
        except Exception as e:
            await utils.answer(message, f"❌ Ошибка: {str(e)}")
          
