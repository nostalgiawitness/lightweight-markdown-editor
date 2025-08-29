# lightweight-markdown-editor

*A feather-lightweight tool to edit **markdown** code with visual feedback.*

## Features
- *Italic text*
- **Bold text**
- ~~Strikethrough~~
- [Links](https://example.com)
- `Inline code`

Even images!
![Alt text](https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png)

### Lists
1. Ordered item
2. Ordered item
- Unordered item

> Blockquote

| Table | Example |
|-------|----------|
| Cell1 | Cell2    |

## Quick start
***

### Requirements
```
tkinter (bundled with python3)
tkinterweb
markdown2
```

### Installation

```
git clone https://github.com/nostalgiawitness/lightweight-markdown-editor.git
pip install -r "requirements.txt"
python editor.py
```

### Building
*(REQUIRES `pyinstaller`)*
```
pyinstaller --onefile --noconsole --icon=icon.ico editor.py
```


---

Happy writing!


