from locust import HttpUser, task, between

class APIUser(HttpUser):
    wait_time = between(0.1, 0.5)
    
    @task
    def test_cpu(self):
        self.client.get("/cpu")
    
    @task
    def test_cpu_fixed(self):
        self.client.get("/cpu_fixed")