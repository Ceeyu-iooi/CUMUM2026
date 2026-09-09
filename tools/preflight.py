#!/usr/bin/env python3
"""CUMCM 2026 submission preflight.

Checks national-format constraints that can be verified mechanically. It is
conservative on purpose: a failed check should be fixed before submission.
Use --template only when testing the distributed example template; placeholder
text is then downgraded from ERROR to WARNING.
"""
from __future__ import annotations

import argparse
import ast
import io
import re
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.tex"
PDF = ROOT / "main.pdf"
AUX = ROOT / "main.aux"
LOG = ROOT / "main.log"
SUPPORT = ROOT / "support"
LIMIT = 20 * 1024 * 1024
SOURCE_EXTS = {".py", ".m", ".r", ".R", ".c", ".cc", ".cpp", ".cxx", ".h", ".hpp", ".java", ".jl", ".sps", ".do", ".sas", ".sql", ".bas", ".vba"}
TEXT_EXTS = SOURCE_EXTS | {".txt", ".md", ".csv", ".tex", ".json", ".yaml", ".yml"}


def strip_tex_comments(text: str) -> str:
    out = []
    for line in text.splitlines():
        cut = len(line)
        i = 0
        while i < len(line):
            if line[i] == "%":
                bs = 0
                j = i - 1
                while j >= 0 and line[j] == "\\":
                    bs += 1
                    j -= 1
                if bs % 2 == 0:
                    cut = i
                    break
            i += 1
        out.append(line[:cut])
    return "\n".join(out)


def support_files(active_tex: str) -> list[str]:
    return re.findall(r"\\SupportFile\s*\{([^{}]+)\}\s*\{", active_tex)


def listing_files(active_tex: str) -> list[str]:
    # Accept optional [..] argument and require paths below support/.
    found = re.findall(r"\\lstinputlisting(?:\[[^\]]*\])?\s*\{support/([^{}]+)\}", active_tex)
    return [p.strip() for p in found]


def label_page(aux_text: str, label: str) -> int | None:
    # Hyperref form: \newlabel{name}{{currentlabel}{PAGE}{...}{...}{...}}
    m = re.search(r"\\newlabel\{" + re.escape(label) + r"\}\{\{[^}]*\}\{(\d+)\}", aux_text)
    return int(m.group(1)) if m else None


