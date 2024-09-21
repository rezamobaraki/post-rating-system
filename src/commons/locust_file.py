import random

import factory
import faker
from locust import between, HttpUser, task


class DjangoRestUser(HttpUser):
    wait_time = between(1, 5)  # Simulate waiting between 1 to 5 seconds between requests

    @task
    def get_posts(self):
        # Replace the endpoint with your actual API endpoint
        self.client.get("/api/v1/posts/")

    @task
    def create_rate(self):
        post_id = random.randint(1, 5)
        score = random.randint(0, 5)
        self.client.post(f"/api/v1/posts/{post_id}/rates/", json={
            "score": score  # Use random score
        })

    def on_start(self):
        username = faker.Faker().user_name()
        password = faker.Faker().password()
        response = self.client.post("/api/v1/accounts/auth/register/", json={
            "username": username,
            "password": password
        })
        token = response.json().get("access_token")
        self.client.headers.update({"Authorization": f"Bearer {token}"})
