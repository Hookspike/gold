# 🥇 黄金价格预测系统

一个基于机器学习和情感分析的黄金价格预测系统，提供实时价格、技术分析、市场情绪分析和价格预测功能。

## ✨ 功能特点

- 📊 **实时价格监控**：从多个数据源获取实时黄金价格
- 📈 **技术分析**：RSI、MACD、布林带等技术指标
- 📰 **情绪分析**：基于中文金融词典的市场情绪分析
- 🔮 **价格预测**：使用机器学习模型预测未来价格
- 🛡️ **数据质量验证**：自动验证数据质量，确保数据可靠性
- 📋 **系统监控**：实时监控系统健康状态和性能指标
- 🔄 **自动更新**：每小时自动更新数据和预测

## 🏗️ 系统架构

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  前端页面   │     │  Flask后端  │     │  数据模块   │
│  (HTML/CSS) │◄────┤   API服务   │◄────┤  (Python)   │
└─────────────┘     └─────────────┘     └─────────────┘
                                      ┌─────────────┐
                                      │  数据缓存   │
                                      └─────────────┘
```

### 核心模块

| 模块 | 文件 | 功能 |
|------|------|------|
| 后端服务 | `backend.py` | Flask API服务 |
| 数据获取 | `data_fetcher.py` | 多数据源数据获取 |
| 技术分析 | `technical_analysis.py` | 技术指标计算 |
| 情绪分析 | `sentiment_analysis.py` | 市场情绪分析 |
| 价格预测 | `predictor.py` | 机器学习预测 |
| 配置管理 | `config.py` | 系统配置 |

## 📦 技术栈

### 后端
- **Python 3.9+**
- **Flask** - Web框架
- **pandas** - 数据处理
- **numpy** - 数值计算
- **scikit-learn** - 机器学习
- **ta** - 技术分析
- **requests** - HTTP请求
- **beautifulsoup4** - HTML解析
- **akshare** - 金融数据获取
- **psutil** - 系统监控

### 前端
- **HTML5/CSS3** - 页面结构
- **JavaScript** - 交互逻辑
- **Chart.js** - 数据可视化
- **Bootstrap 5** - UI框架

## 🚀 快速开始

### 本地运行

1. **克隆仓库**
```bash
git clone https://github.com/yourusername/gold-price-prediction-system.git
cd gold-price-prediction-system
```

2. **创建虚拟环境**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，配置API密钥等
```

5. **启动服务**
```bash
python backend.py
```

6. **访问系统**
打开浏览器访问：http://localhost:5000

## 🌐 部署到 Render

Render是一个免费的云平台，支持Python应用部署。

### 部署步骤

1. **准备代码**
确保代码已推送到GitHub仓库

2. **连接Render到GitHub**
- 访问 https://dashboard.render.com/
- 点击 "New +"
- 选择 "Web Service"
- 连接你的GitHub账户

3. **配置部署**
- **Repository**: 选择 `gold-price-prediction-system` 仓库
- **Branch**: 选择 `main` 分支
- **Root Directory**: 留空或设置为 `/`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn backend:app --host 0.0.0.0 --port $PORT`

4. **环境变量配置**
在Render的Environment部分添加以下变量：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `PYTHON_VERSION` | `3.9.0` | Python版本 |
| `PORT` | `5000` | 应用端口 |

5. **部署**
点击 "Create Web Service" 开始部署

### Render配置文件

项目已包含以下部署配置文件：

- `render.yaml` - Render配置文件
- `Procfile` - 进程文件
- `requirements.txt` - Python依赖

### 免费套餐限制

Render免费套餐限制：
- **内存**: 512MB
- **CPU**: 0.1个CPU核心
- **带宽**: 100GB/月
- **构建时间**: 15分钟

### 优化建议

由于Render免费套餐资源有限，建议：

1. **减少数据缓存**：降低内存使用
2. **优化更新频率**：增加更新间隔到2-4小时
3. **禁用调试模式**：设置 `debug=False`
4. **使用轻量级依赖**：选择必要的库

## 📊 数据来源

### 价格数据
- 新浪财经（实时）
- AkShare（历史）
- Kitco（历史）
- Investing.com（历史）
- YFinance（备用）

### 新闻数据
- 东方财富
- 金十数据
- 新浪财经
- 央视新闻

## 🔧 配置说明

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `GOLD_TICKER` | `XAUUSD` | 黄金交易代码 |
| `HISTORICAL_DAYS` | `365` | 历史数据天数 |
| `PREDICTION_DAYS` | `7` | 预测天数 |
| `UPDATE_INTERVAL_HOURS` | `1` | 数据更新间隔（小时） |
| `SENTIMENT_THRESHOLD` | `0.1` | 情绪阈值 |

### API接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 前端页面 |
| `/api/health` | GET | 系统健康检查 |
| `/api/price` | GET | 历史价格数据 |
| `/api/realtime` | GET | 实时价格 |
| `/api/technical` | GET | 技术指标 |
| `/api/sentiment` | GET | 情绪分析 |
| `/api/predictions` | GET | 价格预测 |
| `/api/support-resistance` | GET | 支撑阻力位 |
| `/api/summary` | GET | 系统摘要 |
| `/api/refresh` | POST | 手动刷新数据 |

## 📈 系统监控

### 健康检查API

```bash
curl https://your-app.onrender.com/api/health
```

返回示例：
```json
{
  "status": "healthy",
  "timestamp": "2026-02-05T18:07:57.590270",
  "uptime_hours": 0.01,
  "services": {
    "data_fetcher": true,
    "predictor": true,
    "sentiment_analyzer": true,
    "technical_analyzer": true
  },
  "cache": {
    "price_data": true,
    "technical_data": true,
    "sentiment_data": true,
    "predictions": true,
    "last_update": "2026-02-05T18:07:20.545870"
  },
  "performance": {
    "update_count": 2,
    "last_update_duration": 0.92,
    "api_call_count": 6,
    "error_count": 0,
    "memory_usage_mb": 126.9,
    "cpu_percent": 38.6
  },
  "data_quality": {
    "price_data_count": 33,
    "sentiment_data_count": 10,
    "predictions_available": true
  }
}
```

## 🛠️ 故障排除

### 常见问题

1. **内存不足错误**
   - 解决方案：减少历史数据天数（`HISTORICAL_DAYS`）
   - 增加更新间隔（`UPDATE_INTERVAL_HOURS`）

2. **数据获取失败**
   - 检查网络连接
   - 查看日志文件 `gold_system.log`
   - 验证数据源可用性

3. **部署失败**
   - 确保 `requirements.txt` 包含所有依赖
   - 检查 `Procfile` 格式正确
   - 查看Render构建日志

## 📝 开发指南

### 添加新功能

1. 在对应模块中添加功能
2. 更新API接口（如需要）
3. 更新前端页面（如需要）
4. 测试功能
5. 提交代码

### 代码规范

- 使用Python类型提示
- 添加详细的文档字符串
- 遵循PEP 8代码风格
- 编写单元测试

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📧 维护者

- [你的名字] - 主要开发者

## 📞 联系方式

- 问题反馈：[GitHub Issues](https://github.com/yourusername/gold-price-prediction-system/issues)
- 邮箱：your.email@example.com

## 🙏 致谢

感谢以下开源项目和数据源：
- AkShare - 金融数据获取
- Chart.js - 数据可视化
- Flask - Web框架
- scikit-learn - 机器学习

---

**注意**：本系统仅用于教育和研究目的，不构成投资建议。投资有风险，请谨慎决策。
