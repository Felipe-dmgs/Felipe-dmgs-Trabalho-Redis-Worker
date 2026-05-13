import time
import json
from fastapi import FastAPI, Request, Response
import redis

app = FastAPI()
r = redis.Redis(host='redis', port=6379, decode_responses=True)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    limit_key = f"limit:{client_ip}"
    
    current_requests = r.incr(limit_key)
    
    if current_requests == 1:
        r.expire(limit_key, 60)

    if current_requests > 5:
        return Response(content="Too Many Requests (Limite Excedido)", status_code=429)
    
    return await call_next(request)


@app.get("/data/{item_id}")
def get_data(item_id: str, response: Response):
    cache_key = f"item:{item_id}"
    cached_value = r.get(cache_key)

    if cached_value:
        response.headers["X-Cache"] = "HIT"
        return {"data": cached_value, "source": "cache"}

    time.sleep(2)
    val = f"Conteúdo pesado gerado para o item {item_id}"
    
    r.setex(cache_key, 30, val)
    
    response.headers["X-Cache"] = "MISS"
    return {"data": val, "source": "database_simulated"}


@app.post("/order")
def create_order(order_data: dict):
    r.lpush("order_queue", json.dumps(order_data))
    return {"status": "Pedido enviado para processamento na fila"}