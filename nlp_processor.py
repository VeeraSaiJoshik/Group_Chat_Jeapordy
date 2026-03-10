from sentence_transformers import SentenceTransformer
from text_processor import Convo, clean_messages, format_messages
import asyncio
from tqdm import tqdm
import anthropic

DESCRIPTION_GENERATOR_SKILL = """
You are an agent who is the first step in the creation of the GroupChatJeapordyGame. This game is a jeapordy knock variation where each point block in each category has an anonymous text from the group chat that relates to that category. The object of the game is for the players to guess which of the group members said each of the things.
GroupChatJeapordy works by smart-parsing through thousands of messages in a group chat with transformers with static filters (length, word variation, etc) and then uses an all-MiniLM-L6-v2 transformer to generate sentence embeddings
You are the agent at the first step of the pipeline that further classifies these filtered messages into 1 of 5 categories for jeapordy. Here is what the pipeline looks like : 

### Prompt Dictionary/Definitions
- word corpus: a vector embedding field of all the unique words that are present within the messages in the group chat
- sentence corpus: a vector embedding field of all the unique sentences that are present within the messages in the group chat
- category bins: an initial array created for each category where all potential messages initially identified are stores. These bins are refined until only 5 messages remain
- LLM Agent: this is referring to you
- strict descriptions: more concrete descriptions of what type of messages should be quried for in the sentence corpus based on the loose definition that was given by the user

### Pipeline Input : Jeapordy Category
- name: the name of the category
    - example : "Roasts", "Quips", "Quircky Statements", "Out of pocket", "Dark Humour", "Sports"
- description: a brief description from the user regarding what type of quotes they want in this category
    - example : "Give me out of pocket roasts that came out of nowhere and absolutely destroyed the other person. These have to be short buy quipy and quircky"
- words: a brief list of words that helps the algorithm shortlist potential quotes
    - example : ["stupid", "idiot", "bafoon", "monkey", "ugly"]

### Step 1 : Keyword Finetuning
- K-Mean Clustering and vector searches to find synonyms within the word corpus
- Identify all messages with user-provided words or synonyms through regex
- Add each identified message into category bins

### Step 2 : Initial Message Classification and Seeding [You are here]
- Use LLM Agent to generate 3-4 strict descriptions for each of the categories based on the user generated data
- Parse through all the sentences and identify a average Cosine_Sim score between the strict descriptions of each category and each message in the corpus
- Identify the top 20 messages with the highest Cosine_Sim score for each category and add them to the category bins.

### Step 3 : Category Pre-Processing & Clustering
- Use another LLM agent (this is NOT YOU) to generate style-matched quotes for each category based on the inital seeds
- Use these quotes as a content reference to use one-shot classification through centroid generation to finish the category bins

### Step 4 : Discrete Weight-Based Sorting
### Step 5 : LLM Final Selection

Now that you know how your input plays into the grand scheme of the shortlisting pipeline, your task is to generate 3-4 strict descriptions for each category based on the user generated data. These descriptions should be more concrete and detailed than the original user prompt and should give a clear picture of what type of messages should be shortlisted for that category.

Your input will have the following list : 
{
    categories: list[Jeapordy Category]
}

Your output should be in the following format :
{
    "category_name": list["string"] <= string of strict descriptions
}

Return nothing else — no preamble, no markdown, no backticks.
"""

class Keyword: 
    def __init__(self, word: str, restrictive: bool):
        self.word = word
        self.restrictive = restrictive
class JeapordyCategory:
    def __init__(self, name: str, description: str, key_words: list[Keyword]):
        self.name = name
        self.description = description
        self.key_words = key_words
    async def get_detailed_description(transformer: SentenceTransformer):
        detailed_description = "" # get claude description
        detailed_description = transformer.encode(detailed_description, device="mps")

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