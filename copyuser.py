# ------------------------------------------------------------
# Module: CopyUser
# Description: One command, and you are already another.
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
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest
from telethon.errors import UsernameNotOccupiedError, UsernameInvalidError, ImageProcessFailedError
import io
import requests
from telethon.tl.functions.channels import JoinChannelRequest

__version__ = (1, 0, 5)

@loader.tds
class ProfileToolsModule(loader.Module):
    strings = {"name": "CopyUser"}

    def __init__(self):
        self.name = self.strings["name"]
        self._backup_data = None

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        await self.client(JoinChannelRequest("kmodules"))

    async def upload_to_0x0(self, photo_bytes):
        try:
            files = {'file': ('photo.png', photo_bytes)}
            response = requests.post(
                'https://0x0.st',
                files=files,
                data={'secret': True}
            )
            return response.text.strip()
        except Exception as e:
            return f"Ошибка: {str(e)}"

    @loader.command()
    async def copyuser(self, message):
        """Скопировать профиль пользователя"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "<emoji document_id=5832251986635920010>➡️</emoji><b>Укажите юзернейм после команды!</b>")
            return

        try:
            user = await message.client.get_entity(args)
            full_user = await message.client(GetFullUserRequest(user.id))
            
            if full_user.full_user.profile_photo:
                try:
                    avatar = await message.client.download_profile_photo(user, bytes)
                    if avatar:
                        photos = await message.client.get_profile_photos('me')
                        await message.client(DeletePhotosRequest(photos))
                        
                        await message.client(UploadProfilePhotoRequest(
                            file=await message.client.upload_file(io.BytesIO(avatar))
                        ))
                        await utils.answer(message, "<emoji document_id=5879770735999717115>👤</emoji><b>Аватар изменен.</b>")
                    else:
                        await utils.answer(message, "<emoji document_id=5210952531676504517>❌</emoji> <b>Ошибка при изменении аватара.</b>")
                except ImageProcessFailedError:
                    await utils.answer(message, "<emoji document_id=5210952531676504517>❌</emoji> <b>Ошибка при обработке аватара.</b>")
            else:
                await utils.answer(message, "<emoji document_id=5240241223632954241>🚫</emoji> <b>У пользователя нет аватара!</b>")
            
            await message.client(UpdateProfileRequest(
                first_name=user.first_name or "",
                last_name=user.last_name or "",
                about=full_user.full_user.about or ""
            ))
            
            await utils.answer(message, "<emoji document_id=5397916757333654639>➕</emoji> <b>Профиль пользователя скопирован!</b>")
        except UsernameNotOccupiedError:
            await utils.answer(message, "<emoji document_id=5240241223632954241>🚫</emoji> <b>Пользователь с таким юзернеймом не найден!</b>")
        except UsernameInvalidError:
            await utils.answer(message, "<emoji document_id=5240241223632954241>🚫</emoji> <b>Неверный формат юзернейма.</b>")
        except Exception as e:
            await utils.answer(message, f"😵 Ошибка: {str(e)}")

    @loader.command()
    async def backupme(self, message):
        """Сделать резервную копию профиля"""
        try:
            user = await self.client.get_me()
            full_user = await self.client(GetFullUserRequest(user.id))
            
            avatar_url = None
            photos = await self.client.get_profile_photos('me')
            if photos:
                avatar_bytes = await self.client.download_profile_photo('me', bytes)
                avatar_url = await self.upload_to_0x0(avatar_bytes)

            backup_data = {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "about": full_user.full_user.about,
                "avatar_url": avatar_url
            }
            
            self.db.set("BackupProfile", "backup_data", backup_data)
            
            await utils.answer(
                message,
                f"<emoji document_id=5294096239464295059>🔵</emoji> <b>Ваш данный профиль сохранен. Вы можете вернуть его используя</b> <code>restoreme</code>\n\n<b>⚙️ URL данной Аватарки: {avatar_url}</b>"
            )

        except Exception as e:
            await utils.answer(message, f"😵 Ошибка: {str(e)}")

    @loader.command()
    async def restoreme(self, message):
        """Восстановить профиль из резервной копии"""
        try:
            backup_data = self.db.get("BackupProfile", "backup_data")
            
            if not backup_data:
                await utils.answer(message, "❌ <b>Резервная копия не найдена!</b>")
                return

            if backup_data.get("avatar_url"):
                try:
                    photos = await self.client.get_profile_photos('me')
                    await self.client(DeletePhotosRequest(photos))
                    
                    response = requests.get(backup_data["avatar_url"])
                    avatar_bytes = io.BytesIO(response.content)
                    
                    await self.client(UploadProfilePhotoRequest(
                        file=await self.client.upload_file(avatar_bytes)
                    ))
                except ImageProcessFailedError:
                    await utils.answer(message, "❌ <b>Не удалось восстановить аватар</b>")

            await self.client(UpdateProfileRequest(
                first_name=backup_data.get("first_name", ""),
                last_name=backup_data.get("last_name", "") or "",
                about=backup_data.get("about", "")
            ))

            await utils.answer(
                message,
                "<emoji document_id=5294096239464295059>🔵</emoji> <b>Ваш прошлый профиль возвращен.</b>"
            )

        except Exception as e:
            await utils.answer(message, f"😵 Ошибка: {str(e)}")
