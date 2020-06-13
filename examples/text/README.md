# Summary of text

The example LaTeX project in this example is readapted from
https://www.overleaf.com/latex/templates/an-example-geophysics-report/jvmtcvsxwhmm.

Two main modifications to the original template have been made:
- Sections have been divided into files and grouped under the directory `geophysics_report/sections`, both for code readability and to show this feature of the summarizer (can look at multiple files).
- The new environment `summaryenv` has been defined and some pieces of text have been surrounded by the corresponding `\begin{} - \end{}` lines.

## Generate summary

From the main directory type the following command on a shell

```
python summarize.py -o ./examples/text/summarized/summary.tex ./examples/text/geophysics_report/main.tex summaryenv
```

It will create the file `summary.tex` containing all the snippets from the `geophysics_report` that are inside a `summaryenv` environment.