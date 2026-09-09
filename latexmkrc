# CUMCM 2026 template build: XeLaTeX -> XDV -> PDF 1.4
$pdf_mode = 5;
$xelatex = 'xelatex -file-line-error -halt-on-error -interaction=nonstopmode %O %S';
$xdvipdfmx = 'xdvipdfmx -V 4 -E -o %D %O %S';
$clean_ext = 'synctex.gz acn acr alg aux bbl bcf blg brf fdb_latexmk fls glsdefs glg glo gls idx ilg ind ist lof log lot out run.xml toc xdv';
