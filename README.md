# FluxDev ⚡ — Where ideas flow into code.

A premium, modern, and minimal web code editor inspired by the design language of **Linear**, **Arc Browser**, and **Raycast**, built with **PyQt6**, **QScintilla**, and **QtWebEngine**.

---

## 🎨 Design Language & Core Layout

* **Architectural Shell**: Custom frameless title bar with macOS/Arc-style minimal dot controls (Close `#EF4444`, Minimize `#F59E0B`, Maximize `#10B981`), full window dragging, rounded corners, and a subtle drop shadow (`QGraphicsDropShadowEffect`).
* **Deep Dark Palette**: Near-black navy workspace (`#0B0D14`), elevated surfaces (`#121626` / `#161B30`), and borders at $6-8\%$ white opacity (`rgba(255, 255, 255, 0.08)`).
* **Signature Violet-to-Cyan Accent Gradient**: Applied sparingly for the active tab underline, primary action buttons, focus rings, and the FluxDev flow mark.
* **Streamlined 3-Pane Splitter Layout**:
  * **Sidebar**: Fixed around 220px, collapsible with smooth animation. Displays an intuitive empty state when no folder is open, and dynamically displays the folder name when opened.
  * **Editor Area**: Generous stretch factor 3 with a minimum width of 400px.
  * **Live Preview**: Stretch factor 2, **hidden by default**. Toggled instantly via the title bar button, `F6`, or `Ctrl+P`. When shown, automatically proportions the workspace ~55/45 between editor and preview.
* **1px Splitter Handles**: Crisp 1px splitter divider lines that highlight with the violet accent on hover.
* **Comfortable Code Surface**: Font size 14, 1.5 line height, 12px left padding in the gutter, visible current-line highlight, and thin indent guides.
* **Theme-Matching Preview**: The Live Preview toolbar is a slim fixed-height bar of 38px. When empty, it displays a dark theme-matching placeholder with *"Open an HTML file to preview"*.
* **Pill-Shaped Tabs**: Modern pill tabs with hover-revealed close buttons, modified dot indicators (`•`), and a gradient underline on the active tab. New untitled tabs automatically open with a short HTML5 boilerplate.
* **Command Palette (`Ctrl+Shift+P` / `Ctrl+K`)**: Floating Raycast-style spotlight search box to trigger any action instantly.
* **Zero QSS Warnings**: Strict Qt-compliant stylesheet ([`editor/style.qss`](editor/style.qss)) with all non-Qt CSS properties removed.

---

## 🎭 Three Custom Themes

1. **FluxDev Dark** *(Default)*: Deep navy background (`#0B0D14`), violet/cyan accents, and soft pastel syntax highlighting.
2. **FluxDev Midnight**: Pure OLED pitch-black (`#000000`) with neon violet/cyan highlights and razor-sharp contrast.
3. **FluxDev Light**: Clean daylight theme (`#F8FAFC`) with jewel-toned syntax highlighting.

Cycle themes on the fly via the title bar **Theme** button or the Command Palette.

---

## 🚀 Setup & Launch (Windows PowerShell)

Ensure Python 3.10+ is installed on your system.


### 1. Clone the repository

```powershell
git clone https://github.com/kamalesh2602/FluxDev.git
```

### 2. Navigate to the project directory

```powershell
cd FluxDev
```

### 3. Create a virtual environment

```powershell
python -m venv venv
```

### 4. Activate the virtual environment

```powershell
.\venv\Scripts\Activate.ps1
```

### 5. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 6. Launch FluxDev

```powershell
python main.py
```

### Open a file or project directly

You can also pass a file or folder path as an argument to launch FluxDev directly into it:

```powershell
python main.py "path/to/my_web_app"
```

---

## ⌨️ Keyboard Shortcuts Reference

| Shortcut | Action |
| :--- | :--- |
| **`Ctrl + Shift + P`** / **`Ctrl + K`** | **Command Palette (Spotlight)** |
| **`F6`** / **`Ctrl + P`** | **Toggle Live WebEngine Preview (55/45 Split)** |
| **`Ctrl + N`** | New File (HTML5 Boilerplate by default) |
| **`Ctrl + O`** | Open File |
| **`Ctrl + S`** | Save Current File |
| **`Ctrl + Shift + S`** | Save File As |
| **`Ctrl + W`** | Close Current Tab |
| **`Ctrl + F`** / **`Ctrl + H`** | Find / Replace |
| **`Ctrl + G`** | Go to Line |
| **`Ctrl + D`** | Duplicate Current Line |
| **`Ctrl + /`** | Toggle Comment (`<!-- -->`, `/* */`, `//`) |
| **`Ctrl + Alt + F`** | Format Document (HTML/CSS/JS/JSON) |
| **`Tab`** | Expand Emmet abbreviation (e.g. `ul>li*3`, `!`) |
| **`F5`** | Force Refresh Live Preview |
| **`Ctrl + B`** | Animated Toggle: Project Explorer Sidebar |
| **`Ctrl + J`** | Toggle JavaScript Console Panel |
| **`Ctrl + +`** / **`Ctrl + -`** | Zoom Code Font In / Out |
