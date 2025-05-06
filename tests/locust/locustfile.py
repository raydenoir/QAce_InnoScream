from locust import HttpUser, task, constant_throughput
from ...src.innoscream.core.config import get_settings

class ScreamBotUser(HttpUser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot_token = get_settings().bot_token
        self.channel_id = get_settings().channel_id


    @task
    def get_updates(self):
        """Simulate checking for new messages"""
        endpoint = f"/bot{self.bot_token}/getUpdates"
        self.client.get(endpoint)