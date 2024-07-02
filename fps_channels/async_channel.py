import traceback
import aiohttp
import requests
from typing import Union
from pandas import DataFrame
from tenacity import (RetryError, retry, retry_if_exception_type,
                      stop_after_attempt, wait_fixed)

from .abs_channel import AbstractChannel
from .exceptions import TelegramException
from .helpers import get_current_file_name, df_to_png, split_telegram_message, get_exception_text


class AsyncTelegramChannel(AbstractChannel):
    """
    Канал для отправки статистики через Telegram.
    """
    MAX_TIMEOUT = 60

    def __init__(self, bot_token: str, chat_id: Union[str, int]) -> None:
        self.bot_token = bot_token
        self.chat_id = chat_id

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

    def send_as_xmlx(self, stat: DataFrame, caption: str) -> None:
        pass

    def send_df_as_png(self, stat: DataFrame, caption: str) -> None:
        pass

    def send_exception(self, e: Exception) -> None:
        pass

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
        async with aiohttp.ClientSession(connector=conn) as session:
            url = f'https://api.telegram.org/bot{self.bot_token}/sendMessage'
            data = {
                'chat_id': self.chat_id,
                'text': text
            }
            async with session.post(url, json=data) as response:
                if response.status != 200:
                    raise TelegramException(response.text)