def pdfinfo(path: Path) -> dict[str, str]:
    try:
        p = subprocess.run(["pdfinfo", str(path)], capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return {}
    result: dict[str, str] = {}
    for line in p.stdout.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            result[k.strip()] = v.strip()
    return result


def pdftotext(path: Path) -> str:
    try:
        p = subprocess.run(["pdftotext", str(path), "-"], capture_output=True, text=True, check=True)
        return p.stdout
    except (OSError, subprocess.CalledProcessError):
        return ""


def estimate_zip_size(paths: list[Path]) -> int:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for p in paths:
            zf.write(p, p.relative_to(SUPPORT).as_posix())
    return len(buf.getvalue())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--template", action="store_true", help="treat template placeholders as warnings")
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []

    if not MAIN.exists():
        print("ERROR: main.tex not found")
        return 2

    raw = MAIN.read_text(encoding="utf-8")
    active = strip_tex_comments(raw)

    # 1) Structure/order checks.
    if re.search(r"\\tableofcontents\b", active):
        errors.append("正文中启用了 \\tableofcontents；2026 全国规范要求正文不要目录。")

    ai_positions = [m.start() for m in re.finditer(r"\\CumcmAI(?:Used|NotUsed)\b", active)]
    # References section: manual thebibliography OR BibTeX driven by \bibliographystyle/\bibliography.
    bib_match = re.search(r"(?:\\begin\{thebibliography\}|\\(?:bibliographystyle|bibliography)\b)", active)
    app_match = re.search(r"\\CumcmAppendix\b", active)
    if bib_match and ai_positions and ai_positions[0] > bib_match.start():
        errors.append("AI 工具使用声明必须位于参考文献之前。")
    if app_match and bib_match and bib_match.start() > app_match.start():
        errors.append("参考文献应位于正文末尾、附录之前。")

    # 2) Placeholders must be gone in the real submission.
    placeholders = sorted(set(re.findall(r"【[^】\n]{1,180}】", active)))
    if placeholders:
        target = warnings if args.template else errors
        target.append(f"仍有 {len(placeholders)} 类【占位内容】未替换/删除。")

    # 3) AI declaration must be exactly one of the template macros.
    used = len(re.findall(r"\\CumcmAIUsed\s*\{", active))
    not_used = len(re.findall(r"\\CumcmAINotUsed\b", active))
    if used + not_used != 1:
        errors.append("AI 工具使用声明必须二选一，且只能启用一条。")

    listed = support_files(active)
    if len(listed) != len(set(listed)):
        errors.append("附录支撑材料文件列表存在重复路径。")
    if not listed:
        errors.append("附录没有列出任何支撑材料文件。")

    ai_listed = "AI工具使用详情.pdf" in listed
    ai_pdf = SUPPORT / "AI工具使用详情.pdf"
    if used == 1:
        if not ai_listed:
            errors.append("声明使用了 AI，但附录文件列表没有 AI工具使用详情.pdf。")
        if not ai_pdf.exists():
            errors.append("声明使用了 AI，但 support/AI工具使用详情.pdf 不存在。")
        elif "【" in pdftotext(ai_pdf) or "】" in pdftotext(ai_pdf):
            errors.append("AI工具使用详情.pdf 中仍含【占位内容】，请据实填写后重新编译。")
    if not_used == 1:
        if ai_listed:
            errors.append("声明未使用 AI，但附录仍列出了 AI工具使用详情.pdf。")
        if ai_pdf.exists():
            warnings.append("声明未使用 AI，但 support/ 中存在 AI工具使用详情.pdf；不要把它提交。")

    # 4) Support list must be an exact file list, not directory names.
    actual_paths: list[Path] = []
    for rel in listed:
        p = SUPPORT / rel
        if not p.exists():
            errors.append(f"支撑材料列表中的文件不存在：{rel}")
        elif p.is_dir():
            errors.append(f"支撑材料列表写成了目录而不是实际文件：{rel}")
        else:
            actual_paths.append(p)

    junk = [p for p in SUPPORT.rglob("*") if p.is_file() and (p.suffix == ".pyc" or "__pycache__" in p.parts or p.name in {".DS_Store", "Thumbs.db"})]
    if junk:
        errors.append("support/ 中存在缓存/系统垃圾文件（如 __pycache__、.pyc、.DS_Store），应删除。")

    # 5) Every source file in support/code must be both listed and typeset in the appendix.
    listings = listing_files(active)
    listed_set = set(listed)
    listing_set = set(listings)
    code_files = {
        p.relative_to(SUPPORT).as_posix()
        for p in (SUPPORT / "code").rglob("*")
        if p.is_file() and p.suffix in SOURCE_EXTS
    } if (SUPPORT / "code").exists() else set()
    missing_from_list = sorted(code_files - listed_set)
    missing_from_appendix = sorted(code_files - listing_set)
    listing_not_listed = sorted(listing_set - listed_set)
    if missing_from_list:
        errors.append("support/code 中有源文件未列入支撑材料文件列表：" + ", ".join(missing_from_list))
    if missing_from_appendix:
        errors.append("support/code 中有源文件未完整排入论文附录：" + ", ".join(missing_from_appendix))
    if listing_not_listed:
        errors.append("论文附录排入了源文件，但支撑材料列表未列出：" + ", ".join(listing_not_listed))

    # Detect real files in data/result that were forgotten in the file list.
    ignored_names = {"README.md", ".gitkeep"}
    for folder in (SUPPORT / "data", SUPPORT / "result"):
        if folder.exists():
            for p in folder.rglob("*"):
                if p.is_file() and p.name not in ignored_names:
                    rel = p.relative_to(SUPPORT).as_posix()
                    if rel not in listed_set:
                        warnings.append(f"{rel} 存在但未列入附录支撑材料文件列表；若实际用于论文，应列入并提交。")

    # 6) Python syntax check without producing .pyc files.
    for p in actual_paths:
        if p.suffix.lower() == ".py":
            try:
                ast.parse(p.read_text(encoding="utf-8"), filename=str(p))
            except Exception as exc:
                errors.append(f"Python 源文件无法通过语法检查：{p.relative_to(ROOT)} ({exc})")

    # 7) Abstract page / 30-page body limit, if compiled auxiliary data exist.
    if AUX.exists():
        aux = AUX.read_text(encoding="utf-8", errors="replace")
        body_start = label_page(aux, "cumcm:body-start")
        appendix_start = label_page(aux, "cumcm:appendix-start")
        if body_start is None:
            warnings.append("无法从 main.aux 读取正文起始页标签；请重新编译两遍。")
        elif body_start != 2:
            errors.append(f"正文从 PDF 第 {body_start} 页开始；为稳妥满足‘摘要原则上不超过一页’，请把摘要控制在第 1 页。")
        else:
            print("[OK] 摘要页：1 页，正文从第 2 页开始")
        if appendix_start is None:
            warnings.append("无法从 main.aux 读取附录起始页标签；请重新编译两遍。")
        else:
            body_pages = appendix_start - 2  # pages 2 ... appendix_start-1
            if body_pages > 30:
                errors.append(f"正文（含 AI 声明和参考文献）共 {body_pages} 页，超过 30 页上限。")
            else:
                print(f"[OK] 正文页数：{body_pages}/30（摘要页与附录不计入此数）")
    else:
        warnings.append("main.aux 不存在，无法检查摘要页数和正文 30 页限制；请先编译。")

    # 8) PDF checks.
    if PDF.exists():
        size = PDF.stat().st_size
        if size > LIMIT:
            errors.append(f"main.pdf 大小 {size/1024/1024:.2f} MB，超过 20 MB。")
        else:
            print(f"[OK] main.pdf：{size/1024/1024:.2f} MB / 20 MB")
        info = pdfinfo(PDF)
        author = info.get("Author", "").strip()
        if author:
            errors.append(f"PDF Author 元数据非空：{author!r}。电子版不应暴露参赛者身份。")
        page_size = info.get("Page size", "")
        if page_size and "A4" not in page_size:
            errors.append(f"PDF 页面尺寸不是 A4：{page_size}")
        pdf_ver = info.get("PDF version", "")
        if pdf_ver:
            print(f"[OK] PDF version: {pdf_ver}")
    else:
        errors.append("main.pdf 不存在；请先编译正式论文。")

    # 9) LaTeX log: undefined refs/citations and overfull boxes.
    if LOG.exists():
        log = LOG.read_text(encoding="utf-8", errors="replace")
        if re.search(r"undefined references|Citation .* undefined|Reference .* undefined", log, re.I):
            errors.append("LaTeX 日志中存在未定义的引用/参考文献。")
        overfull = len(re.findall(r"Overfull \\hbox", log))
        if overfull:
            warnings.append(f"LaTeX 日志中有 {overfull} 处 Overfull \\hbox，请逐处检查是否越界。")

    # 10) Estimated support archive size.
    if actual_paths:
        est = estimate_zip_size(actual_paths)
        if est > LIMIT:
            errors.append(f"按当前文件列表估算压缩后约 {est/1024/1024:.2f} MB，超过 20 MB。")
        else:
            print(f"[OK] 支撑材料压缩体积估算：{est/1024/1024:.2f} MB / 20 MB")

    # 11) Identity-leak heuristics. Warnings only because problem context may contain these words.
    identity_words = re.compile(r"(姓名|学号|参赛队号|报名号|指导教师|所在学校|所在学院|赛区)" )
    email = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)
    phone = re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")
    home_path = re.compile(r"(?:[A-Za-z]:\\Users\\[^\\\s]+|/Users/[^/\s]+|/home/[^/\s]+)")
    if identity_words.search(active) or email.search(active) or phone.search(active) or home_path.search(active):
        warnings.append("main.tex 中检测到可能的身份信息字段/邮箱/手机号，请人工确认论文未暴露参赛者身份。")
    if "致谢" in active:
        warnings.append("检测到“致谢”；数学建模竞赛论文通常无需致谢，请确认其中没有身份或指导信息。")

    for p in actual_paths:
        rel = p.relative_to(SUPPORT).as_posix()
        if identity_words.search(rel):
            warnings.append(f"支撑材料文件名可能含身份字段，请人工核对：{rel}")
        if p.suffix in TEXT_EXTS:
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if email.search(text) or phone.search(text) or home_path.search(text):
                warnings.append(f"支撑材料中检测到邮箱/手机号/用户主目录路径样式，请确认不是参赛者身份信息：{rel}")

        # Check common PDF/Office author metadata in submitted support files.
        if p.suffix.lower() == ".pdf":
            info = pdfinfo(p)
            if info.get("Author", "").strip():
                errors.append(f"支撑材料 PDF Author 元数据非空：{rel} -> {info.get('Author')!r}")
        if p.suffix.lower() in {".docx", ".xlsx", ".pptx"}:
            try:
                with zipfile.ZipFile(p) as zf:
                    core = zf.read("docProps/core.xml").decode("utf-8", errors="ignore") if "docProps/core.xml" in zf.namelist() else ""
                for tag in ("dc:creator", "cp:lastModifiedBy"):
                    m = re.search(rf"<{tag}[^>]*>(.*?)</{tag}>", core, re.S)
                    if m and m.group(1).strip():
                        errors.append(f"支撑材料 Office 文档属性含作者信息：{rel} ({tag}={m.group(1).strip()!r})")
            except (OSError, zipfile.BadZipFile):
                warnings.append(f"无法检查 Office 文档元数据：{rel}")

    if warnings:
        print("\nWARNINGS:")
        for w in warnings:
            print(" -", w)
    if errors:
        print("\nERRORS:")
        for e in errors:
            print(" -", e)
        print("\nPreflight: FAILED")
        return 1

    print("\nPreflight: PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
