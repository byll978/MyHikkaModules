# ------------------------------------------------------------
# Module: CopyUser
# Description: One command, and you are already another.
# Author: @kmodules
# ------------------------------------------------------------
# Licensed under the GNU AGPLv3
# https:/www.gnu.org/licenses/agpl-3.0.html
# ------------------------------------------------------------
# Author: @MeKsenon
# Commands: .copyuser .restoreme .backupme
# scope: hikka_only
# meta developer: @kmodules
# ------------------------------------------------------------

from .. import loader, utils
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.errors import UsernameNotOccupiedError, UsernameInvalidError, ImageProcessFailedError
import io

__version__ (1, 0, 2)

@loader.tds
class UserProfileModule(loader.Module):
    """Модуль чтобы копировать других пользователей."""

    strings = {"name": "CopyUser"}
    
    def __init__(self):
        self.config = loader.ModuleConfig(
            "backup_data", {},
            lambda: "Stored backup data"
        )

    async def client_ready(self, client, db):
        self.client = client
        await self.client(JoinChannelRequest("kmodules"))

    @loader.command()
    async def copyuser(self, message):
        """Копировать профиль пользователя.
        Use: .copyuser <username>"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "<emoji document_id=5832251986635920010>➡️</emoji><b>Provide username after command!</b>")
            return

        try:
            user = await message.client.get_entity(args)
            full_user = await message.client(GetFullUserRequest(user.id))
            
            try:
                photos = await message.client.get_profile_photos('me')
                if photos:
                    await message.client(DeletePhotosRequest(photos))
                
                photo = await message.client.download_profile_photo(user)
                if photo:
                    await message.client(UploadProfilePhotoRequest(
                        await message.client.upload_file(photo)
                    ))
            except Exception as e:
                await utils.answer(message, f"<emoji document_id=5210952531676504517>❌</emoji> <b>Error with avatar: {str(e)}</b>")
           
            await message.client(UpdateProfileRequest(
                first_name=user.first_name or "",
                last_name=user.last_name or "",
                about=full_user.full_user.about or ""
            ))
            
            await utils.answer(message, "<emoji document_id=5397916757333654639>➕</emoji> <b>Профиль успешно скопирован!</b>")
        except UsernameNotOccupiedError:
            await utils.answer(message, "<emoji document_id=5240241223632954241>🚫</emoji> <b>Юзера с таким юзернеймом не найдено!</b>")
        except UsernameInvalidError:
            await utils.answer(message, "<emoji document_id=5240241223632954241>🚫</emoji> <b>Неправильный формат юзернейма.</b>")
        except Exception as e:
            await utils.answer(message, f"😵 Ошибка: {str(e)}")

    @loader.command()
    async def backupme(self, message):
        """Создать бэкап данного профиля"""
        try:
            me = await self.client.get_me()
            full_user = await self.client(GetFullUserRequest(me.id))
            
            backup_data = {
                "first_name": me.first_name or "",
                "last_name": me.last_name or "", 
                "about": full_user.full_user.about or "",
            }
            
            try:
                photo = await self.client.download_profile_photo('me')
                if photo:
                    with open(photo, 'rb') as f:
                        backup_data["avatar"] = f.read().hex()
            except Exception:
                backup_data["avatar"] = None

            self.config["backup_data"] = backup_data
            
            await utils.answer(
                message,
                "<emoji document_id=5294096239464295059>🔵</emoji> <b>Ваш данный профиль сохранен. Вы можете вернуть его используя</b> <code>restoreme</code>"
            )

        except Exception as e:
            await utils.answer(message, f"😵 Ошибка: {str(e)}")

    @loader.command() 
    async def restoreme(self, message):
        """Восстановить старый профиль"""
        try:
            backup = self.config["backup_data"]
            if not backup:
                await utils.answer(message, "❌ <b>Нет сохраненных данных!</b>")
                return

            if backup.get("avatar"):
                try:
                    photos = await self.client.get_profile_photos('me')
                    if photos:
                        await self.client(DeletePhotosRequest(photos))
                    
                    avatar_bytes = bytes.fromhex(backup["avatar"])
                    await self.client(UploadProfilePhotoRequest(
                        await self.client.upload_file(io.BytesIO(avatar_bytes))
                    ))
                except Exception as e:
                    await utils.answer(message, f"<emoji document_id=5210952531676504517>❌</emoji> <b>Ошибка при установлении аватарки: {str(e)}</b>")

            await self.client(UpdateProfileRequest(
                first_name=backup["first_name"],
                last_name=backup["last_name"],
                about=backup["about"]
            ))

            await utils.answer(
                message,
                "<emoji document_id=5294096239464295059>🔵</emoji> <b>Ваш прошлый профиль возвращен.</b>"
            )

        except Exception as e:
            await utils.answer(message, f"😵 Ошибка: {str(e)}")
