# Minify Django .po Files

Removes all unnecessary lines from [.po files](https://www.gnu.org/software/gettext/manual/html_node/PO-Files.html).

### Usage
`$ python minify_po_files.py [-h] [-p] [-e ENCODING] path`
###### positional arguments:
```
  path                  path of Django locale directory
```
###### optional arguments:
```
  -h, --help            show this help message and exit
  -p, --print           print percentage translated for readme.md
  -e ENCODING, --encoding ENCODING
                        encoding, default='utf8'
```
