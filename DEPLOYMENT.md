# 🚀 部署指南

本文档详细说明如何将黄金价格预测系统部署到GitHub和Render平台。

## 📋 部署前准备

### 1. 系统要求

- Python 3.9+
- Git
- GitHub账户
- Render账户（免费）

### 2. 依赖检查

确保所有必需的Python包都在 `requirements.txt` 中：

```
yfinance==0.2.44
pandas==2.2.2
numpy==2.1.0
matplotlib==3.9.2
seaborn==0.13.2
scikit-learn==1.5.2
ta==0.11.0
requests==2.32.3
beautifulsoup4==4.12.3
textblob==0.17.1
vaderSentiment==3.3.2
streamlit==1.39.0
plotly==5.24.1
openai==1.51.0
python-dotenv==1.0.1
schedule==1.2.2
flask==3.0.3
flask-cors==4.0.1
deepseek==1.0.0
akshare==1.12.85
gunicorn==21.2.0
psutil==5.9.8
```

## 🌐 部署到 GitHub

### 步骤 1: 创建GitHub仓库

1. 访问 https://github.com/new
2. 输入仓库名称：`gold-price-prediction-system`
3. 选择公开或私有仓库
4. 不要初始化README、.gitignore或license
5. 点击"Create repository"

### 步骤 2: 初始化本地Git仓库

```bash
cd d:\trae\AI\gold
git init
```

### 步骤 3: 添加文件到Git

```bash
git add .
```

### 步骤 4: 提交更改

```bash
git commit -m "Initial commit: Gold price prediction system"
```

### 步骤 5: 连接到远程仓库

```bash
git remote add origin https://github.com/yourusername/gold-price-prediction-system.git
```

### 步骤 6: 推送到GitHub

```bash
git branch -M main
git push -u origin main
```

### 步骤 7: 验证部署

访问你的GitHub仓库，确认所有文件都已上传：
- https://github.com/yourusername/gold-price-prediction-system

## ☁️ 部署到 Render

Render是一个免费的云平台，支持Python应用部署。

### 步骤 1: 注册Render账户

1. 访问 https://render.com/
2. 点击"Sign Up"
3. 使用GitHub账户登录（推荐）
4. 完成注册流程

### 步骤 2: 连接GitHub到Render

1. 登录Render Dashboard: https://dashboard.render.com/
2. 点击右上角的"New +"
3. 选择"Web Service"

### 步骤 3: 配置Web Service

#### 基本信息
- **Name**: `gold-price-prediction-system`
- **Region**: Oregon (推荐，延迟较低)
- **Branch**: `main`

#### 构建和运行配置
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn backend_optimized:app --workers 1 --threads 2 --timeout 120 --bind 0.0.0.0:$PORT`

#### 高级设置
- **Instance Type**: Free (免费套餐)
- **RAM**: 512 MB
- **CPU**: 0.1 CPU

### 步骤 4: 配置环境变量

在"Environment"部分添加以下环境变量：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `PYTHON_VERSION` | `3.9.0` | Python版本 |
| `PORT` | `5000` | 应用端口 |
| `RENDER` | `true` | 标识为Render环境 |
| `HISTORICAL_DAYS` | `90` | 历史数据天数（优化） |
| `UPDATE_INTERVAL_HOURS` | `2` | 更新间隔（优化） |

### 步骤 5: 部署应用

1. 点击"Create Web Service"
2. 等待构建和部署完成（通常需要5-10分钟）
3. 查看部署日志，确认没有错误

### 步骤 6: 访问应用

部署成功后，Render会提供一个URL，例如：
- https://gold-price-prediction-system.onrender.com

访问这个URL即可使用系统。

## 🔧 Render配置文件说明

### render.yaml

```yaml
services:
  - type: web
    name: gold-price-prediction-system
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn backend_optimized:app --workers 1 --threads 2 --timeout 120 --bind 0.0.0.0:$PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.0
      - key: RENDER
        value: "true"
      - key: HISTORICAL_DAYS
        value: "90"
      - key: UPDATE_INTERVAL_HOURS
        value: "2"
      - key: PORT
        value: 5000
    plan: free
    region: oregon
