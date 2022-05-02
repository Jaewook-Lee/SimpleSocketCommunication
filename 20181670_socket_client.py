import os
import platform
import socket
import webbrowser

# sockeet 통신을 위한 기본적인 setting 진행
BUFF_SIZE = 65535
ADDRESS = "192.168.1.4"    # 서버의 IP 주소를 확인하고 그에 맞게 변경해야 함
PORT = 8000
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
client_socket.connect((ADDRESS, PORT))
CLIENT_OS = platform.platform().split("-")[0]    # 클라이언트의 OS 정보

method = input("Enter method >> ")    # 클라이언트가 메서드를 직접 입력
if method == "GET" or method == "HEAD":
    """
    원하는 파일 이름을 입력(확장자명까지)
    입력을 하지 않는 경우 "Witcher.txt" 가 default 로 설정
    """
    file_name = input("What file do you want to get?(Empty OK) >> ")
    if file_name == "":
        file_name = "Witcher.txt"
    cmd = f"{method} /{file_name} HTTP/1.1\r\nUser-Agent: {CLIENT_OS}\r\n"
    client_socket.send(cmd.encode())
    response = client_socket.recv(BUFF_SIZE).decode()
    print(response)

    """
    여기서부터는 html 파일을 GET 요청한 경우 브라우저로 보여주기 위한 과정
    HEAD 요청인 경우 실행되지 않음
    """
    response_info = response.split("\r\n")
    response_code = int(response_info[0].split()[1])
    if response_code != 404 and method == "GET":
        new_file_content = response_info[-1]
        with open(file_name, "w", encoding='utf-8') as f:
            f.write(new_file_content)    # 서버에 있는 파일을 클라이언트로 복사

        if file_name.endswith("html"):    # html 파일인 경우 브라우저로 보여줌
            webbrowser.open("file://" + os.path.realpath(file_name))
elif method == "PUT" or method == "POST":
    # 서버에 저장시킬 파일은 20181670_socket_client.py 파일이 있는 디렉터리에 위치해야 함(하위 폴더 X)

    file_name = input("What file do you want to put? >> ")    # 서버로 저장하고 싶은 파일 이름을 입력(확장자명까지)
    if not file_name:    # 파일 이름은 무조건 입력받아야 하므로 입력을 하지 않는 경우 클라이언트 종료
        print("You should put something!")
        exit(0)
    else:
        """
        저장시킬 파일의 위치에 대한 경로를 나타내는 과정
        Windows 의 경우 경로 표시에 \\ 문자를 이용하고 Linux 나 macOS 의 경우 / 문자를 사용
        따라서 클라이언트의 운영체제에 따라 파일 경로를 다르게 설정
        """
        if CLIENT_OS == "Linux" or CLIENT_OS == "macOS":
            file_path = os.path.dirname(os.path.realpath(__file__)) + "/" + file_name
        elif CLIENT_OS == "Windows":
            file_path = os.path.dirname(os.path.realpath(__file__)) + "\\" + file_name
        else:
            print("We support Windows, Linux and Mac OS... Sorry...")
            exit(0)

        """
        클라이언트가 서버에 저장시킬 파일이 20181670_socket_client.py 파일이 있는 디렉터리에 있는지 확인하는 과정
        없는 경우 클라이언트 종료
        """
        if os.path.exists(file_path):
            cmd = f"{method} /{file_name} HTTP/1.1\r\nUser-Agent: {CLIENT_OS}\r\n"
            with open(file_path, 'r', encoding='utf-8') as f:
                body = f.read()

            if file_name.endswith(".html"):
                cmd += ("Content-Type: text/html; charset=utf-8\r\n" + body)
            else:
                cmd += ("Content-Type: text/plain; charset=utf-8\r\n" + body)
        else:
            print("File is not exists.")
            exit(0)
    client_socket.send(cmd.encode())
    response = client_socket.recv(BUFF_SIZE).decode()
    print(response)
elif method == "DELETE":
    file_name = input("What file do you want to delete? >> ")    # 서버에서 지우고 싶은 파일 이름 입력
    if file_name:
        cmd = f"{method} /{file_name} HTTP/1.1\r\nUser-Agent: {CLIENT_OS}\r\n"
    else:    # 파일 이름은 무조건 입력받아야 하므로 입력을 하지 않는 경우 클라이언트 종료
        print("You should delete something!")
        exit(0)
    client_socket.send(cmd.encode())
    response = client_socket.recv(BUFF_SIZE).decode()
    print(response)
else:
    # method 가 GET, HEAD, POST, PUT, DELETE 가 아닌 경우
    cmd = f"{method} / HTTP/1.1\r\nUser-Agent: {CLIENT_OS}\r\n"
    client_socket.send(cmd.encode())
    response = client_socket.recv(BUFF_SIZE).decode()
    print(response)
client_socket.close()
