import json

import openai
from loguru import logger

from ai_proxy.settings import settings


class Prompt:

    def __init__(self):
        self.client = openai.OpenAI(
            organization=settings.openai_org,
            project=settings.openai_project,
            api_key=settings.openai_key,
        )

    @staticmethod
    def get_static_prompt():
        for attr in (
            "prompt_message_1",
            "prompt_message_2",
            "prompt_message_3",
            "prompt_message_4",
            "prompt_message_5",
        ):
            message = getattr(settings, attr, None)
            role = getattr(settings, f"{attr}_type", "user")
            if message:
                yield {
                    "role": role,
                    "content": message
                }

    def query(self, message: str, role: str = "user"):
        prompt_messages = [message for message in self.get_static_prompt()]
        chat_completion = self.client.chat.completions.create(
            messages=[
                *prompt_messages,
                {
                    "role": role,
                    "content": message,
                }
            ],
            model="gpt-3.5-turbo",
        )

        logger.info(chat_completion)
        result = chat_completion.choices.pop()
        result_dict = json.loads(result.message.content)

        return result_dict
