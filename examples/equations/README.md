# Summary of text

The example LaTeX project in this example is readapted from
https://www.overleaf.com/latex/templates/an-example-geophysics-report/jvmtcvsxwhmm.

One main modification to the original template has been made:
- Sections have been divided into files and grouped under the directory `geophysics_report/sections`, both for code readability and to show this feature of the summarizer (can look at multiple files).

## Generate summary

From the main directory type the following command on a shell

```
python summarize.py -o ./examples/equations/summarized/summary.tex ./examples/equations/geophysics_report/main.tex equation
```

It will create the file `summary.tex` containing all the snippets from the `geophysics_report` that are inside a `equation` environment.