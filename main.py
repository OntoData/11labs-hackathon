from fastapi import FastAPI
import requests
import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from elevenlabs import ElevenLabs
from loguru import logger

app = FastAPI()

ELEVEN_LABS_API_KEY = "sk_ddcf1116a995e8d8fc660fc5cd2316bcf1d24e2282cf7ff4"
HEADERS = {"xi-api-key": ELEVEN_LABS_API_KEY}
MAKE_UPDATE_CONV_WEBHOOK='https://hook.eu2.make.com/7n8x3uqwlpncavwf47zzd03uhithv9p3'
AGENT_ID='w6UPLbT9UrQACYRfMou2'
RESCAPE_INTERVAL_SECONDS = 300

# Initialize scheduler
scheduler = AsyncIOScheduler()


async def rescrape_11labs():
    """
    Function to periodically rescrape 11Labs data
    Runs every day at midnight
    """
    try:
        client = ElevenLabs(
            api_key=ELEVEN_LABS_API_KEY,
        )
        response = client.conversational_ai.get_conversations(agent_id=AGENT_ID)
        logger.info(response)
        conv_ids = [conv.conversation_id for conv in response.conversations]
        for conv_id in conv_ids:
            response = client.conversational_ai.get_conversation(
                conversation_id=conv_id,
            )
            logger.info(response)
            unix_time_to_fetch = int(datetime.now().timestamp()) - RESCAPE_INTERVAL_SECONDS
            if response.metadata.start_time_unix_secs > unix_time_to_fetch:
                conv_content = '\n'.join([f'{tr.role}: {tr.message}' for tr in response.transcript])
                payload = {'id': conv_id, 'conversation': conv_content}
                logger.info(payload)
                if conv_content:
                    response = requests.post(MAKE_UPDATE_CONV_WEBHOOK, json=payload)
    except requests.exceptions.RequestException as e:
        print(f"[{datetime.now()}] Error fetching 11Labs data: {str(e)}")
        return None


@app.on_event("startup")
async def startup_event():
    # Schedule the rescrape_11labs function to run every day at midnight
    # scheduler.add_job(
    #     rescrape_11labs,
    #     CronTrigger(hour="*", minute="*"),  # Run at midnight
    #     id="rescrape_11labs",
    #     name="Rescrape 11Labs data daily",
    #     replace_existing=True,
    # )
    scheduler.start()


@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()

@app.post("/rescrape")
async def rescrape():
    await rescrape_11labs()
    return {"message": "Rescrape request received"}


@app.get("/")
async def hello():
    # Example of using requests library
    response = requests.get("https://api.github.com/zen")
    return {"message": f"Hello from Cloud Run! Here's some wisdom: {response.text}"}


# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8080)
