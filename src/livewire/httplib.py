from typing import NamedTuple, Callable, Union, Dict


class HttpRequest(NamedTuple):
    method: str
    path: str
    params: Dict[str, str]
    content: Union[str, bytes]
    content_type: str


class HttpResponse(NamedTuple):
    code: int
    content: Union[str, bytes]
    content_type: str

    @staticmethod
    def application_zip(content: bytes) -> 'HttpResponse':
        content_type = 'application/zip, application/octet-stream, application/x-zip-compressed, multipart/x-zip'
        return HttpResponse(200, content, content_type)

    @staticmethod
    def text_html(content: str) -> 'HttpResponse':
        return HttpResponse(200, content, 'text/html')

    @staticmethod
    def text_plain(content: str, code=200) -> 'HttpResponse':
        return HttpResponse(code, content, 'text/plain')


class HttpRoute(NamedTuple):
    path: str
    callback: Callable[[HttpRequest], HttpResponse]
