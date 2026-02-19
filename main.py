from fastapi import FastAPI

app = FastAPI()

@app.get("/names/{name}")
def read_name(name):
  return name