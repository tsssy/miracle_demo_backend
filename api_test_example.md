# 创建女性用户API测试示例

## API端点信息

- **方法**: POST
- **路径**: `/api/v1/users/female_users`
- **描述**: 根据telegram_id创建女性用户

## 请求格式

```json
{
  "telegram_id": "123456789"
}
```

## 响应格式

### 成功创建
```json
{
  "success": true
}
```

### 创建失败
```json
{
  "success": false
}
```

## 测试用例

### 1. 成功创建女性用户

**请求**:
```bash
curl -X POST "http://localhost:8000/api/v1/users/female_users" \
  -H "Content-Type: application/json" \
  -d '{
    "telegram_id": "123456789"
  }'
```

**预期响应**:
```json
{
  "success": true
}
```

### 2. telegram_id不存在

**请求**:
```bash
curl -X POST "http://localhost:8000/api/v1/users/female_users" \
  -H "Content-Type: application/json" \
  -d '{
    "telegram_id": "999999999"
  }'
```

**预期响应**:
```json
{
  "success": false
}
```

### 3. 无效的telegram_id格式

**请求**:
```bash
curl -X POST "http://localhost:8000/api/v1/users/female_users" \
  -H "Content-Type: application/json" \
  -d '{
    "telegram_id": "invalid_id"
  }'
```

**预期响应**:
```json
{
  "success": false
}
```

## 业务逻辑说明

1. **接收telegram_id**: API接收POST请求中的telegram_id参数
2. **数据库查询**: 在telegram_sessions表中查找对应的记录
3. **验证数据**: 检查记录是否存在以及是否包含final_string字段
4. **解析问题**: 从final_string中提取问题1、问题2、问题3的内容
5. **创建问题**: 将提取的问题保存到Question集合中
6. **创建用户**: 在User集合中创建女性用户记录
7. **返回结果**: 返回success状态表示是否成功创建

## 错误处理

- **telegram_id不存在**: 返回 `{"success": false}`
- **缺少final_string字段**: 返回 `{"success": false}`
- **final_string格式错误**: 返回 `{"success": false}`
- **telegram_id格式无效**: 返回 `{"success": false}`
- **数据库操作异常**: 返回 `{"success": false}`

## 数据库要求

确保telegram_sessions表中有对应的记录，格式如下：

```json
{
  "_id": 123456789,
  "gender": 1,
  "final_string": "问题1: 你最喜欢的旅行目的地是哪里？\n\n问题2: 你理想中的周末是怎么度过的？\n\n问题3: 你认为在一段关系中最重要的品质是什么？\n",
  "created_at": "2024-01-15T10:00:00Z",
  "status": "active"
}
``` 