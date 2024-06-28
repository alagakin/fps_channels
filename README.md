# A package for convenient sending errors/messages

As for now fps_channels supports sending data through Telegram in formats such as .xlsx, .png, plain text.

## Example



```
class TelegramAlertChannel(TelegramChannel):
    SHOW_FILENAME = True
    HEADER = "️🆘️ Header text"

alert_channel = TelegramAlertChannel(
    bot_token="bot:token",
    chat_id=12345
)
```


