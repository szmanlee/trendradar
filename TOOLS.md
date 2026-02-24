# TOOLS.md - Local Notes

## 网关主机

- **gateway-server** → 192.168.32.26 (当前运行 OpenClaw 的主机)

---

### QQ Bot (x26.bot)

| 配置项 | 值 |
|--------|-----|
| Bot QQ | 3889976476 |
| 名称 | x26.bot |
| AppID | 102863490 |
| Token | Khtth3CtVdvpWWt1cA7uwwzPVShMl4B4 |
| AppSecret | KKLMOQTWaejou07EMUclu4EPamyBOcq4 |
| 管理员 QQ | 42543 |

---

### Cameras

- (待添加)

### SSH

- (待添加)

### TTS (语音合成)

| 配置项 | 值 | 说明 |
|--------|-----|------|
| **Skill** | voice-reply | 本地 TTS via sherpa-onnx + Piper |
| **sherpa-onnx** | `/opt/sherpa-onnx` | TTS 运行时 |
| **voices** | `/opt/piper-voices` | 语音模型目录 |
| **voices list** | thorsten (de), ryan (en) | 德语 + 英语 |
| **ffmpeg** | 需安装 | 音频转换 |

#### 安装命令

```bash
# 1. 安装 sherpa-onnx
sudo mkdir -p /opt/sherpa-onnx
cd /opt/sherpa-onnx
curl -L -o sherpa.tar.bz2 "https://github.com/k2-fsa/sherpa-onnx/releases/download/v1.12.23/sherpa-onnx-v1.12.23-linux-x64-shared.tar.bz2"
sudo tar -xjf sherpa.tar.bz2 --strip-components=1
rm sherpa.tar.bz2

# 2. 下载语音模型 (德语 thorsten)
sudo mkdir -p /opt/piper-voices
cd /opt/piper-voices
curl -L -o thorsten.tar.bz2 "https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-de_DE-thorsten-medium.tar.bz2"
sudo tar -xjf thorsten.tar.bz2 && rm thorsten.tar.bz2

# 3. 下载语音模型 (英语 ryan)
curl -L -o ryan.tar.bz2 "https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-en_US-ryan-high.tar.bz2"
sudo tar -xjf ryan.tar.bz2 && rm ryan.tar.bz2

# 4. 安装 ffmpeg
sudo apt install -y ffmpeg

# 5. 设置环境变量 (添加到 ~/.bashrc 或 OpenClaw service)
export SHERPA_ONNX_DIR="/opt/sherpa-onnx"
export PIPER_VOICES_DIR="/opt/piper-voices"
```

#### 可用语音

| 语言 | 语音 | 质量 |
|------|------|------|
| 德语 | thorsten | medium |
| 英语 | ryan | high |
