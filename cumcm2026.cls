\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{cumcm2026}[2026/08/30 v2.1 TEXPage-safe CUMCM 2026 electronic-paper class]

% Electronic submission class: the PDF starts directly with the abstract page.
\LoadClass[UTF8,a4paper,12pt,fontset=none]{ctexart}

\RequirePackage{fontspec}
\RequirePackage{geometry}
\RequirePackage{amsmath,amssymb,mathtools,bm}
\RequirePackage{booktabs,array,tabularx,longtable,multirow}
\RequirePackage{graphicx,float,caption,subcaption}
\RequirePackage{enumitem}
\RequirePackage{xcolor}
\RequirePackage{listings}
\RequirePackage{xeCJK-listings}
\RequirePackage{siunitx}
\RequirePackage{microtype}
\RequirePackage{titlesec}
\RequirePackage{fancyhdr}
\RequirePackage{hyperref}
\RequirePackage{cleveref}
\RequirePackage{xurl}
\RequirePackage{etoolbox}

% ---------- Page geometry: national 2026 minimum is 2.5 cm on every side ----------
\geometry{a4paper,left=2.5cm,right=2.5cm,top=2.5cm,bottom=2.5cm,headheight=14pt,footskip=1.2cm}

% ---------- Portable fonts (TeX Live only; stable on TEXPage) ----------
% Use font FILES shipped with TeX Live rather than OS/fontconfig family names.
% This avoids server-dependent fontspec lookup failures on online compilers.
\setmainfont{lmroman10-regular.otf}[
  BoldFont=lmroman10-bold.otf,
  ItalicFont=lmroman10-italic.otf,
  BoldItalicFont=lmroman10-bolditalic.otf
]
\setsansfont{lmsans10-regular.otf}[
  BoldFont=lmsans10-bold.otf,
  ItalicFont=lmsans10-oblique.otf,
  BoldItalicFont=lmsans10-boldoblique.otf
]
\setmonofont{lmmono10-regular.otf}[
  BoldFont=lmmonolt10-bold.otf,
  ItalicFont=lmmono10-italic.otf,
  BoldItalicFont=lmmonolt10-boldoblique.otf
]
\setCJKmainfont{FandolSong-Regular.otf}[BoldFont=FandolSong-Bold.otf]
\setCJKsansfont{FandolHei-Regular.otf}[BoldFont=FandolHei-Bold.otf]
\newCJKfontfamily\cumcmkai{FandolKai-Regular.otf}
\setCJKmonofont{FandolFang-Regular.otf}

% ---------- Body typography ----------
\AtBeginDocument{\zihao{-4}\setcounter{page}{1}}
\setlength{\parindent}{2em}
\setlength{\parskip}{0pt}
\linespread{1.25}
\setlength{\emergencystretch}{2em}
\allowdisplaybreaks[2]
\setlength{\abovedisplayskip}{8pt plus 2pt minus 2pt}
\setlength{\belowdisplayskip}{8pt plus 2pt minus 2pt}
\setlist{leftmargin=2em,labelsep=0.6em,itemsep=0.20em,topsep=0.35em,parsep=0pt}

% ---------- Page numbers ----------
\pagestyle{fancy}
\fancyhf{}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}
\fancypagestyle{plain}{\fancyhf{}\fancyfoot[C]{\thepage}\renewcommand{\headrulewidth}{0pt}\renewcommand{\footrulewidth}{0pt}}

% ---------- Headings ----------
\renewcommand{\thesection}{\chinese{section}}
\renewcommand{\thesubsection}{\arabic{section}.\arabic{subsection}}
\renewcommand{\thesubsubsection}{\arabic{section}.\arabic{subsection}.\arabic{subsubsection}}
\titleformat{\section}{\centering\sffamily\zihao{3}\bfseries}{\thesection、}{0.45em}{}
\titleformat{\subsection}{\sffamily\zihao{4}\bfseries}{\thesubsection}{0.65em}{}
\titleformat{\subsubsection}{\sffamily\zihao{-4}\bfseries}{\thesubsubsection}{0.65em}{}
\titlespacing{\section}{0pt}{1.15em}{0.70em}
\titlespacing{\subsection}{0pt}{0.90em}{0.42em}
\titlespacing{\subsubsection}{0pt}{0.70em}{0.35em}

