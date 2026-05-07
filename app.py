from __future__ import annotations

import argparse
import html
import socket
import sys
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_PORT = 8765

CN_TITLE = "&#28216;&#25103;&#22823;&#21381;"
CN_SUBTITLE = "HTML &#39029;&#28216;&#21551;&#21160;&#20013;&#24515;"
CN_SERVER = "&#26412;&#22320;&#26381;&#21153;"
CN_READY = "&#21487;&#36827;&#20837;"
CN_GAME_COUNT = "&#28216;&#25103;&#25968;&#37327;"
CN_LIBRARY = "&#28216;&#25103;&#24211;"
CN_ALL_GAMES = "&#20840;&#37096;&#28216;&#25103;"
CN_PLAY = "&#24320;&#22987;&#28216;&#25103;"
CN_EMPTY = "&#24403;&#21069;&#30446;&#24405;&#27809;&#26377;&#25214;&#21040; HTML &#28216;&#25103;&#25991;&#20214;&#12290;"
CN_TIP_TITLE = "&#36816;&#34892;&#29366;&#24577;"
CN_TIP_COPY = "&#26032;&#22686; HTML &#25991;&#20214;&#21518;&#21047;&#26032;&#27492;&#39029;&#21363;&#21487;&#20986;&#29616;&#22312;&#21015;&#34920;&#20013;&#12290;"
CN_STATUS_ONLINE = "&#22312;&#32447;"
CN_LOCAL = "&#26412;&#22320;"

GOMOKU_NAME = "\u4e94\u5b50\u68cb"
STAR_HUNTER_NAME = "\u661f\u9645\u730e\u624b"
LIANLIANKAN_NAME = "\u8fde\u8fde\u770b"


def find_html_games() -> list[Path]:
    return sorted(
        (p for p in BASE_DIR.glob("*.html") if p.is_file()),
        key=lambda p: p.name.casefold(),
    )


def game_theme(game: Path) -> tuple[str, str]:
    stem = game.stem
    if GOMOKU_NAME in stem:
        return "gomoku", "BOARD"
    if STAR_HUNTER_NAME in stem:
        return "star-hunter", "STG"
    if LIANLIANKAN_NAME in stem:
        return "match-pair", "PAIR"
    return "default", "HTML"


def build_cover(theme: str, badge: str) -> str:
    if theme == "gomoku":
        stones = "\n".join(
            f'<span class="stone stone-{"black" if i % 2 == 0 else "white"}"></span>'
            for i in range(9)
        )
        return f"""
              <span class="cover cover-gomoku" aria-hidden="true">
                <span class="badge">{badge}</span>
                <span class="gomoku-board">
                  {stones}
                </span>
              </span>
        """
    if theme == "star-hunter":
        stars = "\n".join(f'<span class="star star-{i}"></span>' for i in range(1, 9))
        return f"""
              <span class="cover cover-star" aria-hidden="true">
                <span class="badge">{badge}</span>
                {stars}
                <span class="laser laser-a"></span>
                <span class="laser laser-b"></span>
                <span class="enemy-ship"></span>
                <span class="player-ship"></span>
              </span>
        """
    if theme == "match-pair":
        tiles = "\n".join(
            f'<span class="match-tile tile-{i}">{entity}</span>'
            for i, entity in enumerate(
                [
                    "&#9733;",
                    "&#9679;",
                    "&#9650;",
                    "&#9733;",
                    "&#9679;",
                    "&#9632;",
                    "&#9650;",
                    "&#9632;",
                ],
                start=1,
            )
        )
        return f"""
              <span class="cover cover-match" aria-hidden="true">
                <span class="badge">{badge}</span>
                <span class="match-grid">
                  {tiles}
                </span>
                <span class="link-line"></span>
              </span>
        """
    return f"""
              <span class="cover cover-default" aria-hidden="true">
                <span class="badge">{badge}</span>
                <span class="default-screen"></span>
              </span>
    """


