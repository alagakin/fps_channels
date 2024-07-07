import traceback
import tempfile
import requests
from typing import Union
from pandas import DataFrame
from tenacity import (RetryError, retry, retry_if_exception_type,
                      stop_after_attempt, wait_fixed)

from .abs_channel import AbstractChannel
from .exceptions import TelegramException
from .helpers import get_current_file_name, df_to_png, split_telegram_message, get_exception_text


class TelegramChannel(AbstractChannel):
    MAX_TIMEOUT = 60

    def __init__(self, bot_token: str, chat_id: Union[str, int]) -> None:
        self.bot_token = bot_token
        self.chat_id = chat_id

    def send_as_png(self, df: DataFrame, caption: str = "") -> None:
        f_name = df_to_png(df)
        try:
            caption = self._prepare_message(caption)
            self._send_photo(f_name, caption)
        except RetryError:
            traceback.print_exc()

    def send_message(self, message: str) -> None:
        if not message:
            return
        try:
            message = self._prepare_message(message)
            for sub_message in split_telegram_message(message):
                self._send_message(
                    text=sub_message
                )
        except RetryError:
            traceback.print_exc()

    def _prepare_message(self, message: str):
        if self.SHOW_FILENAME:
            file_name = get_current_file_name()
            message = f"📂 file {file_name} \n{message}"

        if self.HEADER:
            message = self.HEADER + "\n" + message

        return message

    def send_exception(self, e: Exception, caption: str = "") -> None:
        exception_text = get_exception_text(e)
        if caption:
            full_text = "📝 " + caption + "\n" + exception_text
        else:
            full_text = exception_text
        self.send_message(full_text)

    def send_as_xmlx(self, df: DataFrame, caption: str = ""):
        try:
            with tempfile.NamedTemporaryFile(delete=True, suffix=".xlsx") as temp_file:
                df.to_excel(temp_file.name, index=False)
                caption = self._prepare_message(caption)
                self._send_document(
                    document_path=temp_file.name,
                    caption=caption
                )
        except TelegramException:
            traceback.print_exc()

    @retry(
        wait=wait_fixed(5),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(TelegramException),
        reraise=True
    )
    def _send_photo(
            self,
            photo_path: str,
            caption: str,
    ) -> None:
        with open(photo_path, 'rb') as file:
            content = file.read()
            url = f'https://api.telegram.org/bot{self.bot_token}/sendPhoto'
            files = {'photo': content}
            data = {'chat_id': self.chat_id, 'caption': caption}
            response = requests.post(url, files=files, data=data)
            if response.status_code != 200:
                raise TelegramException(response.text)

    @retry(
        wait=wait_fixed(5),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(TelegramException),
        reraise=True
    )
    def _send_document(
            self,
            document_path: str,
            caption: str
    ) -> None:
        with open(document_path, 'rb') as file:
            content = file.read()
            url = f'https://api.telegram.org/bot{self.bot_token}/sendDocument'
            files = {'document': (file.name, content)}
            data = {'chat_id': self.chat_id, 'caption': caption}
            response = requests.post(url, files=files, data=data, timeout=self.MAX_TIMEOUT)
            if response.status_code != 200:
                raise TelegramException(response.text)

    @retry(
        wait=wait_fixed(5),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(TelegramException),
        reraise=True
    )
    def _send_message(
            self,
            text: str
    ) -> None:
        url = f'https://api.telegram.org/bot{self.bot_token}/sendMessage'
        data = {
            'chat_id': self.chat_id,
            'text': text
        }
        response = requests.post(url, data=data)
        if response.status_code != 200:
            raise TelegramException(response.text)
