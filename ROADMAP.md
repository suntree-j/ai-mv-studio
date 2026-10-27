# Roadmap

## v0.1（当前）
- [x] 本地音频流水线（RVC 训练/转换/混音）
- [x] 交付包规范（提示词/时间轴/style）
- [x] Flux 批量出图脚本
- [x] Remotion PackMV 组件（运镜/叠化/片头/书法歌词）
- [x] LRC 抓取与清洗
- [x] 文档与示例

## v0.2
- [ ] CLI 统一入口 `ai-mv`（click/typer）
- [ ] 配置文件校验（JSON Schema）
- [ ] 失败重试与断点续跑
- [ ] 单元测试（props 构建、歌词清洗）
- [ ] Docker Compose 一键环境

## v0.3（Web）
- [ ] FastAPI 任务服务 + Celery/Redis
- [ ] Next.js 工作台（上传/预览/进度/下载）
- [ ] 对象存储（MinIO/S3）
- [ ] 多用户与配额

## v1.0（App）
- [ ] React Native (Expo) 客户端
- [ ] 推送/分享/AI 标识
- [ ] 音色市场（合规审查）
