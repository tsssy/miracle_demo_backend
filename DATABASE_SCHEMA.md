# 数据库 Schema 定义

本文档详细定义了项目中使用的 MongoDB 数据库的集合（Collections）结构。

---

## 集合 `User`

存储用户的基本信息、关系、以及与问题和答案的关联。

| 字段名 (Field Name) | 数据类型 (Type) | 描述 (Description) | 备注 (Notes) |
| ------------------- | --------------- | ------------------ | ------------ |
| `_id` | `Number` | 用户唯一标识符 | **核心：直接使用用户的 `telegram_id` 作为主键** |
| `telegram_id` | `Number` | 用户的 Telegram ID | 与 `_id` 相同，为了查询方便和清晰性可以保留 |
| `gender` | `Number` | 用户性别 |  1-女，2-男，3-other|
| `question_list` | `Array<ObjectId>` | 用户创建的问题ID列表 | 对于男性，此列表为空 |
| `answer_list` | `Array<ObjectId>` | 用户提交的答案ID列表 | 对于女性，此列表为空 |
| `paired_user` | `Array<Number>` | 与该用户配对成功的用户 `telegram_id` 列表 | |
| `profile_photo` | `Number` | 用户的头像标识 | 具体含义待定 (e.g., 文件ID) |
| `mode` | `Number` | 用户寻求的关系模式 | 例如: `1`=friends, `2`=long-term, `3`=short-term |
| `profile` | `Object` | 用户的详细个人资料 | 结构灵活，可存储如昵称、简介等 |
| `model_id` | `ObjectId` | 用户关联的AI模型ID | 用于特定AI功能 |
| `saved_list_question`| `Array<ObjectId>` | 收藏的问题ID列表 | 对于女性，此列表为空 |
| `saved_list_answer` | `Array<ObjectId>` | 收藏的答案ID列表 | 对于男性，此列表为空 |

---

## 集合 `Question`

存储由女性用户创建的问题。

| 字段名 (Field Name) | 数据类型 (Type) | 描述 (Description) | 备注 (Notes) |
| ------------------- | --------------- | ------------------ | ------------ |
| `_id` | `ObjectId` | 问题唯一标识符 | 由 MongoDB 自动生成 |
| `content` | `String` | 问题的文本内容 | |
| `telegram_id` | `Number` | 创建该问题的用户的 `telegram_id` | |
| `is_draft` | `Boolean` | 该问题是否为草稿状态 | `true` 表示是草稿，未发布 |
| `created_at` | `Datetime` | 问题的创建时间 | |
| `answer_list` | `Array<ObjectId>` | 回答了此问题的所有答案 `_id` 列表 | |
| `blocked_answer_list`| `Array<ObjectId>` | 被提问者屏蔽的答案 `_id` 列表 | 应为 `answer_list` 的子集 |
| `liked_answer_list` | `Array<ObjectId>` | 被提问者“喜欢”的答案 `_id` 列表 | 应为 `answer_list` 的子集 |
| `is_active` | `Boolean` | 问题是否有效 | `false` 表示提问者删除了该问题 |

---

## 集合 `Answer`

存储由男性用户对问题创建的答案。

| 字段名 (Field Name) | 数据类型 (Type) | 描述 (Description) | 备注 (Notes) |
| ------------------- | --------------- | ------------------ | ------------ |
| `_id` | `ObjectId` | 答案唯一标识符 | 由 MongoDB 自动生成 |
| `question_id` | `ObjectId` | 该答案对应的问题 `_id` | |
| `telegram_id` | `Number` | 创建该答案的用户的 `telegram_id` | |
| `content` | `String` | 答案的文本内容 | **新增字段**，用于存储 `new_answer` |
| `is_draft` | `Boolean` | 该答案是否为草稿状态 | `true` 表示是草稿，未发送 |
| `created_at` | `Datetime` | 答案的创建时间 | |
| `liked_user_ids` | `Array<Number>` | 点赞了该答案的所有用户的 `telegram_id` 列表 | | 