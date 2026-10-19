import asyncio

def chunk_message(text: str, max_len: int):
    buffer = ""
    for line in text.splitlines(keepends=True):
        if len(buffer) + len(line) > max_len:
            yield buffer
            buffer = ""
        buffer += line
    if buffer:
        yield buffer


async def send_long(channel, text, max_len):
    for i, part in enumerate(chunk_message(text, max_len)):
        if i > 0:
            part = "-\n" + part
        await channel.send(part)
        await asyncio.sleep(0.2)