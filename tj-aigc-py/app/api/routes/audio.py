from fastapi import APIRouter, UploadFile
from fastapi.responses import StreamingResponse

router = APIRouter()


@router.post("/tts-stream")
async def tts_stream(text: str):
    from app.services.audio_service import AudioService

    svc = AudioService()

    async def audio_generator():
        async for chunk in svc.tts_stream(text):
            yield chunk

    return StreamingResponse(audio_generator(), media_type="audio/mpeg")


@router.post("/stt")
async def stt(file: UploadFile) -> str:
    from app.services.audio_service import AudioService

    svc = AudioService()
    audio_data = await file.read()
    return await svc.stt(audio_data)