def build_index_page() -> bytes:
    games = find_html_games()
    if games:
        cards = "\n".join(
            f"""
            <a class="game-card game-card-{theme}" href="/{quote(game.name)}">
              {build_cover(theme, badge)}
              <span class="card-body">
                <span class="game-title">{html.escape(game.stem)}</span>
                <span class="game-file">{html.escape(game.name)}</span>
                <span class="play-row">
                  <span class="play-button">{CN_PLAY}</span>
                  <span class="status-dot">{CN_READY}</span>
                </span>
              </span>
            </a>
            """
            for game in games
            for theme, badge in [game_theme(game)]
        )
    else:
        cards = f'<div class="empty">{CN_EMPTY}</div>'

    page = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{CN_TITLE}</title>
  <style>
    :root {{
      color-scheme: dark;
      --bg: #111623;
      --bg-2: #1a2030;
      --panel: rgba(28, 35, 51, .92);
      --panel-2: rgba(20, 26, 39, .96);
      --text: #f4f7fb;
      --muted: #aab5c8;
      --line: rgba(255, 255, 255, .14);
      --gold: #f6c95f;
      --gold-2: #a8792b;
      --cyan: #56d6ff;
      --green: #55d68a;
      --red: #e65d5d;
      --shadow: rgba(0, 0, 0, .35);
    }}
    * {{
      box-sizing: border-box;
    }}
    body {{
      margin: 0;
      min-height: 100vh;
      font-family: "Microsoft YaHei", "Segoe UI", Arial, sans-serif;
      background:
        linear-gradient(180deg, rgba(255,255,255,.03), rgba(255,255,255,0) 280px),
        repeating-linear-gradient(90deg, rgba(255,255,255,.035) 0 1px, transparent 1px 120px),
        linear-gradient(135deg, #111623 0%, #23202f 44%, #132531 100%);
      color: var(--text);
    }}
    body::before {{
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      background:
        linear-gradient(90deg, rgba(246,201,95,.12), transparent 28%, transparent 72%, rgba(86,214,255,.1)),
        radial-gradient(circle at 50% 0%, rgba(255,255,255,.08), transparent 34%);
    }}
    .shell {{
      position: relative;
      z-index: 1;
      width: min(1180px, calc(100% - 32px));
      margin: 0 auto;
      padding: 24px 0 40px;
    }}
    .topbar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 18px;
      min-height: 64px;
      padding: 0 18px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(15, 20, 31, .72);
      box-shadow: 0 18px 50px var(--shadow);
      backdrop-filter: blur(10px);
    }}
    .brand {{
      display: flex;
      align-items: center;
      gap: 12px;
      min-width: 0;
    }}
    .brand-mark {{
      display: grid;
      place-items: center;
      width: 42px;
      height: 42px;
      border: 1px solid rgba(246,201,95,.5);
      border-radius: 8px;
      background: linear-gradient(145deg, #3a2d19, #171d2c);
      color: var(--gold);
      font-weight: 900;
      box-shadow: inset 0 0 16px rgba(246,201,95,.22);
    }}
    h1 {{
      margin: 0;
      font-size: 24px;
      font-weight: 800;
      letter-spacing: 0;
      line-height: 1.15;
    }}
    .sub {{
      margin: 3px 0 0;
      color: var(--muted);
      font-size: 13px;
    }}
    .server-pill {{
      display: flex;
      align-items: center;
      gap: 10px;
      flex: 0 0 auto;
      min-height: 34px;
      padding: 0 12px;
      border: 1px solid rgba(85,214,138,.38);
      border-radius: 999px;
      background: rgba(20, 74, 49, .34);
      color: #c8ffde;
      font-size: 13px;
      white-space: nowrap;
    }}
    .server-pill::before {{
      content: "";
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--green);
      box-shadow: 0 0 10px var(--green);
    }}
    .hero {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) 280px;
      gap: 18px;
      margin-top: 18px;
      align-items: stretch;
    }}
    .banner {{
      min-height: 188px;
      padding: 26px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background:
        linear-gradient(110deg, rgba(17,22,35,.96), rgba(32,42,62,.82) 58%, rgba(93,59,43,.75)),
        repeating-linear-gradient(0deg, rgba(255,255,255,.045) 0 2px, transparent 2px 18px);
      box-shadow: 0 18px 50px var(--shadow);
      overflow: hidden;
    }}
    .banner-kicker {{
      display: inline-flex;
      align-items: center;
      gap: 9px;
      height: 30px;
      padding: 0 11px;
      border: 1px solid rgba(246,201,95,.36);
      border-radius: 999px;
      background: rgba(246,201,95,.11);
      color: #ffe5a5;
      font-size: 13px;
      font-weight: 700;
    }}
    .banner-title {{
      max-width: 620px;
      margin: 18px 0 0;
      font-size: 42px;
      line-height: 1.08;
      letter-spacing: 0;
      font-weight: 900;
    }}
    .banner-title span {{
      color: var(--gold);
    }}
    .banner-meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 22px;
    }}
    .meta-item {{
      display: flex;
      align-items: center;
      gap: 8px;
      min-height: 34px;
      padding: 0 12px;
      border: 1px solid rgba(255,255,255,.14);
      border-radius: 8px;
      background: rgba(255,255,255,.07);
      color: #d8e1f0;
      font-size: 13px;
    }}
    .meta-item strong {{
      color: var(--text);
      font-size: 15px;
    }}
    .side-panel {{
      padding: 18px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      box-shadow: 0 18px 50px var(--shadow);
    }}
    .side-title {{
      margin: 0 0 14px;
      font-size: 16px;
      font-weight: 800;
    }}
    .stat-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 12px 0;
      border-top: 1px solid rgba(255,255,255,.1);
      color: var(--muted);
      font-size: 13px;
    }}
    .stat-row strong {{
      color: var(--text);
      font-size: 20px;
    }}
    .tip {{
      margin-top: 14px;
      padding: 12px;
      border: 1px solid rgba(86,214,255,.22);
      border-radius: 8px;
      background: rgba(86,214,255,.08);
      color: #d7f5ff;
      font-size: 13px;
      line-height: 1.55;
    }}
    .library {{
      margin-top: 18px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(14, 18, 28, .64);
      box-shadow: 0 18px 50px var(--shadow);
      overflow: hidden;
    }}
    .library-head {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 14px;
      padding: 16px 18px;
      border-bottom: 1px solid var(--line);
      background: rgba(255,255,255,.04);
    }}
    .library-title {{
      margin: 0;
      font-size: 18px;
      font-weight: 800;
    }}
    .tab {{
      height: 32px;
      padding: 0 12px;
      border: 1px solid rgba(246,201,95,.34);
      border-radius: 999px;
      background: rgba(246,201,95,.12);
      color: #ffe5a5;
      font-size: 13px;
      font-weight: 700;
      line-height: 30px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(238px, 1fr));
      gap: 16px;
      padding: 18px;
    }}
    .game-card {{
      display: grid;
      grid-template-rows: 158px 1fr;
      min-height: 300px;
      border: 1px solid rgba(255,255,255,.13);
      border-radius: 8px;
      background: var(--panel-2);
      color: inherit;
      text-decoration: none;
      overflow: hidden;
      transition: border-color .16s ease, transform .16s ease, box-shadow .16s ease;
    }}
    .game-card:hover {{
      border-color: rgba(246,201,95,.78);
      transform: translateY(-4px);
      box-shadow: 0 18px 34px rgba(0,0,0,.42), 0 0 0 1px rgba(246,201,95,.12);
    }}
    .cover {{
      position: relative;
      display: block;
      overflow: hidden;
      border-bottom: 1px solid rgba(255,255,255,.12);
      isolation: isolate;
    }}
    .cover::before {{
      content: "";
      position: absolute;
      inset: 0;
      z-index: 0;
      background:
        linear-gradient(125deg, rgba(255,255,255,.18), transparent 34%),
        repeating-linear-gradient(90deg, rgba(255,255,255,.045) 0 1px, transparent 1px 18px);
      opacity: .72;
    }}
    .cover::after {{
      content: "";
      position: absolute;
      inset: auto 0 0;
      z-index: 1;
      height: 44px;
      background: linear-gradient(180deg, transparent, rgba(0,0,0,.32));
    }}
    .badge {{
      position: absolute;
      z-index: 4;
      left: 14px;
      top: 14px;
      min-width: 46px;
      height: 28px;
      padding: 0 9px;
      border: 1px solid rgba(255,255,255,.2);
      border-radius: 999px;
      background: rgba(0,0,0,.3);
      color: #fff4c7;
      font-size: 12px;
      font-weight: 900;
      line-height: 26px;
      text-align: center;
    }}
    .cover-gomoku {{
      background:
        linear-gradient(145deg, rgba(72,45,23,.95), rgba(186,123,43,.92)),
        #9a6b35;
    }}
    .gomoku-board {{
      position: absolute;
      left: 50%;
      top: 50%;
      z-index: 2;
      display: grid;
      grid-template-columns: repeat(9, 1fr);
      grid-template-rows: repeat(9, 1fr);
      width: min(78%, 320px);
      aspect-ratio: 1.62 / 1;
      padding: 12px 20px;
      border: 2px solid rgba(69,42,20,.78);
      border-radius: 8px;
      background:
        linear-gradient(rgba(58,35,16,.42) 1px, transparent 1px),
        linear-gradient(90deg, rgba(58,35,16,.42) 1px, transparent 1px),
        linear-gradient(135deg, #d49b53, #b87a34);
      background-size: 11.11% 12.5%, 12.5% 11.11%, auto;
      box-shadow: inset 0 0 0 1px rgba(255,255,255,.18), 0 18px 26px rgba(0,0,0,.24);
      transform: translate(-50%, -45%);
    }}
    .stone {{
      align-self: center;
      justify-self: center;
      width: clamp(11px, 2.2vw, 20px);
      height: clamp(11px, 2.2vw, 20px);
      border-radius: 50%;
      box-shadow: 0 4px 8px rgba(0,0,0,.35);
    }}
    .stone:nth-child(1) {{ grid-column: 3; grid-row: 3; }}
    .stone:nth-child(2) {{ grid-column: 4; grid-row: 3; }}
    .stone:nth-child(3) {{ grid-column: 5; grid-row: 4; }}
    .stone:nth-child(4) {{ grid-column: 5; grid-row: 5; }}
    .stone:nth-child(5) {{ grid-column: 6; grid-row: 5; }}
    .stone:nth-child(6) {{ grid-column: 7; grid-row: 5; }}
    .stone:nth-child(7) {{ grid-column: 4; grid-row: 6; }}
    .stone:nth-child(8) {{ grid-column: 5; grid-row: 6; }}
    .stone:nth-child(9) {{ grid-column: 6; grid-row: 7; }}
    .stone-black {{
      background: radial-gradient(circle at 35% 28%, #6b6f78, #0e1118 58%, #000);
    }}
    .stone-white {{
      background: radial-gradient(circle at 35% 28%, #fff, #d9d4c6 62%, #8d8778);
    }}
    .cover-star {{
      background:
        radial-gradient(circle at 70% 28%, rgba(105,170,255,.22), transparent 26%),
        linear-gradient(135deg, #081528, #17284c 48%, #311a59);
    }}
    .star {{
      position: absolute;
      z-index: 2;
      width: 3px;
      height: 3px;
      border-radius: 50%;
      background: #fff;
      box-shadow: 0 0 8px rgba(255,255,255,.85);
    }}
    .star-1 {{ left: 19%; top: 31%; }}
    .star-2 {{ left: 32%; top: 19%; }}
    .star-3 {{ left: 47%; top: 58%; }}
    .star-4 {{ left: 67%; top: 18%; }}
    .star-5 {{ left: 77%; top: 48%; }}
    .star-6 {{ left: 23%; top: 68%; }}
    .star-7 {{ left: 87%; top: 29%; }}
    .star-8 {{ left: 55%; top: 34%; }}
    .player-ship {{
      position: absolute;
      left: 14%;
      top: 52%;
      z-index: 3;
      width: 78px;
      height: 50px;
      transform: rotate(5deg);
      clip-path: polygon(0 50%, 72% 8%, 100% 50%, 72% 92%);
      background: linear-gradient(90deg, #57d6ff, #f1fbff 44%, #4667ff);
      box-shadow: 0 0 24px rgba(86,214,255,.45);
    }}
    .player-ship::before {{
      content: "";
      position: absolute;
      left: -18px;
      top: 18px;
      width: 34px;
      height: 14px;
      border-radius: 999px;
      background: linear-gradient(90deg, rgba(255,109,70,0), #ff8a4d);
    }}
    .enemy-ship {{
      position: absolute;
      right: 18%;
      top: 24%;
      z-index: 3;
      width: 60px;
      height: 42px;
      clip-path: polygon(50% 0, 100% 48%, 74% 100%, 26% 100%, 0 48%);
      background: linear-gradient(180deg, #ff7474, #752d56);
      box-shadow: 0 0 18px rgba(230,93,93,.5);
    }}
    .laser {{
      position: absolute;
      left: 36%;
      z-index: 2;
      height: 4px;
      border-radius: 999px;
      background: #66f0ff;
      box-shadow: 0 0 14px rgba(102,240,255,.95);
    }}
    .laser-a {{ top: 47%; width: 34%; }}
    .laser-b {{ top: 62%; width: 24%; }}
    .cover-match {{
      background:
        radial-gradient(circle at 78% 22%, rgba(246,201,95,.18), transparent 26%),
        linear-gradient(135deg, #27304f, #2b5c66 58%, #3d704c);
    }}
    .match-grid {{
      position: absolute;
      left: 50%;
      top: 50%;
      z-index: 2;
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 8px;
      width: min(74%, 300px);
      transform: translate(-50%, -44%);
    }}
    .match-tile {{
      display: grid;
      place-items: center;
      aspect-ratio: 1;
      border: 1px solid rgba(255,255,255,.22);
      border-radius: 8px;
      background: linear-gradient(180deg, rgba(255,255,255,.2), rgba(255,255,255,.07));
      color: #fff7ca;
      font-size: clamp(18px, 2.2vw, 27px);
      font-weight: 900;
      box-shadow: 0 10px 18px rgba(0,0,0,.22);
    }}
    .tile-1, .tile-4 {{ background-color: rgba(246,201,95,.23); }}
    .tile-2, .tile-5 {{ background-color: rgba(86,214,255,.18); }}
    .tile-3, .tile-7 {{ background-color: rgba(85,214,138,.18); }}
    .tile-6, .tile-8 {{ background-color: rgba(230,93,93,.17); }}
    .link-line {{
      position: absolute;
      left: 38%;
      top: 49%;
      z-index: 3;
      width: 28%;
      height: 3px;
      border-radius: 999px;
      background: #ffe57c;
      box-shadow: 0 0 14px rgba(255,229,124,.85);
      transform: rotate(-19deg);
    }}
    .cover-default {{
      background:
        linear-gradient(145deg, rgba(255,255,255,.16), transparent 34%),
        linear-gradient(135deg, #25395c, #7c3f3c);
    }}
    .default-screen {{
      position: absolute;
      left: 50%;
      top: 50%;
      z-index: 2;
      width: 76%;
      height: 42px;
      border: 1px solid rgba(255,255,255,.18);
      border-radius: 8px;
      background: rgba(0,0,0,.22);
      transform: translate(-50%, -45%);
    }}
    .card-body {{
      display: flex;
      flex-direction: column;
      min-width: 0;
      padding: 16px;
    }}
    .game-title {{
      min-height: 56px;
      overflow-wrap: anywhere;
      color: var(--text);
      font-size: 22px;
      font-weight: 900;
      line-height: 1.26;
    }}
    .game-file {{
      margin-top: 8px;
      overflow-wrap: anywhere;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.4;
    }}
    .play-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-top: auto;
      padding-top: 18px;
    }}
    .play-button {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 104px;
      height: 40px;
      padding: 0 14px;
      border: 1px solid rgba(255,255,255,.2);
      border-radius: 8px;
      background: linear-gradient(180deg, #ffd977, #c4862d);
      color: #261704;
      font-size: 14px;
      font-weight: 900;
      box-shadow: inset 0 1px 0 rgba(255,255,255,.45), 0 10px 20px rgba(0,0,0,.22);
    }}
    .status-dot {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      color: #bfffd8;
      font-size: 12px;
      white-space: nowrap;
    }}
    .status-dot::before {{
      content: "";
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: var(--green);
      box-shadow: 0 0 9px var(--green);
    }}
    .empty {{
      grid-column: 1 / -1;
      padding: 28px;
      border: 1px dashed rgba(255,255,255,.22);
      border-radius: 8px;
      background: rgba(255,255,255,.05);
      color: var(--muted);
      text-align: center;
    }}
    @media (max-width: 840px) {{
      .hero {{
        grid-template-columns: 1fr;
      }}
      .banner-title {{
        font-size: 34px;
      }}
    }}
    @media (max-width: 640px) {{
      .shell {{
        width: min(100% - 20px, 1180px);
        padding: 12px 0 28px;
      }}
      .topbar {{
        align-items: flex-start;
        flex-direction: column;
        padding: 14px;
        gap: 12px;
      }}
      .brand {{
        align-items: flex-start;
      }}
      .brand-mark {{
        width: 38px;
        height: 38px;
      }}
      h1 {{
        font-size: 22px;
      }}
      .server-pill {{
        width: 100%;
        justify-content: center;
      }}
      .banner {{
        min-height: 154px;
        padding: 18px;
      }}
      .banner-title {{
        font-size: 28px;
      }}
      .banner-meta {{
        margin-top: 16px;
      }}
      .meta-item {{
        min-height: 32px;
        font-size: 12px;
      }}
      .side-panel {{
        padding: 14px;
      }}
      .library-head {{
        align-items: flex-start;
        flex-direction: column;
        padding: 14px;
      }}
      .grid {{
        grid-template-columns: 1fr;
        padding: 12px;
      }}
      .game-card {{
        grid-template-rows: 154px 1fr;
        min-height: 288px;
      }}
      .card-body {{
        padding: 14px;
      }}
      .game-title {{
        min-height: auto;
        font-size: 21px;
      }}
      .play-row {{
        padding-top: 16px;
      }}
      .play-button {{
        min-width: 112px;
        height: 44px;
      }}
      .gomoku-board {{
        width: min(82%, 320px);
        padding: 10px 16px;
      }}
      .player-ship {{
        left: 12%;
        width: 68px;
        height: 44px;
      }}
      .enemy-ship {{
        right: 14%;
        width: 52px;
        height: 38px;
      }}
      .match-grid {{
        width: min(78%, 300px);
        gap: 7px;
      }}
    }}
    @media (max-width: 390px) {{
      .shell {{
        width: min(100% - 16px, 1180px);
      }}
      .banner-title {{
        font-size: 25px;
      }}
      .game-card {{
        grid-template-rows: 138px 1fr;
      }}
      .play-row {{
        align-items: stretch;
        flex-direction: column;
        gap: 10px;
      }}
      .play-button {{
        width: 100%;
      }}
      .status-dot {{
        justify-content: center;
      }}
    }}
  </style>
</head>
<body>
  <main class="shell">
    <nav class="topbar" aria-label="Game launcher">
      <div class="brand">
        <div class="brand-mark">GL</div>
        <div>
          <h1>{CN_TITLE}</h1>
          <p class="sub">{CN_SUBTITLE}</p>
        </div>
      </div>
      <div class="server-pill">{CN_SERVER} · {CN_STATUS_ONLINE}</div>
    </nav>

    <section class="hero">
      <div class="banner">
        <div class="banner-kicker">{CN_LOCAL} HTML</div>
        <div class="banner-title"><span>{CN_READY}</span> · {CN_LIBRARY}</div>
        <div class="banner-meta">
          <div class="meta-item">{CN_GAME_COUNT}<strong>{len(games)}</strong></div>
          <div class="meta-item">{CN_SERVER}<strong>127.0.0.1</strong></div>
        </div>
      </div>
      <aside class="side-panel">
        <h2 class="side-title">{CN_TIP_TITLE}</h2>
        <div class="stat-row"><span>{CN_GAME_COUNT}</span><strong>{len(games)}</strong></div>
        <div class="stat-row"><span>{CN_SERVER}</span><strong>{CN_STATUS_ONLINE}</strong></div>
        <div class="tip">{CN_TIP_COPY}</div>
      </aside>
    </section>

    <section class="library">
      <div class="library-head">
        <h2 class="library-title">{CN_LIBRARY}</h2>
        <div class="tab">{CN_ALL_GAMES}</div>
      </div>
      <div class="grid" aria-label="Game list">
        {cards}
      </div>
    </section>
  </main>
</body>
</html>
"""
    return page.encode("utf-8")


class GameLauncherHandler(SimpleHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path in {"/", "/index.html", "/index.htm"}:
            content = build_index_page()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        super().do_GET()

    def log_message(self, format: str, *args: object) -> None:
        sys.stdout.write("%s - %s\n" % (self.address_string(), format % args))


def pick_port(host: str, preferred_port: int) -> int:
    for port in range(preferred_port, preferred_port + 100):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                probe.bind((host, port))
            except OSError:
                continue
            return port
    raise RuntimeError(f"No available port found from {preferred_port} to {preferred_port + 99}.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Start a local HTML game launcher.")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind. Default: 127.0.0.1")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Port to bind. Default: {DEFAULT_PORT}")
    parser.add_argument("--no-browser", action="store_true", help="Start the server without opening a browser.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    port = pick_port(args.host, args.port)
    handler = partial(GameLauncherHandler, directory=str(BASE_DIR))
    server = ThreadingHTTPServer((args.host, port), handler)
    url = f"http://{args.host}:{port}/"

    games = find_html_games()
    print(f"Base directory: {BASE_DIR}")
    print(f"Game count: {len(games)}")
    for game in games:
        print(f" - {game.name}")
    print(f"URL: {url}")
    print("Press Ctrl+C to stop.")

    if not args.no_browser:
        webbrowser.open(url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
