from fastapi import UploadFile
from config import app_config
import aiohttp
from timeloop import Timeloop
import requests
from datetime import timedelta

timeloop_app = Timeloop()


async def call_videos_api(videos: list[UploadFile], user_id: int):

    try:
        async with aiohttp.ClientSession() as aiohttp_session:
            url = f"http://{app_config.API_Video_To_Images_URL}/scan_videos"
            data = aiohttp.FormData()

            data.add_field('videos',
                    await videos[0].read(),
                    filename=videos[0].filename,
                    content_type='multipart/form-data')
            data.add_field('user_id', str(user_id), content_type='multipart/form-data')
            async with aiohttp_session.post(url, data=data) as response_http:
                response = await response_http.text()
    except aiohttp.client_exceptions.ClientConnectorError:
        print("ERROR: video api is unavailable. Location: calling videos api from background tasks.")
        return
    return response


@timeloop_app.job(interval=timedelta(seconds=20))
def send_ocr_api_batch_scanning_request():
# def send_ocr_api_batch_scanning_request(video_id: int, user_id: int):
    # with aiohttp.ClientSession() as session:
    #     url = f"http://{app_config.API_OCR_URL}/start_batch_scanning"
    #     data = aiohttp.FormData()
    #     data.add_field('user_id', str(user_id), content_type='multipart/form-data')
    #     data.add_field('video_id', str(video_id), content_type='multipart/form-data')

    #     with session.post(url, data=data) as response_http:
            # response = response_http.json()
    # r = requests.post(url, data=json.dumps({"user_id": user_id, "video_id": video_id}))
    # print("hello")
    try:
        url = f"http://{app_config.API_OCR_URL}/start_batch_scanning"
        r = requests.post(url)
        # print(r.text)

        if r.json()['status']:
            url = f"http://localhost/stop_scanning"
            # r = requests.get(url)
    except:
        pass

    return