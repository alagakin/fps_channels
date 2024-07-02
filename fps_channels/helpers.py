import inspect
import tempfile
import traceback
from typing import List

import dataframe_image as dtf

from pandas import DataFrame


def get_current_file_name() -> str:
    stack = inspect.stack()
    caller_frame = stack[len(stack) - 1]
    return caller_frame.filename


def df_to_png(df: DataFrame) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
        dtf.export(
            df,
            filename=temp_file,
            table_conversion='matplotlib'
        )
        return temp_file.name


def split_telegram_message(message: str) -> List[str]:
    return [message[i: i + 4096] for i in range(0, len(message), 4096)]


def get_exception_text(e: Exception) -> str:
    return "".join(traceback.format_exception(type(e), e, e.__traceback__))
