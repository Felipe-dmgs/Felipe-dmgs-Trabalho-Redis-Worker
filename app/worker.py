import redis
import json
import time

r = redis.Redis(host='redis', port=6379, decode_responses=True)

print("Worker iniciado, aguardando pedidos...")

while True:
    _, message = r.brpop("order_queue", timeout=0)
    
    order = json.loads(message)
    print(f"[*] Processando pedido: {order}")
    
    time.sleep(5)
    print(f"[V] Pedido concluído!")