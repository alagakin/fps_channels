# A package for convenient sending errors/messages

As for now fps_channels supports sending data through Telegram in formats such as .xlsx, .png, plain text.

It supports both async and sync sending.

## Example (sync)



```
class TelegramAlertChannel(TelegramChannel):
    SHOW_FILENAME = True
    HEADER = "️🆘️ Header text"

alert_channel = TelegramAlertChannel(
    bot_token="bot:token",
    chat_id=12345
)
alert_channel.send_message("Message")
```

## Example (async)



```
class AsyncTelegramAlertChannel(AsyncTelegramChannel):
    SHOW_FILENAME = True
    HEADER = "️🆘️ Header text"

async alert_channel = AsyncTelegramAlertChannel(
    bot_token="bot:token",
    chat_id=12345
)
await alert_channel.send_message("Message")
```

