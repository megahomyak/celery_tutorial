from worker import app


@app.task
def add(x, y):
    return x + y


@app.task
def sum_task(numbers):
    return sum(numbers)
