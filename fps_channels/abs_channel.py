from abc import abstractmethod, ABC

from pandas import DataFrame

from fps_channels.helpers import get_current_file_name


class AbstractChannel(ABC):
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
    def send_as_png(self, stat: DataFrame, caption: str) -> None:
        ...

    @abstractmethod
    def send_exception(self, e: Exception) -> None:
        ...

    def _prepare_message(self, message: str) -> str:
        if self.SHOW_FILENAME:
            file_name = get_current_file_name()
            message = f"📂 file {file_name} \n{message}"

        if self.HEADER:
            message = self.HEADER + "\n" + message

        return message
