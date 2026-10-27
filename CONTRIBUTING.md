# 贡献指南

## 开发环境

```bash
git clone <repo>
cd ai-mv-studio
cp scripts/common/env.sh.example scripts/common/env.sh
pip install -r requirements-dev.txt   # 可选
```

## 目录约定

- `scripts/`：可执行脚本，参数通过 CLI/env 传入，不写死路径
- `docs/`：文档更新与代码同 PR
- `remotion/`：前端组件；不要提交 node_modules 与素材
- `packs/`：只提交 schema 与示例，不提交真实歌曲交付包

## 提 PR

1. Fork & 创建分支 `feat/xxx` / `fix/xxx`
2. 改代码 + 更新文档
3. 本地跑通：`python scripts/mv/render_batch.py --only demo`
4. 提交 PR，说明改动与验证方式

## 不允许提交

- 歌曲音频、歌词全文、音色模型、生成图片/视频
- 个人隐私信息、服务器密码/密钥
- 未经授权的声音样本

## 问题反馈

请附：命令、报错、环境（GPU/系统/Python/Node 版本）。
