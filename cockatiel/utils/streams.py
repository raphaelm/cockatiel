def chunks(stream, chunk_size=1024):
    while True:
        chunk = stream.read(chunk_size)
        if not chunk:
            break
        yield chunk
