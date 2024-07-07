import tempfile
import traceback
import aiohttp

from typing import Union
from pandas import DataFrame
from tenacity import (RetryError, retry, retry_if_exception_type,
                      stop_after_attempt, wait_fixed)

from .abs_channel import AbstractChannel
from .exceptions import TelegramException
from .helpers import df_to_png, split_telegram_message, get_exception_text


class AsyncTelegramChannel(AbstractChannel):
    """
    Канал для отправки статистики через Telegram.
    """
    MAX_TIMEOUT = 60

    def __init__(self, bot_token: str, chat_id: Union[str, int]) -> None:
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.timeout = aiohttp.ClientTimeout(
            total=10,
            connect=3
        )

    async def send_message(self, message: str) -> None:
        if not message:
            return
        try:
            message = self._prepare_message(message)
            for sub_message in split_telegram_message(message):
                await self._send_message(
                    text=sub_message
                )
        except RetryError:
            traceback.print_exc()

    async def send_as_png(self, df: DataFrame, caption: str = "") -> None:
        f_name = df_to_png(df)
        try:
            caption = self._prepare_message(caption)
            await self._send_photo(f_name, caption)
        except RetryError:
            traceback.print_exc()

    async def send_as_xmlx(self, df: DataFrame, caption: str = "") -> None:
        try:
            with tempfile.NamedTemporaryFile(delete=True, suffix=".xlsx") as temp_file:
                df.to_excel(temp_file.name, index=False)
                caption = self._prepare_message(caption)
                await self._send_document(
                    document_path=temp_file.name,
                    caption=caption
                )
        except TelegramException:
            traceback.print_exc()

    async def send_exception(self, e: Exception, caption: str = "") -> None:
        exception_text = get_exception_text(e)
        if caption:
            full_text = "📝 " + caption + "\n" + exception_text
        else:
            full_text = exception_text
        await self.send_message(full_text)

    @retry(
        wait=wait_fixed(5),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(TelegramException),
        reraise=True
    )
    async def _send_message(
            self,
            text: str
    ) -> None:
        conn = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=conn, timeout=self.timeout) as session:
            url = f'https://api.telegram.org/bot{self.bot_token}/sendMessage'
            data = {
                'chat_id': self.chat_id,
                'text': text
            }
            async with session.post(url, json=data) as response:
                if response.status != 200:
                    raise TelegramException(response.text)

    @retry(
        wait=wait_fixed(5),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(TelegramException),
        reraise=True
    )
    async def _send_photo(
            self,
            photo_path: str,
            caption: str,
    ) -> None:
        conn = aiohttp.TCPConnector(ssl=False)
        with open(photo_path, 'rb') as file:
            async with aiohttp.ClientSession(connector=conn, timeout=self.timeout) as session:
                url = f'https://api.telegram.org/bot{self.bot_token}/sendPhoto'
                data = aiohttp.FormData()
                data.add_field('chat_id', str(self.chat_id))
                data.add_field('caption', caption)
                data.add_field('photo', file)

                async with session.post(url, data=data) as response:
                    if response.status != 200:
                        raise TelegramException(response.text)

    @retry(
        wait=wait_fixed(5),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(TelegramException),
        reraise=True
    )
    async def _send_document(
            self,
            document_path: str,
            caption: str
    ) -> None:
        conn = aiohttp.TCPConnector(ssl=False)
        with open(document_path, 'rb') as file:
            async with aiohttp.ClientSession(connector=conn, timeout=self.timeout) as session:
                url = f'https://api.telegram.org/bot{self.bot_token}/sendDocument'
                data = aiohttp.FormData()
                data.add_field('chat_id', str(self.chat_id))
                data.add_field('caption', caption)
                data.add_field('document', file, filename=file.name)

                async with session.post(url, data=data) as response:
                    if response.status != 200:
                        raise TelegramException(response.text)
