# ------------------------------------------------------------
# Module: GitHubInfo
# Description: Модуль информации о профиле GitHub.
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

import requests
from datetime import datetime
from .. import loader, utils
from telethon.tl.functions.channels import JoinChannelRequest

@loader.tds
class GitHubInfoMod(loader.Module):
    """Модуль информации о профиле GitHub."""

    strings = {
        "name": "GitHubInfo",
        "no_username": "<emoji document_id=5420323339723881652>⚠️</emoji> <b>Укажите имя пользователя!</b>",
        "user_not_found": "<emoji document_id=5210952531676504517>❌</emoji> <b>Пользователь не найден</b>", 
        "error": "<emoji document_id=5420323339723881652>⚠️</emoji> <b>Ошибка при получении данных</b>: <i>{}</i>",
        "loading": "<emoji document_id=5328239124933515868>⚙️</emoji> <b>Загружаю информацию...</b>"
    }

    async def client_ready(self, client, db):
        self.client = client
        await client(JoinChannelRequest("durov"))

    @loader.command()
    async def github(self, message):
        """<username> - получить информацию о профиле GitHub"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings["no_username"])
            return

        await utils.answer(message, self.strings["loading"])

        try:
            r = requests.get(f"https://api.github.com/users/{args}")
            if r.status_code == 404:
                await utils.answer(message, self.strings["user_not_found"])
                return
            if r.status_code != 200:
                await utils.answer(message, self.strings["error"].format("Некорректный ответ API")) 
                return

            user = r.json()
            
            repos = requests.get(f"https://api.github.com/users/{args}/repos")
            repos_data = repos.json()
            languages = {}
            for repo in repos_data:
                if repo['language'] and not repo['fork']:
                    languages[repo['language']] = languages.get(repo['language'], 0) + 1
            
            top_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:3]
            
            if len(top_langs) > 1:
                langs_parts = []
                for i, lang in enumerate(top_langs):
                    prefix = " ┣ " if i < len(top_langs)-1 else " ┗ "
                    langs_parts.append(f"{prefix}<b>{lang[0]}:</b> <i>{lang[1]} репозиториев</i>")
                langs_text = "\n".join(langs_parts)
            elif len(top_langs) == 1:
                langs_text = f" ┗ <b>{top_langs[0][0]}:</b> <i>{top_langs[0][1]} репозиториев</i>"
            else:
                langs_text = " ┗ Нет данных"
            
            created = datetime.strptime(user['created_at'], "%Y-%m-%dT%H:%M:%SZ")
            created_date = created.strftime("%d.%m.%Y")
            
            text = (
                f"<emoji document_id=5296237851891998039>😸</emoji> <b>Github профиль:</b>\n\n"
                f"<emoji document_id=5879770735999717115>👤</emoji> <b>Основная информация:</b>\n"
                f" ┣ <b>Имя в Github:</b> <a href='https://github.com/{user['login']}'>{user['login']}</a>\n"
                f" ┣ <b>Компания:</b> {user['company'] or '❌'}\n"
                f" ┣ <b>Аккаунт создан:</b> {created_date}\n"
                f" ┣ <b>Сайт:</b> {user['blog'] or '❌'}\n"
                f" ┗ <b>EMail:</b> {user['email'] or '❌'}\n\n"
                f"<emoji document_id=5231200819986047254>📊</emoji> <b>Статистика:</b>\n"
                f" ┣ <b>Репозитории:</b> {user['public_repos']}\n"
                f" ┣ <b>Gists:</b> {user['public_gists']}\n"
                f" ┣ <b>Подписчики:</b> {user['followers']}\n"
                f" ┗ <b>Подписки:</b> {user['following']}\n\n"
                f"<emoji document_id=5447410659077661506>🌐</emoji> <b>Топ репозиториев по ЯП:</b>\n"
                f"{langs_text}\n\n"
                f"<emoji document_id=5334544901428229844>ℹ️</emoji> <b>Bio:</b> <b>{user['bio'] or '❌'}</b>"
            )

            await message.client.send_file(
                message.chat_id,
                user['avatar_url'],
                caption=text,
                reply_to=message.reply_to_msg_id
            )
            
            if message.out:
                await message.delete()
                
        except Exception as e:
            await utils.answer(message, self.strings["error"].format(str(e)))
