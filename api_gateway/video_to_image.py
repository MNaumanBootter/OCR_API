from decord import VideoReader
from decord import cpu


async def convert_video_to_images(video_file):
    vr = VideoReader(video_file, ctx=cpu(0))
    return vr