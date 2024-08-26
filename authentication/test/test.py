from locust import HttpUser, TaskSet, task, between

class UserBehavior(TaskSet):

    def on_start(self):
        self.login()

    def login(self):
        response = self.client.post("/auth/login", json={"username": "user2", "password": "password"})
        if response.status_code == 200:
            token = response.json().get("token")
            self.headers = {"Authorization": f"Token {token}", "Content-Type": "application/json"}
        else:
            self.headers = {}

    @task
    def index(self):
        self.client.get("/auth/get_internships", headers=self.headers)

class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)
    host = "http://localhost:8000" 