from textual.app import App, ComposeResult,RenderResult
from textual.widgets import TextArea, MarkdownViewer, Footer, Header, Input
from textual.screen import ModalScreen
from textual.widget import Widget
from textual import on
import os



class PreviewScreen(ModalScreen):
    """Modal screen showing markdown content."""
    BINDINGS = [("escape", "escape_from_preview_screen", "Close preview")]

    def __init__(self, markdown_text: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.markdown_text = markdown_text  

    def compose(self) -> ComposeResult:
        yield Header()
        yield MarkdownViewer(self.markdown_text, open_links=False, show_table_of_contents=True)
        yield Footer()

    def on_mount(self) -> None:
        self.title = "📝 Preview Page"

    def action_escape_from_preview_screen(self) -> None:
        self.app.pop_screen()


class Greeting(Widget):
    """Display a greeting."""

    def __init__(self, file_path: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file_path=file_path

    def get_file_size(self,file_path):
        """Returns human-readable file size (e.g., '1.5 MB')"""
        size_bytes = os.path.getsize(self.file_path)
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
    

    def render(self) -> RenderResult:
        self.notify("File has been saved successfully!", severity="information",timeout=3)
        return f"""
File name: {self.file_path}
File size: {self.get_file_size(self.file_path)}

Press "q" to quiet the tool."""


class GoodbyeApp(ModalScreen):

    def __init__(self, file_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file_name=file_name

    CSS_PATH = "greeting.tcss"

    def compose(self) -> ComposeResult:
        yield Greeting(self.file_name)
        
    
    def on_key(self, event) -> None:
        if event.key == "q":
            self.app.exit(message="Goodbye! 👋")


class Help_page(ModalScreen):

    BINDINGS = [
        ("ctrl+b", "back", "Back"),
    ]


    def __init__(self, theme_text: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.theme_text=theme_text

    def compose(self) -> ComposeResult:
        help_text="""# 🚀 Markdown Editor Help

Welcome to the terminal-based Markdown editor! Edit your documents with the power of a TUI, right in your terminal.

---

## ⌨️ Keyboard Shortcuts

### 📝 Editing
| Shortcut | Description |
|----------|-------------|
| **Type normally** | Start writing Markdown immediately |
| **Tab / Shift+Tab** | Indent / Unindent selected lines |
| **Ctrl+Shift+C / Ctrl+Shift+V** | Copy and paste (system clipboard) |
| **Ctrl+Shift+Z / Ctrl+Shift+Y** | Undo / Redo changes |

### 🎮 Quick Actions
| Shortcut | Action | Details |
|----------|--------|---------|
| `Ctrl` + `s` | **Save File** | Opens save dialog to write to disk |
| `Ctrl` + `r` | **Toggle Preview** | Live preview of rendered Markdown |
| `Ctrl` + `t` | **Change Theme** | Switch between Tokyo Night and Solarized Light |
| `Ctrl` + `q` | **Quit** | Exit the application safely |
| `Ctrl` + `h` | **Show Help** | Open this help screen |

### 🖱️ Mouse Support
- **Click and drag** to select text
- **Scroll** to navigate long documents
- **Click UI buttons** for alternative control methods

---

## 💡 Pro Tips

1. **Live Preview**: Press `Ctrl+R` anytime to see how your Markdown renders - great for checking tables, code blocks, and formatting!

2. **Theme Preference**: Toggle `Ctrl+T` if you prefer light over dark (or vice versa) - perfect for different lighting conditions.

3. **Safe Saving**: The save dialog appears when you press `Ctrl+S`. Enter a filename with `.md` extension for best results.

4. **Quick Exit**: When viewing the save confirmation screen, press `Q` to return to your shell.

---


"""
        yield MarkdownViewer(help_text, open_links=False, show_table_of_contents=False)
        yield Footer()

    def action_back(self):
        self.app.theme=self.theme_text
        self.app.pop_screen()


class SaveFile(ModalScreen):  
    DEFAULT_CSS = """
    SaveFile {
        align: center middle;
    }
    
    #input {
        width: 50;
    }
    """

    BINDINGS = [
        ("ctrl+b", "back", "Back"),
    ]

    def __init__(self, markdown_text: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.markdown_text = markdown_text  

    def compose(self) -> ComposeResult:
        yield Input(placeholder="File name...",id="input")
        yield Footer()

    @on(Input.Submitted)
    def accept_file_name_save(self):
        input_widget = self.query_one(Input)
        file_name = input_widget.value.strip()
        
        if not file_name:
            self.notify("Please enter a valid file name!", severity="warning")
            input_widget.focus()
            return
        
        try:
            with open(file_name, "w") as file:
                file.write(self.markdown_text)
            self.app.push_screen(GoodbyeApp(file_name))
        except Exception as e:
            self.notify(f"Error saving file: {str(e)}", severity="error")

    def action_back(self):
        self.app.pop_screen()


class MarkdownEditorApp(App[None]):
    CSS = """
    Screen {
        align: center middle;
    }
    """
    
    ENABLE_COMMAND_PALETTE = False
    BINDINGS = [
        ("ctrl+q", "quit", "Quit"),
        ("ctrl+r", "show_preview", "See preview"),
        ("ctrl+s", "save", "Save the file"),
        ("ctrl+t", "changetheme", "Change theme"),
        ("ctrl+h", "showhelp", "Help"),
    ]

    def compose(self) -> ComposeResult:   
        yield Header()
        yield TextArea.code_editor(language="markdown")
        yield Footer()

    def on_mount(self) -> None:
        self.title = "📝 Markdown Editor"
        self.theme = "tokyo-night"

    def action_show_preview(self) -> None:
        text_area = self.query_one(TextArea)
        self.push_screen(PreviewScreen(text_area.text))

    def action_save(self) -> None:
        text_area = self.query_one(TextArea)
        self.push_screen(SaveFile(text_area.text))

    def action_changetheme(self) -> None:
        if self.theme == "tokyo-night":
            self.theme = "solarized-light"
        elif self.theme == "solarized-light":
            self.theme = "tokyo-night"

    def action_showhelp(self) -> None:
        current_theme=self.theme
        self.theme = "textual-dark"
        self.push_screen(Help_page(current_theme))



if __name__ == "__main__":    
    app = MarkdownEditorApp()
    app.run()