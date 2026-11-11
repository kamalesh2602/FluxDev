"""
Starter templates for Web Development.
Provides HTML5 boilerplate and a complete 'HTML + CSS + JS' starter project folder.
"""

import os

HTML5_BOILERPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>New Web Page</title>
</head>
<body>
    <h1>Hello, World!</h1>
</body>
</html>
"""

STARTER_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web App Starter</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>🚀 My Web Project</h1>
            <p>Built with Notepad++ Web Studio</p>
        </header>

        <main>
            <div class="card">
                <h2>Interactive Demo</h2>
                <p>Click the button below to test JavaScript execution.</p>
                <button id="counter-btn" class="btn">Clicks: 0</button>
            </div>
        </main>

        <footer>
            <p>&copy; 2026 Web Studio Project</p>
        </footer>
    </div>

    <script src="script.js"></script>
</body>
</html>
"""

STARTER_CSS = """/* Modern Web App Stylesheet */
:root {
    --primary: #007acc;
    --primary-hover: #005999;
    --bg: #f8fafc;
    --card-bg: #ffffff;
    --text: #1e293b;
    --text-muted: #64748b;
    --border: #e2e8f0;
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background-color: var(--bg);
    color: var(--text);
    line-height: 1.6;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    padding: 20px;
}

.container {
    width: 100%;
    max-width: 600px;
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 32px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
}

header {
    text-align: center;
    margin-bottom: 24px;
}

header h1 {
    font-size: 26px;
    color: var(--primary);
    margin-bottom: 6px;
}

header p {
    color: var(--text-muted);
    font-size: 14px;
}

.card {
    background: #f1f5f9;
    border-radius: 8px;
    padding: 20px;
    text-align: center;
    margin-bottom: 24px;
}

.card h2 {
    font-size: 18px;
    margin-bottom: 8px;
}

.card p {
    font-size: 14px;
    color: var(--text-muted);
    margin-bottom: 16px;
}

.btn {
    background-color: var(--primary);
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.15s ease, transform 0.1s;
}

.btn:hover {
    background-color: var(--primary-hover);
}

.btn:active {
    transform: scale(0.98);
}

footer {
    text-align: center;
    font-size: 12px;
    color: var(--text-muted);
    border-top: 1px solid var(--border);
    padding-top: 16px;
}
"""

STARTER_JS = """// Web App Interactive Logic
console.log("Web App Starter initialized successfully!");

let clickCount = 0;
const btn = document.getElementById("counter-btn");

if (btn) {
    btn.addEventListener("click", () => {
        clickCount++;
        btn.textContent = `Clicks: ${clickCount}`;
        console.log(`Button clicked! New count: ${clickCount}`);
    });
}
"""


def create_starter_project(target_dir: str) -> list[str]:
    """
    Creates 'index.html', 'style.css', and 'script.js' inside target_dir.
    Returns the list of absolute paths to the created files.
    """
    os.makedirs(target_dir, exist_ok=True)

    files = {
        "index.html": STARTER_HTML,
        "style.css": STARTER_CSS,
        "script.js": STARTER_JS
    }

    created = []
    for filename, content in files.items():
        path = os.path.join(target_dir, filename)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
        created.append(path)

    return created
