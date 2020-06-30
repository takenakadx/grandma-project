import requests
import json

def get_id_from_token(token):
    headers = {}
    headers["Content-Type"] = "application/json"
    headers["Authorization"] = "Bearer {}".format(token)
    res = requests.post("https://api.line.me/v2/profile",headers=headers)
    if(res.status_code == 200):
        response_json = json.loads(res.text)
        return response_json
    else:
        print(res.status_code)
        print(res.text)
        return None

def send_text_messages_to(id,messages):
    post_body = {}
    post_body["to"] = id
    post_body["messages"] = []
    for elem in messages:
        post_body["messages"].append({"type":"text","text":elem})
    headers = {}
    headers["Content-Type"] = "application/json"
    headers["Authorization"] = "Bearer MgCvmUbYeE0w22nyxniqz/6ubItzEBlB4w/KuM1lCB2AIBB18JuHtebOZA/zjCItUB9YuhzBR7nLvMz7Cxm1J3n+MNqpZ1lDc5DqIr5vR5emGwCswNIZwY8JzQVPAEIMXiVdXzdeGVS80L0taWV1+gdB04t89/1O/w1cDnyilFU="
    res = requests.post("https://api.line.me/v2/bot/message/push",headers=headers,json=post_body)
    print(res.status_code)
    print(res.text)
    return res

if __name__ == "__main__":
    _id = get_id_from_token("eyJhbGciOiJIUzI1NiJ9.KTVLQL8zrVq_p_9HX1Bvo691V-3NPaUC4fSy-_RtwyV6RWiExG2Xc9hxZ_lN5hxR9GcWYQT25ncL2CU3SVw8-jm5uPaWKkbgLp1IGzRUl9vRzwwENK-pBiNJHQoN3qO3.pctqGDYXOuHXJPBSKC2uGnooFOLYrMxbV20LJ1JIOCg")
    print(_id)
    send_text_messages_to(_id["userId"],["お前の後ろにいるよ"])