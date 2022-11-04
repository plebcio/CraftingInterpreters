import time

def fib(n):
    if n < 2:
        return n
    return fib(n-1) + fib(n-2)

s = time.time()
print(fib(40))
print(time.time() - s)