# https://webdir.tistory.com/206 우분투 방화벽 설정
import socket
import os
import platform
from datetime import datetime as dtime

"""
socket 통신을 위한 기본적인 setting 을 진행
"""
BUFF_SIZE = 65535
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)        # SO_REUSEADDR 통해 포트를 즉시 재사용 할 수 있게 설정
PORT = 8000
SERVER_IP = socket.gethostbyname(socket.gethostname())
server_socket.bind((SERVER_IP, PORT))
server_socket.listen(0)

"""
20181670_socket_server.py 를 실행하면서 전체적으로 쓰일 변수들 선언
- SERVER_OS: 서버의 OS에 따라 파일 경로 설정이 달라지기 때문에 서버의 OS를 변수로 설정
- CONTENT_HEADER: 모든 메서드에 공통적으로 삽입할 헤더
- OK_MSG: 성공적으로 수행했음을 알리는 response
- FILE_NOT_FOUND_RESPONSE: 파일을 못 찾았음을 알리는 response
- OS_NOT_SUPPORT_RESPONSE: Linux, macOS, Windows 아니면 파일 경로가 어떻게 돼있는지 몰라서 세 OS 아니면 실행 거부하는 response
"""
SERVER_OS = platform.platform().split("-")[0]
CONTENT_HEADER = "Content-Type: text/plain; charset=utf-8\r\n"
OK_MSG = "HTTP/1.1 200 OK\r\n"
FILE_NOT_FOUND_RESPONSE = "HTTP/1.1 404 Not Found\r\n" + CONTENT_HEADER + "\nFile not found"
OS_NOT_SUPPORT_RESPONSE = "HTTP/1.1 500 Internal Server Error\r\n" + CONTENT_HEADER + "\nOS Not Supported"

dir_path = os.path.dirname(os.path.realpath(__file__))    # 현재 http_sever.py 가 있는 디렉터리의 경로


def do_GET(file_name):
    """
    클라이언트가 다운로드 받을 파일의 내용을 보내주는 함수\n
    클라이언트가 원하는 파일이 있으면 200 response 전송\n
    파일을 찾지 못했으면 404 response 를 전송\n
    :param file_name: 클라이언트가 다운로드 하고 싶어하는 파일의 이름
    :return: HTTP Response 구조를 따른 message
    """
    try:
        text_file = open(dir_path + file_name, encoding="utf-8")
        body = text_file.read()
    except FileNotFoundError:
        return FILE_NOT_FOUND_RESPONSE
    text_file.close()

    msg = OK_MSG + CONTENT_HEADER + "\n" + body
    return msg


def do_HEAD(file_name):
    """
    클라이언트가 원하는 파일의 헤더 정보를 보내주는 함수\n
    클라이언트가 원하는 파일이 있으면 204 response 전송(실질적인 body 내용이 없기 때문에 204로 결정)\n
    파일을 찾지 못했으면 404 response 를 전송\n
    :param file_name: 클라이언트가 원하는 파일의 이름
    :return: HTTP Response 구조를 따른 message
    """
    try:
        text_file = open(dir_path + file_name, encoding="utf-8")
        whole_text = text_file.read()
    except FileNotFoundError:
        return FILE_NOT_FOUND_RESPONSE
    text_file.close()
    text_len = len(whole_text)
    content_length_header = "Content-Length: %d" % text_len + "\r\n\n"    # HEAD 에서만 Content_Length 헤더 추가

    msg = "HTTP/1.1 204 No Content\r\n" + CONTENT_HEADER + "\n" + content_length_header
    return msg


def do_POST(file_name, text):
    """
    클라이언트의 파일을 서버에 저장하는 함수\n
    동일 이름의 파일이 존재하면 403 response 전송(파일 저장을 할 권한이 없다고 판단)\n
    존재하지 않으면 파일 저장 후, 201 response 를 전송\n
    :param file_name: 클라이언트가 서버에 저장할 파일의 이름
    :param text: 클라이언트가 서버에 저장할 파일의 내용
    :return: HTTP Response 구조를 따른 message
    """
    if not os.path.exists(dir_path + file_name):
        with open(dir_path + file_name, "w") as f:
            f.write(text)
        return f"HTTP/1.1 201 Created\r\nContent-Location: {file_name}\r\n"
    else:
        # 서버에서의 파일 위치 알림
        return "HTTP/1.1 403 Forbidden\r\n" + CONTENT_HEADER + f"\nFile already exist in {file_name}"


