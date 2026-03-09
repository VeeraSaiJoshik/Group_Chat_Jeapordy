from sentence_transformers import SentenceTransformer
from text_processor import Convo, clean_messages, format_messages
import asyncio
from tqdm import tqdm

async def gather_category_options(convos: list[Convo]):
    transformer_model = SentenceTransformer('all-MiniLM-L6-v2', device="mps")
    all_messages = [message  for convo in convos for message in convo.messages]

    texts = [msg.text for msg in all_messages]                                                                                                                                                                                                                                                                                                                      
    embeddings = transformer_model.encode(texts, batch_size=64, show_progress_bar=True) 

    for msg, embedding in tqdm(zip(all_messages, embeddings)):
        msg.encoding = embedding
    return []

if __name__ == "__main__":
    with open("./texts.txt", "r") as f:
        lines = f.readlines()

    messages = format_messages(lines)
    formatted_convos = clean_messages(messages)

    asyncio.run(gather_category_options(formatted_convos))