```

### Procfile

```
web: gunicorn backend_optimized:app --workers 1 --threads 2 --timeout 120 --bind 0.0.0.0:$PORT
```

## 📊 Render免费套餐限制

### 资源限制

| 资源 | 限制 |
|------|------|
| 内存 | 512 MB |
| CPU | 0.1 核心共享 |
| 带宽 | 100 GB/月 |
| 构建时间 | 15分钟 |
| 睡眠时间 | 15分钟无活动后休眠 |
| 启动时间 | 休眠后30秒唤醒 |

### 优化策略

为了在免费套餐限制下稳定运行，系统已进行以下优化：

1. **减少内存使用**
   - 历史数据天数从365天减少到90天
   - 使用更高效的数据结构
   - 及时清理缓存

2. **降低CPU使用**
   - 更新间隔从1小时增加到2小时
   - 使用单worker进程
   - 优化数据获取逻辑

3. **防止休眠**
   - 设置健康检查端点
   - 使用外部监控服务（可选）

## 🛠️ 故障排除

### 问题 1: 部署失败

**症状**: 构建过程中出现错误

**解决方案**:
1. 检查 `requirements.txt` 是否包含所有依赖
2. 确认Python版本兼容性
3. 查看Render构建日志，定位具体错误
4. 检查 `Procfile` 格式是否正确

### 问题 2: 内存不足

**症状**: 应用崩溃或响应缓慢

**解决方案**:
1. 减少 `HISTORICAL_DAYS` 的值
2. 增加 `UPDATE_INTERVAL_HOURS` 的值
3. 检查是否有内存泄漏
4. 使用 `psutil` 监控内存使用

### 问题 3: 应用休眠

**症状**: 访问应用时加载缓慢

**解决方案**:
1. 设置定期ping服务（如UptimeRobot）
2. 升级到付费套餐
3. 接受首次访问需要30秒唤醒

### 问题 4: 数据获取失败

**症状**: 价格或新闻数据为空

**解决方案**:
1. 检查网络连接
2. 验证数据源是否可用
3. 查看应用日志
4. 增加重试逻辑

## 📈 监控和维护

### 健康检查

定期检查系统健康状态：

```bash
curl https://your-app.onrender.com/api/health
```

### 查看日志

在Render Dashboard中查看实时日志：
1. 进入你的Web Service
2. 点击"Logs"
3. 选择日志级别（Info, Error等）

### 更新应用

更新代码后，Render会自动重新部署：

```bash
git add .
git commit -m "Update code"
git push
```

## 🔄 持续集成/持续部署 (CI/CD)

### 自动部署

Render支持GitHub集成，当代码推送到main分支时自动部署。

### 手动部署

如果需要手动触发部署：
1. 进入Render Dashboard
2. 选择你的Web Service
3. 点击"Manual Deploy"
4. 选择分支并确认

## 📝 后续优化建议

### 短期优化

1. **添加缓存层**
   - 使用Redis缓存频繁访问的数据
   - 减少数据库查询

2. **优化数据库**
   - 使用SQLite存储历史数据
   - 定期清理旧数据

3. **添加监控**
   - 集成Sentry错误追踪
   - 设置告警通知

### 长期优化

1. **升级套餐**
   - 升级到Standard套餐获得更多资源
   - 提高并发处理能力

2. **使用CDN**
   - 静态资源使用CDN加速
   - 减少带宽消耗

3. **多区域部署**
   - 在多个区域部署实例
   - 提高可用性

## 📚 参考资源

- [Render官方文档](https://render.com/docs)
- [Flask部署指南](https://flask.palletsprojects.com/en/2.3.x/deploying/)
- [Gunicorn配置](https://docs.gunicorn.org/en/stable/settings.html)
- [Python最佳实践](https://docs.python-guide.org/)

## 🆘 获取帮助

如果遇到问题：

1. 查看 [GitHub Issues](https://github.com/yourusername/gold-price-prediction-system/issues)
2. 阅读 [Render文档](https://render.com/docs)
3. 联系维护者

---

**注意**: 本系统仅用于教育和研究目的，不构成投资建议。投资有风险，请谨慎决策。