def do_PUT(file_name, text):
    """
    클라이언트가 원하는 서버 내의 파일을 삭제하는 함수\n
    동일 이름의 파일이 존재하면 그 파일에 내용을 덮어쓰고 200 response 를 전송\n
    :param file_name: 클라이언트가 서버에 저장할 파일의 이름
    :param text: 클라이언트가 서버에 저장할 파일의 내용
    :return: HTTP Response 구조를 따른 message
    """
    with open(dir_path + file_name, "w") as f:
        f.write(text)
    return OK_MSG + f"Content-Location: {file_name}\r\n\n"


def do_DELETE(file_name):
    """
    클라이언트의 파일을 서버에 저장하는 함수\n
    파일이 존재하면 그 파일을 삭제하고 200 response 를 전송\n
    파일을 찾지 못했으면 404 response 를 전송\n
    :param file_name: 클라이언트가 서버에 저장하할 파일의 이름
    :return: HTTP Response 구조를 따른 message
    """
    if os.path.exists(dir_path + file_name):
        os.remove(dir_path + file_name)
        msg = OK_MSG + CONTENT_HEADER + f"\nFile is deleted."
    else:
        return FILE_NOT_FOUND_RESPONSE
    return msg


def handle_exception(client_method):
    """
    GET, HEAD, DELETE, PUT, POST 외의 method(대소문자 구별) 가 요청될 경우 400 response 전송하는 함수\n
    :param client_method: 클라이언트가 입력한 method
    :return: HTTP Response 구조를 따른 message
    """
    return "HTTP/1.1 400 Bad Request\r\n{}\nWe didn't provide {}".format(CONTENT_HEADER, client_method)


def run_server():
    """
    서버가 동작하는 함수
    """
    while True:
        connect, addr = server_socket.accept()
        with connect:
            message = connect.recv(BUFF_SIZE).decode()
            now = dtime.now()
            print(now, message)    # 클라이언트의 요청 시간과 message 출력

            msg_status = message.split("\r\n")    # 클라이언트의 message 분석을 위한 list
            request_line, body = msg_status[0], None    # request_line: 헤더와 body 를 뗀 첫 줄({method} /{file_name} HTTP/1.1)

            """
            클라이언트의 messsage 에서 body 부분을 떼어내기 위한 if문
            body 내용이 없는 GET 이나 HEAD, DELETE 같은 경우 "User-Agent: {클라이언트 OS}" 가 저장
            하지만 GET, HEAD, DELETE 에서 body 를 가지고 작업을 하지 않음
            PUT, POST 요청 경우, body 내용을 정확히 얻을 수 있음("User-Agent: {클라이언트 OS}" 헤더가 무조건 있기 때문)
            """
            if len(msg_status) > 1:
                body = msg_status[len(msg_status) - 1]

            request_info = request_line.split()    # 클라이언트의 method 와 HTTP version 정보를 얻기 위한 list

            """
            아직 원인을 모르지만 브라우저를 통해 서버에 GET 요청하는 경우, /favicon.ico 등의 여러 전송이 발생해 형식에 맞지 않는 요청 발생
            그 전송들을 무시하기 위한 try 절
            이를 통해 자신이 원했던 클라이언트의 요청만 얻음
            """
            try:
                method, version = request_info[0], request_info[2]
            except IndexError:
                continue

            version = float(version.split("/")[1])
            target = request_info[1][1:]    # 클라이언트가 요청하는 파일
            if target == "":    # 브라우저로 GET 요청할 때 default file 을 설정하기 위한 작업
                target = "Witcher.txt"

            """
            Windows 의 경우 경로 표시에 \\ 문자를 이용하고 Linux 나 macOS 의 경우 / 문자를 사용
            따라서 서버의 운영체제에 따라 파일 경로를 다르게 설정
            """
            if SERVER_OS == "Windows":
                target = "\\" + target
            elif SERVER_OS == "macOS" or SERVER_OS == "Linux":
                target = "/" + target

            send_msg = ""
            if version != 1.1:
                send_msg += "HTTP/1.1 505 HTTP Version Not Support\r\n"
            elif method == "GET":
                send_msg += do_GET(target)
            elif method == "HEAD":
                send_msg += do_HEAD(target)
            elif method == "POST":
                send_msg += do_POST(target, body)
            elif method == "PUT":
                send_msg += do_PUT(target, body)
            elif method == "DELETE":
                send_msg += do_DELETE(target)
            else:
                send_msg += handle_exception(method)

            connect.send(send_msg.encode())


if __name__ == "__main__":
    run_server()
