## 启动本地服务
```bash
uvicorn app.server_run:app --host 0.0.0.0 --port 8000 --reload
```

## 访问 API 文档
```bash
http://127.0.0.1:8000/docs
```


# 测试用例

## 1. API：`/edit_answer` （男用户）编辑问题

-   **创建全新答案**:
    ```json
    {
      "telegram_id": 9168168168,
      "question_id": "6871d041c94ec9fc95dd99a7",
      "new_answer": "我喜欢蓝色。",
      "is_send": true
    }
    ```

-   **创建全新草稿**:
    ```json
    {
      "telegram_id": 9168168168,
      "question_id": "6871d041c94ec9fc95dd99a7",
      "new_answer": "我喜欢。",
      "is_send": false
    }
    ```

-   **更新答案**:
    ```json
    {
        "telegram_id": 9168168168,
        "question_id": "6871d041c94ec9fc95dd99a7",
        "new_answer": "我不喜欢。",
        "is_send": true,
        "answer_id": "687217f6d8944c0144075464"
    }
    ```

-   **更新草稿**:
    ```json
    {
        "telegram_id": 9168168168,
        "question_id": "6871d041c94ec9fc95dd99a7",
        "new_answer": "我喜欢红色。",
        "is_send": false,
        "answer_id": "687217f6d8944c0144075464"
    }
    ```
---

## 2. API：`/toggle_question_save` （男用户）收藏/取消收藏问题

-   **收藏/取消收藏一个问题**:
    -   预期：用户 `saved_question_ids` 列表中添加该问题 ID，返回 `{"is_saved": true}`。
    ```json
    {
      "telegram_id": 9168168168,
      "question_id": "6871d041c94ec9fc95dd99a7"
    }
    ```
---
## 3. API：`/get_question` （男用户）获取问题
-   **获取一个问题**:

    ```json
    {
      "telegram_id": 9168168168,
      "is_swiping_toward_left": true
    }

    ```

---

## 4. API：`/block_answer` （女用户）拉黑答案

-   **女性用户拉黑一个答案**:
    -   预期：用户的 `blocked_answer_ids` 列表中添加该答案 ID，返回 `{"success": true}`。
    ```json
    {
      "telegram_id": 123456789,
      "answer_id": "687136f3e978ca10032d9cc5"
    }
    ```
---

## 5. API：`/like_answer` （女用户）喜欢/取消喜欢答案

-   **女性用户喜欢/取消喜欢一个男性用户的答案**:
    -   预期：
        -   喜欢时：双方被配对，返回 `{"is_liked": true, "paired_telegram_id": "男方ID"}`。
        -   取消喜欢时：双方解除配对，返回 `{"is_liked": false, "paired_telegram_id": "男方ID"}`。
    ```json
    {
      "telegram_id": 123456789,
      "answer_id": "687136f3e978ca10032d9cc5"
    }
    ```
---

## 6. API：`/get_answer` （女用户）获取答案
