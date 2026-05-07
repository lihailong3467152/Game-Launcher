# HTML 游戏启动器

这个目录里的 `app.py` 会扫描同级目录下的 `*.html` 文件，并生成一个本地游戏选择页。

## 使用方法

1. 进入目录：

   ```powershell
   cd D:\Python\娱乐
   ```

2. 启动：

   ```powershell
   python app.py
   ```

3. 浏览器会自动打开游戏选择页。点击游戏名称即可运行对应 HTML 游戏。

4. 停止服务：在运行窗口按 `Ctrl+C`。

## 可选参数

只启动服务，不自动打开浏览器：

```powershell
python app.py --no-browser
```

指定端口：

```powershell
python app.py --port 9000
```

## 新增游戏

把新的 `.html` 游戏文件放到本目录，和 `app.py` 同级即可。重新打开或刷新启动页后会自动显示。

## 依赖

不需要第三方 Python 依赖，使用 Python 标准库即可。建议 Python 3.8 或更高版本。
