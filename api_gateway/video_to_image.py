from decord import VideoReader
from decord import cpu
from io import BytesIO


async def convert_video_to_images(video_bytes):
    video_file_bytesio = BytesIO(video_bytes)
    vr = VideoReader(video_file_bytesio, ctx=cpu(0))
    return vr