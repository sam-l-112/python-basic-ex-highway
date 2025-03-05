import requests
print(requests.__version__)

import multiprocessing

def worker():
    print("子進程運行中")

if __name__ == "__main__":
    process = multiprocessing.Process(target=worker)
    process.start()
    process.join()

