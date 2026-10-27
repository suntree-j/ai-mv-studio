# Web 应用路线图

把本地流水线升级为在线服务，目标：用户上传/选择歌曲 → 选音色 → 自动生成翻唱 + MV。

## 阶段 1：API 化（2–3 周）

- **FastAPI** 后端，任务模型：
  - `train_job`（音色训练，长任务）
  - `song_job`（分离→转换→混音）
  - `mv_job`（出图→渲染→合成）
- 任务队列：Celery / RQ + Redis；GPU worker 单独部署
- 存储：S3/MinIO（音频、图片、成片），Postgres 存元数据
- 接口：
  - `POST /voices` 训练音色
  - `POST /songs` 创建歌曲任务
  - `GET /jobs/{id}` 查询进度（WebSocket/SSE）
  - `GET /songs/{id}/download`

## 阶段 2：前端（3–4 周）

- **Next.js + TypeScript + Tailwind**
- 页面：
  - 工作台：歌曲列表、任务状态、进度条
  - 训练向导：上传音频 → 质量检测 → 训练
  - 制作页：上传原曲/填歌词 → 选音色 → 生成
  - 预览：在线播放、逐镜预览、重新出图
  - 导出：MP3/MV 下载
- 组件：任务卡片、镜头时间轴编辑器、歌词对齐预览

## 阶段 3：多租户与计费（可选）

- 用户体系（OAuth）
- 配额/订阅（Stripe）
- 任务优先级队列、GPU 资源调度
- 内容审核：合规声明、禁止冒充、AI 标识水印

## 技术选型建议

| 层 | 选择 |
|---|---|
| 前端 | Next.js 15 + Tailwind + shadcn/ui |
| 后端 | FastAPI + Pydantic + SQLAlchemy |
| 队列 | Celery + Redis |
| 存储 | MinIO（自建）/ S3 |
| 部署 | Docker Compose（开发）→ K8s（生产） |
| GPU | 独立 worker 节点，按队列消费 |

## 关键难点

1. **长任务体验**：训练/渲染分钟级，需要进度上报与断点续跑
2. **GPU 排队**：单卡串行，多卡按 job 分片
3. **文件体积**：成片数百 MB，需要分片上传/下载
4. **可复现**：每个 job 记录模型版本、seed、参数
