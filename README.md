# HTML 页游大厅

这是一个静态 HTML 页游入口项目，首页为 `index.html`，可以直接部署到 GitHub Pages、Netlify、Vercel 等静态网站平台。

## 当前游戏

- `五子棋.html`：棋盘对弈类游戏
- `星际猎手.html`：太空射击类游戏
- `消消乐.html`：配对消除类游戏

## 文件说明

```text
娱乐/
├─ index.html          # 静态网站首页，上线时的入口文件
├─ 五子棋.html          # 五子棋游戏
├─ 星际猎手.html        # 星际猎手游戏
├─ 消消乐.html          # 消消乐游戏
├─ app.py              # 本地 Python 启动器，可选
├─ requirements.txt    # Streamlit Cloud 依赖文件，可选
└─ README.md           # 项目说明
```


## 本地预览

进入目录：

```powershell
cd D:\Python\娱乐
```

启动静态预览服务：

```powershell
python -m http.server 8891 --bind 127.0.0.1
```

浏览器打开：

```text
http://127.0.0.1:8891/
```

停止服务：在运行命令的窗口按 `Ctrl+C`。

## GitHub Pages 上线步骤

1. 登录 GitHub。
2. 新建一个仓库，例如 `html-games`。
3. 把以下文件上传到仓库根目录：

```text
index.html
五子棋.html
星际猎手.html
消消乐.html
```

4. 打开仓库的 `Settings`。
5. 进入 `Pages`。
6. 在 `Build and deployment` 中设置：

```text
Source: Deploy from a branch
Branch: main
Folder: /root
```

7. 保存后等待 GitHub 部署完成。
8. 部署完成后访问地址一般是：

```text
https://你的用户名.github.io/html-games/
```

## Netlify 上线步骤

1. 打开 Netlify 并登录。
2. 点击 `Add new site`。
3. 选择从 GitHub 导入仓库，或直接拖拽上传文件夹。
4. 如果拖拽上传，上传包含以下文件的文件夹：

```text
index.html
五子棋.html
星际猎手.html
消消乐.html
```

5. Netlify 部署完成后会生成一个公开访问地址。


## 更新游戏

如果要新增游戏：

1. 把新的 `.html` 游戏文件放到本目录。
2. 在 `index.html` 中新增一个游戏卡片链接。
3. 重新上传到静态网站平台。

如果只是本地运行 `app.py`，它会自动扫描同级目录下的 HTML 文件；但静态上线用的 `index.html` 不会自动扫描，需要手动添加入口。
