# 支撑材料工作目录（不要直接把整个目录压缩提交）

正式提交的支撑材料至少应包含：

- 建模所用全部可运行源程序；
- 自行查阅并实际使用的数据资料（赛题原始数据除外）；
- 较大篇幅的中间结果图表等必要材料；
- 如竞赛期间使用 AI：`AI工具使用详情.pdf`。

**不要直接把整个 `support/` 文件夹压缩提交。** 这个工作目录还包含模板说明、AI 详情 `.tex` 等不应提交的文件。

论文附录中的 `\SupportFile{...}{...}` 是最终支撑材料文件列表。运行：

```bash
python tools/preflight.py
python tools/stage_submission.py
```

会检查并把“真正要提交的文件”复制到 `submission/support_materials/`。最后请按官方要求用 WinRAR 将该目录中的内容压缩为 ZIP 或 RAR，并确认压缩包不超过 20MB。

补充：若使用 Jupyter Notebook，建议保留 `.ipynb` 作为支撑材料（如确有必要），同时**导出对应完整 `.py` 源程序**放入 `code/` 并排入论文附录；若使用 Excel 宏、SPSS/Stata/SAS 等命令脚本，也应导出相应 VBA/语法文件或完整命令并排入附录。


若使用 AI，请在本目录执行：

```bash
latexmk AI工具使用详情.tex
```

不要从项目根目录用 `latexmk support/AI工具使用详情.tex`，否则部分 latexmk 配置会把 PDF 输出到根目录。
