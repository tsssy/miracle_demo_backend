# FastAPI CORS 配置说明

## 当前配置

你的FastAPI应用已经配置了CORS中间件，支持以下域名：

### 默认允许的域名
- `https://cupid-yukio-frontend.vercel.app` - 生产环境前端地址
- `http://localhost:5173` - 本地开发环境前端地址 (Vite默认端口)
- `http://127.0.0.1:5173` - 本地IP地址

### 环境变量配置

你可以通过设置环境变量来配置CORS：

```bash
# 在 .env 文件中添加

# 方式1: 允许所有域名 (开发环境推荐)
CORS_ALLOW_ALL=true

# 方式2: 指定特定域名
CORS_EXTRA_ORIGINS=https://cupid-yukio-frontend-git-main-username.vercel.app,https://cupid-yukio-frontend-git-develop-username.vercel.app
```

## 全局允许配置

### 使用 `CORS_ALLOW_ALL=true`

当你设置 `CORS_ALLOW_ALL=true` 时：
- ✅ 允许所有域名访问
- ❌ `allow_credentials` 自动设置为 `False`
- ⚠️ 不能携带认证信息（cookies, authorization headers等）

**适用场景**：
- 开发环境测试
- 不需要认证的API
- 快速原型开发

### 使用特定域名列表

当你不设置 `CORS_ALLOW_ALL` 或设置为 `false` 时：
- ✅ 只允许指定的域名
- ✅ `allow_credentials` 设置为 `True`
- ✅ 可以携带认证信息

**适用场景**：
- 生产环境
- 需要认证的API
- 安全要求较高的应用

## Vercel Preview 部署配置

### 1. 获取Vercel Preview域名

当你创建Pull Request或推送到特定分支时，Vercel会自动生成preview域名，格式如下：
```
https://cupid-yukio-frontend-git-{branch}-{username}.vercel.app
```

### 2. 设置环境变量

在你的部署环境中设置环境变量：

**方法1：在Vercel项目设置中**
1. 进入Vercel项目仪表板
2. 点击 "Settings" → "Environment Variables"
3. 添加变量：

   **开发环境（推荐使用全局允许）**：
   - Name: `CORS_ALLOW_ALL`
   - Value: `true`

   **生产环境（使用特定域名）**：
   - Name: `CORS_EXTRA_ORIGINS`
   - Value: `https://cupid-yukio-frontend-git-main-username.vercel.app,https://cupid-yukio-frontend-git-develop-username.vercel.app`

4. 选择部署环境（Production, Preview, Development）

**方法2：在本地 .env 文件中**
```bash
# 开发环境
CORS_ALLOW_ALL=true

# 或者生产环境
CORS_EXTRA_ORIGINS=https://cupid-yukio-frontend-git-main-username.vercel.app,https://cupid-yukio-frontend-git-develop-username.vercel.app
```

## 测试CORS配置

### 1. 检查服务器日志
启动服务器后，查看日志中的CORS配置：

**全局允许模式**：
```
CORS配置: 允许所有域名 (allow_credentials=False)
```

**特定域名模式**：
```
CORS允许的域名: ['https://cupid-yukio-frontend.vercel.app', 'http://localhost:5173', ...]
```

### 2. 浏览器开发者工具
在浏览器中打开开发者工具，查看Network标签页，确认没有CORS错误。

### 3. 测试API端点
使用curl或Postman测试API端点，确认CORS头部正确设置。

## 常见问题

### Q: 为什么全局允许时不能携带认证信息？
A: 这是浏览器的安全策略。当 `allow_origins=["*"]` 时，`allow_credentials` 必须为 `False`。

### Q: 如何选择使用全局允许还是特定域名？
A: 
- **开发环境**：使用 `CORS_ALLOW_ALL=true` 更方便
- **生产环境**：使用特定域名列表更安全

### Q: Vercel preview域名经常变化怎么办？
A: 在preview环境中设置 `CORS_ALLOW_ALL=true`，在生产环境中使用特定域名。

### Q: 如何添加新的域名？
A: 设置 `CORS_EXTRA_ORIGINS` 环境变量，用逗号分隔多个域名。 