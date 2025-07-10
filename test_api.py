import httpx

BASE_URL = "http://localhost:8000/api/v1/users"

def test_create_new_female_user():
    print("测试新建女用户接口...")
    data = {"telegram_id": 10001}
    resp = httpx.post(f"{BASE_URL}/female_users", json=data)
    print("请求体:", data)
    print("响应状态码:", resp.status_code)
    print("响应内容:", resp.text)
    print("响应类型:", resp.headers.get("content-type"))
    if resp.headers.get("content-type", "").startswith("application/json"):
        print("响应JSON:", resp.json())
        assert resp.status_code == 200
        assert resp.json().get("success") is True
    else:
        print("不是JSON响应")
        assert False, "响应不是JSON"

def test_create_new_male_user():
    print("测试新建男用户接口...")
    data = {"telegram_id": 10002, "mode": 1}
    resp = httpx.post(f"{BASE_URL}/male_users", json=data)
    print("请求体:", data)
    print("响应状态码:", resp.status_code)
    print("响应内容:", resp.text)
    print("响应类型:", resp.headers.get("content-type"))
    if resp.headers.get("content-type", "").startswith("application/json"):
        print("响应JSON:", resp.json())
        assert resp.status_code == 200
        assert resp.json().get("success") is True
    else:
        print("不是JSON响应")
        assert False, "响应不是JSON"

def test_get_user_gender():
    print("测试获取性别接口...")
    data = {"telegram_id": 10001}
    resp = httpx.post(f"{BASE_URL}/telegram_session", json=data)
    print("请求体:", data)
    print("响应状态码:", resp.status_code)
    print("响应内容:", resp.text)
    print("响应类型:", resp.headers.get("content-type"))
    if resp.headers.get("content-type", "").startswith("application/json"):
        print("响应JSON:", resp.json())
        assert resp.status_code == 200
        assert resp.json().get("gender") == 1
    else:
        print("不是JSON响应")
        assert False, "响应不是JSON"

if __name__ == "__main__":
    test_create_new_female_user()
    test_create_new_male_user()
    test_get_user_gender()
    print("全部测试通过！") 