# [8/12/25, 4:46:49 PM] Lalittle: I got 212 index too
from datetime import datetime
import asyncio
from tqdm import tqdm
import math

MINUTE = 60

class Message: 
    def __init__(self, message: str):
        raw_date_time = message.split("]")[0].replace("[", "").replace("\u200e", "").replace("\u202f", " ").strip()
        raw_date = raw_date_time.split(", ")[0]
        raw_time = raw_date_time.split(", ")[1] 

        self.date_time = datetime.strptime(f"{raw_date}, {raw_time}", "%m/%d/%y, %I:%M:%S %p") 
        self.text = message.split(": ")[1] if len(message.split(": ")) > 1 else ""
        self.author = message.split(": ")[0].split("] ")[1].strip()

def full_message(line: str):
    return line[0] == "[" and "]" in line and ("AM" in line or "PM" in line)

def clean_and_compress(raw_messages: list[str]) -> list[Message] : 
    # formatting the messages
    cleaned_up_raw_messages = []
    cache = ""
    for message in raw_messages: 
        if full_message(message):
            if cache != "": cleaned_up_raw_messages.append(cache)
            cache = message
        else : 
            cache += "\n" + message
    cleaned_up_raw_messages.append(cache)
    
    formatted_messages: list[Message] = [Message(line) for line in tqdm(cleaned_up_raw_messages)]
    print("💬 Raw Message Count: ", len(formatted_messages))

    dedup_messages = []
    cache = ""
    for message in tqdm(formatted_messages): 
        if cache == "" : 
            cache = message 
            continue
        
        if cache.author == message.author and math.fabs((message.date_time - cache.date_time).total_seconds()) < MINUTE: 
            cache.text += " " + message.text
        else : 
            dedup_messages.append(cache)
            cache = message
    
    dedup_messages.append(cache)
    print("💬 Raw Message Count: ", len(dedup_messages))

    return formatted_messages

async def get_suggestions(raw_messages):
    messages = clean_and_compress(raw_messages)

if __name__ == "__main__":
    with open("./texts.txt", "r") as f:
        lines = f.readlines()

    asyncio.run(get_suggestions(lines))