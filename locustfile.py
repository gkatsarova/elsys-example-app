from locust import HttpUser, task, between

class FileStorageUser(HttpUser):
    wait_time = between(1, 3)  

    @task
    def ping_root(self):
        self.client.get("/")

    @task
    def list_files(self):
        self.client.get("/files")

    @task
    def health_check(self):
        self.client.get("/health")
