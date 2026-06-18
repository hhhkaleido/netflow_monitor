# NetFlow Monitor

NetFlow Monitor 是一个基于 FastAPI、SQLAlchemy、MySQL 和 Python 的网络流量分析后端。系统支持 CSV/PCAP 数据导入、流量查询、统计分析和多线程批量处理。

## 功能

- FastAPI REST API 与 OpenAPI 文档
- MySQL 流量记录存储及索引
- CSV 单线程批量导入
- PCAP/PCAPNG 转 CSV 后导入
- 生产者消费者模式并发导入
- 最近流量及源 IP、目标 IP 条件查询
- 热门源 IP、目标端口、协议分布和总览统计
- Python 网络拓扑可视化

## 项目结构

```text
backend/
  app/
    routers/       HTTP 路由
    services/      业务逻辑
    utils/         CSV 解析工具
    config.py      环境变量配置
    crud.py        数据访问
    database.py    SQLAlchemy 连接
    models.py      ORM 模型
    schemas.py     API 响应模型
  requirements.txt
  run.py
py/
  extract_pcap.py
  visualize_graph.py
  visualize_3d.py
sql/
  schema.sql
  indexes.sql
data/              示例 CSV 数据
```

后端调用链：

```text
router -> service -> crud -> SQLAlchemy Session -> MySQL
```

## 环境要求

- Python 3.10+
- MySQL 8.x

## 安装

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
```

## 初始化数据库

```powershell
mysql -u root -p < sql\schema.sql
mysql -u root -p netflow_monitor < sql\indexes.sql
```

## 配置

数据库连接信息通过环境变量提供，不应写入源码或提交到 Git。

```powershell
$env:MYSQL_HOST="127.0.0.1"
$env:MYSQL_PORT="3306"
$env:MYSQL_USER="root"
$env:MYSQL_PASSWORD="your-password"
$env:MYSQL_DATABASE="netflow_monitor"
$env:BATCH_SIZE="1000"
$env:IMPORT_WORKER_COUNT="4"
```

也可以在本地使用 `.env` 管理敏感配置，但该文件已被 `.gitignore` 排除。

## 启动

```powershell
cd backend
python run.py
```

- API：`http://127.0.0.1:8000`
- Swagger：`http://127.0.0.1:8000/docs`
- 健康检查：`http://127.0.0.1:8000/health`

健康检查预期返回：

```json
{"status":"ok"}
```

## API

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/health` | 服务健康检查 |
| POST | `/traffic/import?csv_path=data/network_data.csv` | 单线程导入 CSV |
| POST | `/traffic/import-concurrent?csv_path=data/network_data.csv` | 并发导入 CSV |
| POST | `/traffic/import-pcap?pcap_path=data/sample.pcap` | PCAP 转换并导入 |
| GET | `/traffic/search?src_ip=...&dst_ip=...&limit=20` | 按源/目标 IP 查询 |
| GET | `/traffic/recent?limit=20` | 最近流量记录 |
| GET | `/stats/top-src-ip?limit=10` | 热门源 IP |
| GET | `/stats/top-dst-port?limit=10` | 目标端口排行 |
| GET | `/stats/protocol-stats` | 协议分布 |
| GET | `/stats/summary` | 流量统计总览 |
| GET | `/stats/src-ip-aly?src_ip=...` | 查询源 IP 聚合数据 |

文件参数支持项目根目录相对路径和绝对路径。

## CSV 格式

解析器兼容规范字段和旧数据字段。示例：

```csv
Source,Destination,Protocol,SrcPort,DstPort,DataSize,Duration
112.65.219.203,183.94.22.40,17,1113,52500,156,120.492
```

协议号 `1`、`6`、`17` 分别转换为 `ICMP`、`TCP`、`UDP`，其他值转换为 `OTHER`。

## 当前完成情况

| 模块 | 状态 |
| --- | --- |
| FastAPI 服务与健康检查 | 完成 |
| MySQL 表、ORM 与索引 | 完成 |
| CSV 单线程导入 | 完成 |
| 基础查询 API | 部分完成 |
| 统计 API | 完成 |
| PCAP 导入 | 完成 |
| 多线程导入 | 完成 |

基础查询目前支持源 IP、目标 IP 和最近记录查询，尚未实现协议、端口、时间范围筛选以及完整分页。

## 安全说明

- 不要把真实数据库密码写入 `backend/app/config.py`。
- 不要提交 `.env`、私钥、访问令牌或凭据文件。
- 不要提交包含敏感网络信息的 PCAP 和生成数据。
- `AGENTS.md` 是本地开发说明，已被 `.gitignore` 排除。
- 提交前运行 `git status --ignored` 检查待上传文件。
