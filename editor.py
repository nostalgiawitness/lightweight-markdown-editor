import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinterweb import HtmlFrame
import markdown2, os

DEF_HEIGHT = 600
DEF_WIDTH = 1300
DEF_DEBOUNCE = 300  # milliseconds

DEF_EDITOR_FONT = "Consolas"
DEF_EDITOR_FONTSIZE = 12
DEF_STARTING_TEXT = ""
if os.path.exists("README.md"):
    with open("README.md", "r", encoding="utf-8") as f:
        DEF_STARTING_TEXT = f.read()

EDITOR_INSERT = tk.INSERT


class Editor:
    def __init__(self):
        self.root = tk.Tk()
        self.window_height = DEF_HEIGHT
        self.window_width = DEF_WIDTH
        self.setupWindow()
        self.createWidgets()
        self.setupBindings()
    
    def setupWindow(self):
        self.root.title("Lightweight Markdown Editor")
        self.root.geometry(f"{self.window_width}x{self.window_height}")
        self.root.minsize(600, 400)
        style = ttk.Style()
        style.configure("TButton", font=(DEF_EDITOR_FONT, DEF_EDITOR_FONTSIZE, 'bold'))
    
    def createWidgets(self):
        # *** TOOLBAR ***
        self.toolbar = ttk.Frame(self.root, padding=5)
        self.toolbar.pack(fill=tk.X)

        # HEADERS
        for i in range(1, 6):
            btn = ttk.Button(self.toolbar, text=f"H{i}", width=3, command=lambda lvl=i: self.insertStart("#" * lvl + " "))
            btn.pack(side=tk.LEFT, padx=2)

        # FORMATTING
        ttk.Button(self.toolbar, text="B", width=3, command=lambda: self.insertAround("**")).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="I", width=3, command=lambda: self.insertAround("*")).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="U", width=3, command=lambda: self.insertAround("__")).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="S", width=3, command=lambda: self.insertAround("~~")).pack(side=tk.LEFT, padx=2)  # Strikethrough
        ttk.Button(self.toolbar, text="Code", width=5, command=lambda: self.insertAround("`")).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="BlockCode", width=9, command=lambda: self.insertBlockCode()).pack(side=tk.LEFT, padx=2)

        # LISTS
        ttk.Button(self.toolbar, text="UL", width=3, command=lambda: self.insertStart("- ")).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="OL", width=3, command=lambda: self.insertOrderedList()).pack(side=tk.LEFT, padx=2)

        # QUOTES / HR / TABLE
        ttk.Button(self.toolbar, text="Quote", width=6, command=lambda: self.insertStart("> ")).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="HR", width=3, command=lambda: self.insertStart("---\n")).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="Table", width=5, command=self.insertTable).pack(side=tk.LEFT, padx=2)

        # IMAGE
        img_frame = ttk.Frame(self.toolbar, border=1, relief=tk.SUNKEN, padding=2)
        img_frame.pack(side=tk.LEFT)
        self.text_IMG = tk.Text(img_frame, font=(DEF_EDITOR_FONT, 8), height=2, width=16)
        self.text_IMG.pack(side=tk.LEFT, padx=2)
        self.text_IMG.insert(tk.END, "https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png")
        ttk.Button(img_frame, text="IMG", width=5, command=lambda: self.insertImage(self.text_IMG.get("1.0", tk.END).strip())).pack(side=tk.LEFT, padx=2)

        # LINK
        link_frame = ttk.Frame(self.toolbar, border=1, relief=tk.SUNKEN, padding=2)
        link_frame.pack(side=tk.LEFT)
        self.text_LINK = tk.Text(link_frame, font=(DEF_EDITOR_FONT, 8), height=2, width=16)
        self.text_LINK.pack(side=tk.LEFT, padx=2)
        self.text_LINK.insert(tk.END, "https://example.com")
        ttk.Button(link_frame, text="Link", width=5, command=lambda: self.insertLink(self.text_LINK.get("1.0", tk.END).strip())).pack(side=tk.LEFT)

        #OPEN FILE
        ttk.Button(self.toolbar, text="Open", width=5, command=lambda: self.openFile()).pack(side=tk.RIGHT, padx=2)

        #SAVE FILE
        ttk.Button(self.toolbar, text="Save", width=5, command=lambda: self.saveToFile()).pack(side=tk.RIGHT, padx=2)

        #CLEAR with confirmation dialog button
        ttk.Button(self.toolbar, text="Clear", width=5, command= lambda: self.clearEditor()).pack(side=tk.RIGHT, padx=2)

        # *** WORKSPACE ***
        self.workspace = ttk.Panedwindow(self.root, orient=tk.HORIZONTAL)
        self.workspace.pack(fill=tk.BOTH, expand=True)

        # EDITOR
        self.editor_frame = ttk.Frame(self.workspace)
        editor_scroll = ttk.Scrollbar(self.editor_frame)
        editor_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.editor = tk.Text(
            self.editor_frame,
            wrap=tk.WORD,
            yscrollcommand=editor_scroll.set,
            font=(DEF_EDITOR_FONT, DEF_EDITOR_FONTSIZE),
            padx=5,
            pady=5,
            undo=True
        )
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        editor_scroll.config(command=self.editor.yview)
        self.editor.insert(tk.END, DEF_STARTING_TEXT)

        # PREVIEW
        self.preview_frame = ttk.Frame(self.workspace)
        self.preview = HtmlFrame(
            self.preview_frame,
            messages_enabled=False
        )
        self.preview.pack(fill=tk.BOTH, expand=True)

        self.workspace.add(self.editor_frame, weight=1)
        self.workspace.add(self.preview_frame, weight=1)

    
    def setupBindings(self):
        self.editor.bind('<KeyRelease>', self.scheduleUpdate)
        self.editor.bind('<Button-1>', self.scheduleUpdate)
        self.updatePreview()
        self.update_after_id = None
    
    def scheduleUpdate(self, event):
        if hasattr(self, "update_after_id") and self.update_after_id:
            self.root.after_cancel(self.update_after_id)
        self.update_after_id = self.root.after(DEF_DEBOUNCE, self.updatePreview)
    
    def updatePreview(self):
        markdown = self.editor.get("1.0", tk.END)
        html_text = self.convertMDHTML(markdown)
        
        try:
            self.preview.load_html(html_text)
        except Exception as e:
            self.preview.load_html(f"<p>ERR: {str(e)}</p>")
        self.update_after_id = None

    def convertMDHTML(self, text: str) -> str:
        html = markdown2.markdown(
            text,
            extras=[
                "fenced-code-blocks",
                "tables",
                "footnotes",
                "strike",
                "cuddled-lists",
                "code-friendly",
            ]
        )
        return html

    def insertStart(self, string:str):
        if not self.editor.tag_ranges(tk.SEL):
            line_start = self.editor.index(f"{EDITOR_INSERT} linestart")
            self.editor.insert(line_start, string)
        else: 
            sel_start = self.editor.index(tk.SEL_FIRST)
            sel_end = self.editor.index(tk.SEL_LAST)
            start_line = int(sel_start.split('.')[0])
            end_line = int(sel_end.split('.')[0])
            for line in range(start_line, end_line + 1):
                self.editor.insert(f"{line}.0", string)
        self.updatePreview()

    def insertAround(self, string:str):
        if not self.editor.tag_ranges(tk.SEL):
            line_start = self.editor.index(f"{EDITOR_INSERT} linestart")
            line_end = self.editor.index(f"{EDITOR_INSERT} lineend")
            self.editor.insert(line_end, string)
            self.editor.insert(line_start, string)
        else:
            sel_start = self.editor.index(tk.SEL_FIRST)
            sel_end = self.editor.index(tk.SEL_LAST)
            self.editor.insert(sel_end, string)
            self.editor.insert(sel_start, string)
        self.updatePreview()

    def insertBlockCode(self):
        if not self.editor.tag_ranges(tk.SEL):
            self.editor.insert(EDITOR_INSERT, "\n```\nYour code here\n```\n")
        else:
            sel_start = self.editor.index(tk.SEL_FIRST)
            sel_end = self.editor.index(tk.SEL_LAST)
            self.editor.insert(sel_end, "\n```\n")
            self.editor.insert(sel_start, "```\n")
        self.updatePreview()

    def insertOrderedList(self):
        if not self.editor.tag_ranges(tk.SEL):
            line_start = self.editor.index(f"{EDITOR_INSERT} linestart")
            self.editor.insert(line_start, "1. ")
        else:
            sel_start = self.editor.index(tk.SEL_FIRST)
            sel_end = self.editor.index(tk.SEL_LAST)
            start_line = int(sel_start.split('.')[0])
            end_line = int(sel_end.split('.')[0])
            num = 1
            for line in range(start_line, end_line + 1):
                self.editor.insert(f"{line}.0", f"{num}. ")
                num += 1
        self.updatePreview()

    def insertImage(self, url):
        self.editor.insert(EDITOR_INSERT, f"![Alt text]({url})")
        self.updatePreview()

    def insertTable(self):
        table_md = """\n| Column1 | Column2 |\n|---------|---------|\n| Data1   | Data2   |\n"""
        self.editor.insert(EDITOR_INSERT, table_md)
        self.updatePreview()

    def insertLink(self, link):
        if not self.editor.tag_ranges(tk.SEL):
            return
        sel_start = self.editor.index(tk.SEL_FIRST)
        sel_end = self.editor.index(tk.SEL_LAST)
        self.editor.insert(sel_end, f"]({link})")
        self.editor.insert(sel_start, "[")
        self.updatePreview()

    def saveToFile(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".md", filetypes=[("Markdown files", "*.md"), ("All files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.editor.get("1.0", tk.END))
            except Exception as e:
                from tkinter import messagebox
                messagebox.showerror("ERR", str(e))

    def openFile(self):
        file_path = filedialog.askopenfilename(filetypes=[("Markdown files", "*.md"), ("All files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.editor.delete("1.0", tk.END)
                self.editor.insert(tk.END, content)
                self.updatePreview()
            except Exception as e:
                from tkinter import messagebox
                messagebox.showerror("ERR", str(e))

    def clearEditor(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to clear the editor?"):
            self.editor.delete("1.0", tk.END)
            self.updatePreview()

    def run(self):
        self.root.mainloop()


def main():
    app = Editor()
    app.run()


if __name__ == "__main__":
    main()