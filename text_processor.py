# [8/12/25, 4:46:49 PM] Lalittle: I got 212 index too
from datetime import datetime
import asyncio
from tqdm import tqdm
import math
import re

MINUTE = 60

class Message: 
    def __init__(self, message: str):
        raw_date_time = message.split("]")[0].replace("[", "").replace("\u200e", "").replace("\u202f", " ").strip()
        raw_date = raw_date_time.split(", ")[0]
        raw_time = raw_date_time.split(", ")[1] 

        self.date_time = datetime.strptime(f"{raw_date}, {raw_time}", "%m/%d/%y, %I:%M:%S %p") 
        self.text = message.split(": ")[1] if len(message.split(": ")) > 1 else ""
        self.author = message.split(": ")[0].split("] ")[1].strip()

class Convo:
    def is_worthy_message(message_obj: Message, _):
        message = message_obj.text.lower()

        words = message.split(" ")
        if len(words) < 3 and len(message) < 100 : return False # Enough Words
        if len(list(set([word.lower() for word in words]))) < 4 : return False # Enough Unique Words
        letters = list(filter(lambda x: x.isalpha(), [char for char in message]))

        if len(list(set(letters))) < 4 or len(letters) < 4: return False # Enough Unique Letters

        # Check if it is a URL
        stripped = re.sub(r'https?://\S+', '', message).strip()                                                                                                                          
        if len(stripped) < 10: return False   

        # Native Media
        key_phrases = ["<Media omitted>", "This message was deleted", "missed call", "audio omitted", "image omitted", "sticker omitted", "POLL"]
        if True in [phrase in message for phrase in key_phrases]: return False

        return True

    def __init__(self, og_messages: list[Message]):
        self.length = len(og_messages)
        self.messages = []
        for message in og_messages :
            if Convo.is_worthy_message(message, self.messages) : 
                self.messages.append(message)


def full_message(line: str):
    return line[0] == "[" and "]" in line and ("AM" in line or "PM" in line)

def remove_short_outliers(conversations: list[list[Message]]) -> list[list[Message]]:                                                                                            
    lengths = [len(c) for c in conversations]                                                                                                                                    
    q1 = sorted(lengths)[len(lengths) // 4]                                                                                                                                      
    lower_bound = q1 - 1.5 * (sorted(lengths)[3 * len(lengths) // 4] - q1)                                                                                                       
    return [c for c in conversations if len(c) >= lower_bound] 

def format_messages(input_msgs: list[str]) -> list[Message] : 
    # Clean each line of messages
    remove_phrases = ["<This message was edited>", "This message was deleted"]
    raw_messages = []
    for msg in input_msgs:
        for phrase in remove_phrases : 
            msg = msg.replace(phrase, "")
        raw_messages.append(msg)
    
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

    # dedupping message
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

    return dedup_messages

def remove_short_outliers(conversations: list[list[Message]]) -> list[list[Message]]:                                                                                            
      lengths = [len(c) for c in conversations]                                                                                                                                    
      q1 = sorted(lengths)[len(lengths) // 4]                                                                                                                                      
      lower_bound = q1 - 1.5 * (sorted(lengths)[3 * len(lengths) // 4] - q1)                                                                                                       
      return [c for c in conversations if len(c) >= lower_bound]

def clean_messages(messages: list[Message]):
    # removing messages from stale conversations
    is_ingroup = lambda prevs, message : math.fabs((prevs[-1].date_time - message.date_time).total_seconds()) < 60 * MINUTE

    conversations = []
    conversation = []
    for message in tqdm(messages):
        if len(conversation) == 0 : 
            conversation = [message]
            continue

        if is_ingroup(conversation, message) : 
            conversation.append(message)
        else : 
            conversations.append(conversation)
            conversation = [message]
    conversations.append(conversation)
    conversations = remove_short_outliers(conversations)

    formatteed_convos = [Convo(convo) for convo in tqdm(conversations) ]
    print("👫🏾 Conversation Count: ", len(formatteed_convos))
    print("👫🏾 Messages Count: ", sum([len(convo.messages) for convo in formatteed_convos]))
    
    return formatteed_convos

async def get_suggestions(raw_messages):
    messages = format_messages(raw_messages)
    clean_messages(messages)

if __name__ == "__main__":
    with open("./texts.txt", "r") as f:
        lines = f.readlines()

    asyncio.run(get_suggestions(lines))