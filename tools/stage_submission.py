#!/usr/bin/env python3
"""Stage exactly the files intended for CUMCM electronic submission.

The script deliberately does NOT create the final support ZIP/RAR. The 2026
national specification asks teams to use WinRAR. After staging, compress the
CONTENTS of submission/support_materials/ with WinRAR and check <= 20 MB.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUPPORT = ROOT / "support"
SUB = ROOT / "submission"


def strip_comments(text: str) -> str:
    out = []
    for line in text.splitlines():
        cut = len(line)
        for i, ch in enumerate(line):
            if ch == "%":
                bs = 0
                j = i - 1
                while j >= 0 and line[j] == "\\":
                    bs += 1
                    j -= 1
                if bs % 2 == 0:
                    cut = i
                    break
        out.append(line[:cut])
    return "\n".join(out)


def main() -> int:
    check = subprocess.run([sys.executable, str(ROOT / "tools" / "preflight.py")])
    if check.returncode != 0:
        print("\n未生成 submission/：请先修复 preflight 报错。")
        return check.returncode

    active = strip_comments((ROOT / "main.tex").read_text(encoding="utf-8"))
    listed = re.findall(r"\\SupportFile\s*\{([^{}]+)\}\s*\{", active)

    if SUB.exists():
        shutil.rmtree(SUB)
    (SUB / "support_materials").mkdir(parents=True)
    shutil.copy2(ROOT / "main.pdf", SUB / "参赛论文.pdf")

    for rel in listed:
        src = SUPPORT / rel
        dst = SUB / "support_materials" / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    (SUB / "README.txt").write_text(
        "【最终提交前人工核对】\n"
        "1. 参赛论文.pdf 直接作为电子版论文提交，不要压缩。\n"
        "2. 用 WinRAR 将 support_materials 文件夹内部的全部内容压缩成一个 ZIP 或 RAR；不要把外层 support_materials 目录一起套进去。\n"
        "3. 论文文件和支撑材料压缩包分别确认不超过 20MB。\n"
        "4. 文件名、文件夹名、PDF/Office 文档属性、源码注释中均不得出现参赛者姓名、学校、赛区等身份信息。\n"
        "5. 支撑材料压缩包中的路径和论文附录‘支撑材料文件列表’必须逐项一致。\n",
        encoding="utf-8",
    )
    print(f"已生成提交暂存目录：{SUB}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
