import asyncio
import aiohttp

JOKE_API = 'https://official-joke-api.appspot.com/random_joke'
QUOTE_API = 'https://zenquotes.io/api/random'
TRIVIA_API = 'https://opentdb.com/api.php?amount=1'


async def get_joke(session):
    async with session.get(JOKE_API) as resp:
        data = await resp.json()
        return f"{data['setup']} ... {data['punchline']}"

    
async def get_quote(session):
    async with session.get(QUOTE_API) as resp:
        data = await resp.json()
        return f"“{data[0]['q']}” — {data[0]['a']}"

    
async def get_trivia(session):
    async with session.get(TRIVIA_API) as resp:
        data = await resp.json()
        result = data['results'][0]
        question = result['question']
        answer = result['correct_answer']
        return f"Q: {question} | A: {answer}"

    
async def main():
    async with aiohttp.ClientSession() as session:
        joke_task = get_joke(session)
        quote_task = get_quote(session)
        trivia_task = get_trivia(session)

        joke, quote, trivia = await asyncio.gather(joke_task, quote_task, trivia_task)

        print('Joke:', joke)
        print('Quote:', quote)
        print('Trivia:', trivia)

        
asyncio.run(main())
