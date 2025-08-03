# Typeman
A terminal‑based typing-speed test CLI tool that shows **real-time feedback**, **WPM**, and **accuracy** in a beautiful, live interface built with **Typer** and **Rich**.

<img width="959" height="599" alt="image" src="https://github.com/user-attachments/assets/7e5a5aca-63c9-4cb1-aad3-76c85c52b1fe" />


## ✨ Why Typeman?

- Fast, interactive, and cross-platform 🧭  
- Live-color feedback: correct keystrokes turn **green**, mistakes in **red**  
- Custom cursor highlights typing position  
- Uses a built-in 10k word list for realistic, daily vocabulary  
- No external dependencies beyond Python packages  


## 🚀 Installation

**Create a virtual environment using [uv](https://docs.astral.sh/uv/getting-started/installation/)**

```bash
uv venv .type
```

**Activate the virtual environment**

```bash
source .type/bin/activate
```

**Install Typeman into your isolated `.type` virtual environment**

```bash
uv pip install typeman
```

### Alternatively, if you prefer traditional tools

```bash
python3 -m venv .venv      # Create a virtual environment
source .venv/bin/activate
pip install typeman        # Standard pip install
```

## Usage

### 🔸 Run a 30-second typing test (seconds must be 0–60)
```bash
typeman 30 
```

## Demo

https://github.com/user-attachments/assets/5f087a16-bcae-463c-b1e1-ec984ab858ee