% ---------- Title + abstract page ----------
\makeatletter
\renewcommand{\maketitle}{%
  \thispagestyle{plain}%
  \begin{center}
    {\sffamily\zihao{-2}\mdseries\@title\par}
  \end{center}
  \vspace{0.50em}%
}
\AtBeginDocument{\hypersetup{pdftitle={\@title},pdfauthor={},pdfsubject={2026 CUMCM参赛论文}}}
\makeatother

\renewenvironment{abstract}{%
  \begin{center}{\sffamily\zihao{3}\bfseries 摘\quad 要}\end{center}
  \vspace{-0.15em}\zihao{-4}%
}{%
  \par\clearpage
}
\newcommand{\keywords}[1]{\par\vspace{0.65em}\noindent{\sffamily\bfseries 关键词：}#1}

% ---------- Figures and tables ----------
\graphicspath{{figs/}}
\DeclareGraphicsExtensions{.pdf,.png,.jpg,.jpeg}
\captionsetup{font=small,labelsep=quad,skip=6pt}
\captionsetup[table]{position=top}
\renewcommand{\figurename}{图}
\renewcommand{\tablename}{表}
\renewcommand{\arraystretch}{1.25}
\newcolumntype{Y}{>{\centering\arraybackslash}X}
\newcolumntype{L}{>{\raggedright\arraybackslash}X}
\newcolumntype{R}{>{\raggedleft\arraybackslash}X}

% ---------- Hyperlinks and references ----------
\hypersetup{unicode=true,hidelinks,pdfauthor={},bookmarksnumbered=true,bookmarksopen=false}
\urlstyle{same}
\renewcommand{\refname}{参考文献}
% Excellent CUMCM papers commonly keep references as the final numbered body section.
\makeatletter
\patchcmd{\thebibliography}{\section*{\refname}}{\section{\refname}}{}{}
\makeatother
\crefname{figure}{图}{图}
\crefname{table}{表}{表}
\crefformat{equation}{#2式~(#1)#3}

% ---------- Exact 2026 AI declaration wording ----------
\newcommand{\CumcmAINotUsed}{%
  \section*{AI工具使用声明}
  本参赛队在竞赛过程中未使用任何AI工具。
}
\newcommand{\CumcmAIUsed}[1]{%
  \section*{AI工具使用声明}
  本参赛队在竞赛过程中使用了AI工具，主要用于#1，详细使用情况见支撑材料。
}

% ---------- Support-file list ----------
\newcommand{\SupportFile}[2]{\item \nolinkurl{#1}：#2}

% ---------- Appendix ----------
\newcommand{\CumcmAppendix}{%
  \clearpage
  \phantomsection\label{cumcm:appendix-start}%
  \appendix
  \renewcommand{\thesection}{\Alph{section}}
  \renewcommand{\thesubsection}{\Alph{section}.\arabic{subsection}}
  \renewcommand{\thesubsubsection}{\Alph{section}.\arabic{subsection}.\arabic{subsubsection}}
  \titleformat{\section}{\centering\sffamily\zihao{3}\bfseries}{附录\thesection}{0.65em}{}
}

% ---------- Long code listings ----------
\definecolor{codegray}{HTML}{555555}
\lstdefinestyle{cumcmappendixcode}{
  basicstyle=\ttfamily\fontsize{8.2pt}{9.8pt}\selectfont,
  numbers=left,
  numberstyle=\fontsize{6.8pt}{8pt}\selectfont\color{codegray},
  stepnumber=1,
  numbersep=8pt,
  frame=single,
  rulecolor=\color{black!25},
  backgroundcolor=\color{white},
  keywordstyle=\bfseries,
  commentstyle=\color{codegray},
  stringstyle=\color{black},
  breaklines=true,
  breakatwhitespace=false,
  showstringspaces=false,
  columns=fullflexible,
  keepspaces=true,
  xleftmargin=2.2em,
  framexleftmargin=1.6em,
  aboveskip=0.65em,
  belowskip=0.85em,
  captionpos=t
}
\renewcommand{\lstlistingname}{代码}
\lstset{style=cumcmappendixcode}
\sisetup{detect-all,group-minimum-digits=4}

\endinput
