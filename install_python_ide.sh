#!/bin/bash

set -e

# CONFIG
REPO_URL="https://github.com/Ulrich1981/Python-IDE.git"
REPO_DIR="$HOME/.Python-IDE"
PYTHON_VERSION="python3"  # <-- use system default
VENV_DIR="$REPO_DIR/venv"
STARTER_LINK="/usr/local/bin/Python-IDE"

# --- Install dependencies ---
echo "Installing dependencies..."
sudo apt update
sudo apt install -y $PYTHON_VERSION $PYTHON_VERSION-venv git
sudo apt install -y python3-tk

# --- Clone repo ---
if [ ! -d "$REPO_DIR" ]; then
    echo "Cloning repository..."
    git clone "$REPO_URL" "$REPO_DIR"
fi

# --- Setup virtual environment ---
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    $PYTHON_VERSION -m venv "$VENV_DIR"
fi

echo "Installing requirements..."
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install -r "$REPO_DIR/requirements.txt"

# --- Make executable ---
echo "Creating launcher script..."
cat << EOF > "$REPO_DIR/launch.sh"
#!/bin/bash
cd "$HOME/.Python-IDE"
source "$HOME/.Python-IDE/venv/bin/activate"
python3 "$HOME/.Python-IDE/Python-IDE/python_ide.py"
EOF

chmod +x "$REPO_DIR/launch.sh"

# --- Add to PATH (optional) ---
if [ ! -d /usr/local/bin ]; then
    echo "Creating /usr/local/bin..."
    sudo mkdir -p /usr/local/bin
fi
echo "Creating system-wide shortcut..."
sudo ln -sf "$REPO_DIR/launch.sh" "$STARTER_LINK"

echo "Installation complete. Run the app using: Python-IDE"
