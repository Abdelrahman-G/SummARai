# pip install -r requirements.txt

import io
from pipes import quote
from typing import IO, Iterator

from fastapi import FastAPI, UploadFile, Request, File, Body
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse

from OCRService import OCRService
from SummarizationPipeline import SummarizationService
from Events import SSEEvent, EventModel
import asyncio
from sse_starlette import EventSourceResponse
app = FastAPI()
summarizationService = SummarizationService()

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/getSummary")
async def getSummary(file: UploadFile = File(...)):
    summary = await summarizationService.run(file)


    return StreamingResponse(
        io.BytesIO(summary),
        media_type="application/pdf",
        headers={
            # This header will make Spring’s WebClient (or a browser) see it as a downloadable file
            "Content-Disposition": 'attachment; filename="book.pdf"'
        }
    )


@app.get("/stream")
async def stream_events(req: Request):
    async def stream_generator():
        while True:
            event = SSEEvent.get_event()
            if event:
                temp = event.model_dump()
                if temp['message'] == 'end':
                    break
                else:
                    yield "data: {}\n\n".format(event.model_dump_json())

            await asyncio.sleep(0.01)

    return EventSourceResponse(stream_generator())

