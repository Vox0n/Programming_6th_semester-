from quart import Quart, jsonify
import asyncio
import time

app = Quart(__name__)

def cpu_intensive_task():
    total = 0
    for i in range(15_000_000):
        total += i
    return total

@app.route('/cpu')
async def cpu():
    start = time.time()
    # BLOCKING - bad for async
    result = cpu_intensive_task()
    elapsed = time.time() - start
    return jsonify({
        "result": result,
        "execution_time": elapsed,
        "mode": "blocking"
    })

@app.route('/cpu_fixed')
async def cpu_fixed():
    start = time.time()
    # NON-BLOCKING - good
    result = await asyncio.to_thread(cpu_intensive_task)
    elapsed = time.time() - start
    return jsonify({
        "result": result,
        "execution_time": elapsed,
        "mode": "non-blocking"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, workers=1)