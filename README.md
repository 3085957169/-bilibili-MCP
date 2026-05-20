<img width="1276" height="800" alt="Snipaste_2026-05-20_16-22-45" src="https://github.com/user-attachments/assets/3b0c3fb5-b0a4-4b8a-8eb7-afc197dd11ca" />
# Bilibili MCP

通过 MCP (Model Context Protocol) 让 AI 助手搜索 B 站视频、转换成音频并在线播放。

## 功能

| 工具 | 说明 |
|------|------|
| `search_videos` | 按关键词搜索 B 站视频 |
| `play_audio` | 搜索并直接在浏览器播放音频 |
| `download_song` | 下载视频并转换为 mp3 |
| `get_stream_url` | 获取音频流地址 |
| `list_songs` | 列出已下载的音频文件 |
| `delete_song` | 删除已下载的音频 |
| `get_settings` | 查看服务器设置 |

## 安装

```bash
git clone https://github.com/3085957169/-bilibili-MCP.git
cd -bilibili-MCP/mcp-music
pip install -r requirements.txt
```

## 配置 MCP

### Claude Code

在项目目录或 `~/.claude/` 下创建 `.mcp.json`：

```json
{
  "mcpServers": {
    "music": {
      "command": "python",
      "args": ["路径/mcp-music/server.py"]
    }
  }
}
```

### 其他 MCP 客户端

```json
{
  "mcpServers": {
    "music": {
      "command": "python",
      "args": ["路径/mcp-music/server.py"]
    }
  }
}
```

> macOS / Linux 上 `command` 改为 `python3`

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `MUSIC_BASE_URL` | 音乐服务后端地址 | `http://47.108.64.39:50282` |

```json
{
  "mcpServers": {
    "music": {
      "command": "python",
      "args": ["路径/mcp-music/server.py"],
      "env": {
        "MUSIC_BASE_URL": "http://你的服务器:50282"
      }
    }
  }
}
```

## 使用示例

对话式交互，无需手动操作：

```
用户：搜索陈奕迅陀飞轮
AI：    [列表 1. Hi-res版 2. 现场版 3. MV ...]
用户：1
AI：    [转换 + 浏览器自动打开播放]
```
