from fastapi import FastAPI 

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World from Mr. khan"}

# @app.get("/add")
# async def add(a: int, b: int):
#     result = a + b
#     return{
#         "num1": a,
#         "num2": b,
#         "result": result
#     }