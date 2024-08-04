import socket


def get_device_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        pass

    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        if ip != "127.0.0.1":  # Check if it's not localhost
            return ip
    except Exception:
        pass

    return None


if __name__ == '__main__':
    print(get_device_ip())
