# 音频流水线

## 1. 训练音色模型（一次性）

### 数据要求
- **只用高质量原始音频**（FLAC / 320k MP3），不要用分离后的低质人声训练
- 单人独唱 20–60 首，总时长 1.5–4 小时
- 不要混入合唱、对唱、翻唱版本

### 训练步骤

```bash
bash scripts/audio/train_pipeline.sh --dataset data/train --exp myvoice --epochs 100
```

内部步骤：
1. BS-Roformer 分离人声（训练用）
2. 3.7s 切片预处理
3. f0（rmvpe）+ HuBERT 特征提取
4. RVC v2 40k 训练（batch 8，100 epoch，每 10 epoch 存权重）

### 建议参数

| 项目 | 值 |
|---|---|
| 采样率 | 40k |
| 版本 | v2 |
| batch | 8（24G 显存可 10–12） |
| epoch | 60–150（听感最好为准） |
| 底模 | f0G40k / f0D40k |

## 2. 单曲制作

```bash
cp configs/song.example.json configs/songs/mysong.json
# 填：slug、audio_original、rvc_model、output_audio、pack、lrc
bash scripts/audio/convert.sh configs/songs/mysong.json
```

流程：
1. 原曲分离（有官方伴奏则只分离人声）
2. RVC 转换：`--f0-method rmvpe --pitch 0 --index-rate 0 --protect 0.33 --rms-mix-rate 0.25`
3. 混音：人声 -15dB / 伴奏 -17dB / 峰值 -1dB（`scripts/audio/mix_song.py`）
4. 输出：`loudnorm I=-14:TP=-1.5` 320k MP3

## 3. 爆音/杂音排查清单

| 现象 | 原因 | 解决 |
|---|---|---|
| 副歌爆炸音 | 用“原曲−伴奏”相位抵消人声做输入 | 必须用 BS-Roformer 分离 |
| 句首爆音 | 单遍动态 loudnorm | 改静态增益后统一响度 |
| 回响/糊 | 分离伴奏残留 | 优先官方伴奏 |
| 整体发闷 | 训练数据含低码率/分离噪底 | 只用高质量原曲训练 |
| 高音破音 | 模型能力边界 | 换 e30/e60 检查点、降调、换音色模型 |

## 4. LRC 获取与清洗

```bash
python scripts/audio/get_lrc_qq.py '歌名'            # 搜索 QQ 音乐
python scripts/audio/get_lrc_qq.py '歌名' <songmid> <slug>  # 下载 LRC
```

清洗规则（`build_mvprops.py` 已内置）：
- 去除：作词/作曲/编曲/和声/混音/母带/制作/监制/出品/发行/策划/企划等名单行
- 去除：歌名行（`歌名 - 歌手`）、版权说明行
- 去除：`司南：` `银临：` 等歌手名前缀（对唱 LRC）
- 只保留真实歌词
