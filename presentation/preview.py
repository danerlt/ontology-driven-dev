"""仅在本机提供演示预览，日志使用中文。"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class PreviewHandler(SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f'预览请求：{self.path}；响应信息：' + ' '.join(str(x) for x in args[1:]), flush=True)


if __name__ == '__main__':
    directory = str(Path(__file__).resolve().parent)
    handler = partial(PreviewHandler, directory=directory)
    print('演示预览已启动：http://127.0.0.1:8765', flush=True)
    ThreadingHTTPServer(('127.0.0.1', 8765), handler).serve_forever()
