from app import make_app
from aiohttp.test_utils import AioHTTPTestCase


class MyTestCase(AioHTTPTestCase):
    headers = {"content-type": '"application/json"'}

    async def get_application(self):
        return make_app()

    async def test_hello_world(self):
        async with self.client.request("GET", "/") as resp:
            self.assertEqual(resp.status, 200)
            text = await resp.text()
        self.assertIn("Hello World!", text)

    async def test_post(self):
        data = {
  "type": "conversationUpdate",
  "membersAdded": [
    {
      "id": "aec0ab60-bb21-11ec-b54f-a33171a5137d",
      "name": "Bot"
    },
    {
      "id": "66dca36a-ce7d-4fea-83d5-c63b12d138e8",
      "name": "User"
    }
  ],
  "membersRemoved": [],
  "channelId": "emulator",
  "conversation": {
    "id": "582b8b00-bb4c-11ec-b54f-a33171a5137d|livechat"
  },
  "id": "583ca200-bb4c-11ec-b7bc-4f566319158b",
  "localTimestamp": "2022-04-13T12:08:31-05:00",
  "recipient": {
    "id": "aec0ab60-bb21-11ec-b54f-a33171a5137d",
    "name": "Bot",
    "role": "bot"
  },
  "timestamp": "2022-04-13T17:08:31.392Z",
  "from": {
    "id": "66dca36a-ce7d-4fea-83d5-c63b12d138e8",
    "name": "User",
    "role": "user"
  },
  "locale": "en-US",
  "serviceUrl": "http://localhost:56890"
}
        
        async with self.client.request(
            "POST", "/api/messages", headers=self.headers, json=data
        ) as resp:
            # self.assertEqual(resp.status, 200)
            print(resp.status)
            print(await resp.text())
            print(await resp.json(content_type="application/octet-stream"))
