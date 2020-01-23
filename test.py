import requests


def test_runcmd():
    url = "http://192.168.1.186:5000/runcmd"
    data = {"command":"fs_cli","command2":"db_cache status"}
    r = requests.post(url, data=data)
    print(r.content)

def test_getxml():
    url = "http://192.168.1.186:5000/getxml"
    data = {"command":"fs_cli","command2":"db_cache status"}
    r = requests.get(url)
    print(r.content)

if __name__ == "__main__":
    # test_runcmd()
    test_getxml()