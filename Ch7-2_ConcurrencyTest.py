import time
import functools

import asyncio
from aiofile import AIOFile, Reader, Writer

import json
import pandas as pd
from collections import defaultdict
from pathlib import Path
from tqdm import tqdm

DEFAULT_FMT = "[{elapsed:0.8f}s] {name}({args}, {kwargs}) -> {result}"
path = Path("/home/shyeon/workspace/python/SparkDefinitiveGuide/data/activity-data/")


def clock(fmt=DEFAULT_FMT):
    def decorate(func):
        @functools.wraps(func)
        def clocked(*_args, **_kwargs):  # clocked에서 *, ** 키워드를 통해 설정된 인수를 변수화
            t0 = time.time()
            _result = func(*_args)
            elapsed = time.time() - t0
            name = func.__name__
            args = ", ".join(repr(arg) for arg in _args)
            pairs = ["%s=%r" % (k, w) for k, w in sorted(_kwargs.items())]
            kwargs = ", ".join(pairs)
            result = repr(_result)
            print(fmt.format(**locals()))
            return _result  # clocked()는 데커레이트된 함수를 대체하므로, 원래 함수가 반환하는 값을 반환해야 한다.

        return clocked  # decorate()는 clocked()를 반환한다.

    return decorate  # clock()은 decorate()를 반환한다.


async def load_json(path):
    async with AIOFile(path, "r", encoding="UTF-8") as afp:
        print(await afp.read())


def convert_json2dict(json_str: str, dic: dict):
    for key, value in json.loads(json_str).items():
        dic[key].append(value)


@clock()
def main():
    dd = defaultdict(list)
    files = path.glob("*.json")

    tasks = [load_json(file) for file in files]

    return tasks


#     result = pd.DataFrame(dd)
#     print(result.head())


if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(*main()))
#     loop.close()
