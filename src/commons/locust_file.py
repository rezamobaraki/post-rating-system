import random

import faker
from locust import between, HttpUser, task


class DjangoRestUser(HttpUser):
    wait_time = between(1, 5)  # Simulate waiting between 1 to 5 seconds between requests

    @task
    def get_posts(self):
        self.client.get("/api/v1/posts/")

    @task
    def create_rate(self):
        post_id = random.randint(1, 5)
        score = random.randint(0, 5)
        response = self.client.post(f"/api/v1/posts/{post_id}/rates/", json={"score": score})
        if response.status_code != 201:
            print(f"Failed to create rate: {response.status_code}, {response.text}")

    def on_start(self):
        # Generating random username and password
        fake = faker.Faker()
        username = fake.user_name()
        password = fake.password()

        # Register a new user
        response = self.client.post("/api/v1/accounts/auth/register/", json={
            "username": username,
            "password": password
        })
        token = response.json().get("access_token")
        self.client.headers.update({"Authorization": f"Bearer {token}"})
