# IPE File Merger

This tool allows to merge serveral IPE files into one.
It is based on the work by Simon Fink (https://gitlab.infosun.fim.uni-passau.de/finksim/ipe-merger)

## Usage

```
merge-ipe-files.py OUT_FILE IN_FIES
```

Optional arguments
- ``--template`` IPE files whose template is used for the merged file, default: first file
- ``--symbol`` only merge pages containing the specified symbol