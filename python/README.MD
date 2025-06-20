# MKV 视频字幕提取

提取 MKV 的字幕轨道成独立字幕文件，便于后续翻译。

## 用法

### 环境

> 基于 [uv][]

```bash
uv sync
```

### GUI

```python
uv run src/gui.py
```

### CLI

```python
uv run src/main.py path_to_mkv_file
```

## 依赖

需要安装 [MKVToolNix][MKVToolNix]，并将其安装目录添加到环境变量中，即在命令行或终端中能够运行 `mkvinfo` 以及 `mkvextract` 命令

[MKVToolNix]: https://mkvtoolnix.download/downloads.html
[uv]: https://docs.astral.sh/uv/
