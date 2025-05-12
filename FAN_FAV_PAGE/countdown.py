import streamlit as st
import asyncio
import datetime

async def countdown_async(duration, placeholder):
    end_time = datetime.datetime.now() + datetime.timedelta(seconds=duration)
    while datetime.datetime.now() < end_time:
        remaining = end_time - datetime.datetime.now()
        minutes = remaining.seconds // 60
        seconds = remaining.seconds % 60
        placeholder.metric("Countdown", f"{minutes:02d}:{seconds:02d}")
        await asyncio.sleep(1)
    st.balloons()
    st.success("Asynchronous Countdown Finished!")

def run_asyncio_task(duration, placeholder):
    asyncio.run(countdown_async(duration, placeholder))

st.title("Asynchronous Countdown")

# Input in minutes instead of seconds
duration_minutes = st.number_input("Enter countdown time in minutes:", min_value=1, value=1)
start_button = st.button("Start Asynchronous Countdown")
placeholder = st.empty()

if start_button:
    # Convert minutes to seconds
    duration_seconds = duration_minutes * 60
    run_asyncio_task(duration_seconds, placeholder)
    st.info("Countdown started!")