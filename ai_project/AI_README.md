```from ai_project import Salesman, IncMsgStructure
import asyncio

ai = Salesman()

async def main():
    response = await ai.handle(IncMsgStructure(user_id=1, text="hi", content_type="text"))
    print(response)

asyncio.run(main())
```