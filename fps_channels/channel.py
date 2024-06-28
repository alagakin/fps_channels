import inspect
import traceback
import tempfile
import dataframe_image as dtf
import telegram

from abc import ABC, abstractmethod
from typing import List, Union
from pandas import DataFrame
from telegram import Document, PhotoSize
from telegram.utils.types import FileInput
from tenacity import (RetryError, retry, retry_if_exception_type,
                      stop_after_attempt, wait_fixed)


class Channel(ABC):
    """
     Канал для отправки статистики.
     """
    SHOW_FILENAME = False
    HEADER = ""

    @abstractmethod
    def send_message(self, message: str):
        pass

    @abstractmethod
    def send_as_xmlx(self, stat: DataFrame, caption: str) -> None:
        ...

    @abstractmethod
    def send_df_as_png(self, stat: DataFrame, caption: str) -> None:
        ...

    @abstractmethod
    def send_exception(self, e: Exception) -> None:
        ...

    @staticmethod
    def _get_filename():
        stack = inspect.stack()
        caller_frame = stack[len(stack) - 1]
        return caller_frame.filename

    @staticmethod
    def _stat_to_png(cdr_stat: DataFrame):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            dtf.export(
                cdr_stat,
                filename=temp_file,
                table_conversion='matplotlib'
            )
            return temp_file.name


class TelegramChannel(Channel):
    """
    Канал для отправки статистики через Telegram.
    """

    MAX_TIMEOUT = 60

    def __init__(self, bot_token: str, chat_id: Union[str, int]) -> None:
        self.bot_token = bot_token
        self.chat_id = chat_id
        self._bot = telegram.Bot(self.bot_token)

    def send_df_as_png(self, stat: DataFrame, caption: str = "") -> None:
        f_name = self._stat_to_png(stat)
        with open(f_name, 'rb') as file:
            content = file.read()
        try:
            self._send_photo(
                chat_id=self.chat_id,
                photo=content,
                caption=caption
            )
        except RetryError:
            traceback.print_exc()

    def send_message(self, message: str) -> None:
        if not message:
            return
        try:
            if self.SHOW_FILENAME:
                file_name = self._get_filename()
                message = f"📂 file {file_name} \n {message}"

            if self.HEADER:
                message = self.HEADER + "\n" + message

            for sub_message in self._split_message(message):
                self._send_message(
                    chat_id=self.chat_id,
                    text=sub_message
                )
        except RetryError:
            traceback.print_exc()

    def send_exception(self, e: Exception) -> None:
        exception_text = self._get_exception_text(e)
        self.send_message(exception_text)

    def send_as_xmlx(self, stat: DataFrame, caption: str = ""):
        try:
            with tempfile.NamedTemporaryFile(delete=True, suffix=".xlsx") as temp_file:
                stat.to_excel(temp_file.name, index=False)
                self._send_document(
                    chat_id=self.chat_id,
                    document=temp_file.read(),
                    file_name=temp_file.name,
                    caption=caption
                )
        except RetryError:
            traceback.print_exc()

    @staticmethod
    def _split_message(message: str) -> List[str]:
        return [message[i: i + 4096] for i in range(0, len(message), 4096)]

    @staticmethod
    def _get_exception_text(e: Exception) -> str:
        return "".join(traceback.format_exception(type(e), e, e.__traceback__))

    @retry(
        wait=wait_fixed(5),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(telegram.error.NetworkError),
    )
    def _send_photo(
            self,
            chat_id: Union[int, str],
            photo: Union[FileInput, PhotoSize],
            caption: str,
    ) -> None:
        self._bot.send_photo(
            chat_id=chat_id,
            photo=photo,
            caption=caption,
            timeout=self.MAX_TIMEOUT
        )

    @retry(
        wait=wait_fixed(5),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(telegram.error.NetworkError),
    )
    def _send_document(
            self,
            chat_id: Union[int, str],
            document: Union[FileInput, Document],
            caption: str,
            file_name: str
    ) -> None:
        self._bot.send_document(
            chat_id=chat_id,
            document=document,
            filename=file_name,
            caption=caption,
            timeout=self.MAX_TIMEOUT
        )

    @retry(
        wait=wait_fixed(5),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(telegram.error.NetworkError),
    )
    def _send_message(
            self,
            chat_id: Union[int, str],
            text: str
    ) -> None:
        self._bot.send_message(
            chat_id=chat_id,
            text=text,
            timeout=self.MAX_TIMEOUT
        )
