# CUMCM 2026 LaTeX 模板（全国赛电子版 / 终审核查版）
## TEXPage 编译设置（重要）

在 TEXPage 顶部 **设置** 中选择：

- 主文件：`main.tex`
- 编译器：**XeLaTeX**
- TeX Live：优先选择平台提供的较新稳定版本

本模板的中文字体固定使用 TeX Live 自带的 Fandol，西文字体固定使用 TeX Live 自带的 Latin Modern 字体文件，不依赖服务器操作系统安装的字体。**不要使用 pdfLaTeX**，因为模板包含 `fontspec` / `xeCJK` / `xeCJK-listings`。

如果从旧版本项目覆盖升级，修改编译器后请在 TEXPage 点击一次“清空编译缓存”再重新编译。


这是一个**以 2026 年全国大学生数学建模竞赛全国格式规范为基线**的电子版论文模板。设计思路类似期刊 LaTeX 模板：正文主要改 `main.tex`，版式集中在 `cumcm2026.cls`，图片统一放 `figs/`，支撑材料统一在 `support/` 工作目录管理。

> 注意：全国规范允许各赛区增加要求。正式提交前仍需核对本赛区/学校当年的补充通知。

## 目录

```text
main.tex                 # 主要写作文件：完整示例论文直接在这里
cumcm2026.cls            # 全国赛电子版基础版式，通常不要改
commons/preamble.tex     # 自定义宏/额外宏包
figs/                    # 所有论文图片
support/
  code/                  # 全部实际使用的完整源程序
  data/                  # 自行查阅并实际使用的数据（题目原始附件不重复放）
  result/                # 必要的大型中间结果/图表/结果文件
  requirements.txt       # Python 依赖示例
  environment.txt        # 运行环境与运行方式
  AI工具使用详情.tex      # 仅实际使用 AI 时填写并编译
  README.md              # 工作目录说明，不提交
support/AI工具使用详情.pdf # 仅实际使用 AI 时生成，并作为支撑材料提交
tools/preflight.py       # 提交前自动检查
 tools/stage_submission.py # 按论文附录文件列表整理真正要提交的文件
docs/                    # 官方规范备查，不提交
```

## 最推荐的比赛工作流

1. **只把 `main.tex` 当正文写作入口。** 把里面的【示例/占位内容】逐步替换掉。
2. 图片全部放 `figs/`，正文直接 `\includegraphics{文件名}`。
3. 全部实际使用的代码放 `support/code/`，并在论文附录用 `\lstinputlisting` **逐个完整排入 PDF**。
4. 自行查阅并实际使用的数据放 `support/data/`；题面附件原始数据不需要重复提交。
5. 必要的大型中间结果放 `support/result/`。论文附录 `\SupportFile{...}{...}` 必须列出**最终支撑材料压缩包中实际存在的每个文件**。
6. 若实际使用 AI：把 `\CumcmAINotUsed` 改成 `\CumcmAIUsed{...}`，填写 `support/AI工具使用详情.tex`，然后在 `support/` 目录中编译：

   ```bash
   cd support
   latexmk AI工具使用详情.tex
   cd ..
   ```

   这样会固定生成 `support/AI工具使用详情.pdf`；最后取消附录对应 `\SupportFile` 的注释。
7. 用 XeLaTeX/latexmk 编译：

   ```bash
   latexmk main.tex
   ```

8. 正式提交前运行严格检查：

   ```bash
   python tools/preflight.py
   ```

9. 检查通过后整理提交文件：

   ```bash
   python tools/stage_submission.py
   ```

   `submission/参赛论文.pdf` 是电子版论文；再用 **WinRAR** 把 `submission/support_materials/` **内部的全部内容**压缩为一个 ZIP 或 RAR。论文和支撑材料压缩包分别确认不超过 20MB。

## 纸质版与电子版不要混用

这个 class **只生成电子版论文**，因此第一页直接是摘要页，不包含承诺书和编号页。纸质版如需承诺书/编号专用页，应使用当年组委会/赛区提供的正式专用页放在打印稿最前面；不要用模板自己仿制一套。

## 正式提交前必须删除的模板痕迹

- 所有 `【...】` 示例/占位内容；
- 示例图 `figs/example_result.pdf` 及其正文引用；
- 示例参考文献，换成实际引用；
- 示例程序和示例结果，换成实际项目文件；
- `support/README.md`、`support/AI工具使用详情.tex`、`docs/`、`tools/` 等工作文件**都不要手工塞进支撑材料压缩包**。

推荐始终通过 `stage_submission.py` 暂存最终提交文件，避免把缓存、旧 PDF、README 或 `.tex` 模板误交上去。

## 兼容 Notebook / Excel / SPSS 等工具

- Jupyter：建议把最终 Notebook 导出为完整 `.py`，把 `.py` 放入 `support/code/` 并完整排入附录；`.ipynb` 如确有复现价值可另作为支撑材料列出。
- Excel 宏/VBA：导出 `.bas`/`.vba` 或把完整命令代码作为源程序保存并排入附录。
- SPSS / Stata / SAS：保存完整 `.sps` / `.do` / `.sas` 语法文件并排入附录。

`stage_submission.py` 生成的 `参赛论文.pdf` 只是便于整理的临时文件名；**如果当年竞赛提交系统/赛区要求特定命名，以系统要求为准。**