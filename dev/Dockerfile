# === Dev Stage ===
FROM python:3.13-slim AS dev
# FROM nvidia/cuda:12.4.1-devel-ubuntu22.04 as base

# Set environment variables for Python behavior and module discovery
ENV PYTHONUNBUFFERED=1
# ENV PYTHONPATH="$PYTHONPATH:/code"
ENV TERM=xterm-256color

# Install build tools and required system packages
RUN apt-get update -y && apt-get install --no-install-recommends -y \
    build-essential \
    ca-certificates \
    curl \
    socat \
    docker.io \
    fzf \
    fontconfig \
    git \
    inotify-tools \
    python3-dev \
    python3-pip \
    sudo \
    unzip \
    vim \
    zsh

# --- Node.js (via NodeSource) ---
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get update && apt-get install -y nodejs \
    && npm install -g npm \
    && node -v && npm -v && npx --version


# --- <fixuid install> ---
ARG FIXUID_VERSION=0.6.0
RUN curl -fsSL https://github.com/boxboat/fixuid/releases/download/v${FIXUID_VERSION}/fixuid-${FIXUID_VERSION}-linux-amd64.tar.gz \
    | tar -C /usr/local/bin -xz && \
    chown root:root /usr/local/bin/fixuid && chmod 4755 /usr/local/bin/fixuid
# --- non-root user; UID/GID will be remapped at runtime by fixuid ---
RUN useradd -m -u 1000 -U dev && usermod -aG sudo dev
RUN echo "dev ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/dev && chmod 0440 /etc/sudoers.d/dev

ENV USER=dev
ENV HOME=/home/dev

# fixuid config
COPY <<'EOF' /etc/fixuid/config.yml
user: dev
group: dev
EOF

# workspace + caches under /home/dev (match your volumes below)
RUN mkdir -p /workspace \
    $HOME/history \
    $HOME/.vscode-server \
    $HOME/.cache/huggingface \
    $HOME/.cache/google-vscode-extension \
    $HOME/.gemini
RUN chown -R dev:dev /home/dev /workspace
ENV HISTFILE=$HOME/history/.zsh_history
# --- </fixuid install> ---


# --- <zsh + Oh My Zsh + Powerlevel10k + plugins> ---
# Nerd Font: MesloLGS (helps in GUI/tmux; still install Meslo so apps in-container can render it)
RUN mkdir -p /usr/local/share/fonts \
    && curl -fsSL -o /tmp/Meslo.zip https://github.com/ryanoasis/nerd-fonts/releases/latest/download/Meslo.zip \
    && unzip -q /tmp/Meslo.zip -d /usr/local/share/fonts/meslo \
    && fc-cache -f \
    && rm -f /tmp/Meslo.zip

USER dev

# Install Oh My Zsh unattended
RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended

# Powerlevel10k theme and plugins (autosuggestions + syntax highlighting)
RUN git clone --depth=1 https://github.com/romkatv/powerlevel10k.git $HOME/.oh-my-zsh/custom/themes/powerlevel10k \
    && git clone --depth=1 https://github.com/zsh-users/zsh-autosuggestions.git $HOME/.oh-my-zsh/custom/plugins/zsh-autosuggestions \
    && git clone --depth=1 https://github.com/zsh-users/zsh-syntax-highlighting.git $HOME/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting
# zsh config
RUN printf '%s\n' \
    'export ZSH="$HOME/.oh-my-zsh"' \
    'ZSH_THEME="powerlevel10k/powerlevel10k"' \
    'plugins=(git docker python zsh-autosuggestions zsh-syntax-highlighting)' \
    'export HISTFILE=$HOME/history/.zsh_history' \
    'export POWERLEVEL10K_DISABLE_CONFIGURATION_WIZARD=true' \
    'setopt HIST_IGNORE_ALL_DUPS SHARE_HISTORY INC_APPEND_HISTORY' \
    'source $ZSH/oh-my-zsh.sh' \
    '[[ -f ~/.p10k.zsh ]] && source ~/.p10k.zsh' \
    > $HOME/.zshrc
# after your Oh My Zsh setup and .zshrc that sources ~/.p10k.zsh
COPY p10k.zsh $HOME/.p10k.zsh
# reset user
USER root
# Make zsh the login shell for root (won't affect Docker RUN shell)
RUN chsh -s /usr/bin/zsh root || true
RUN chsh -s /usr/bin/zsh dev || true
# --- </zsh + Oh My Zsh + Powerlevel10k + plugins> ---


# --- GeminiCLI ---
RUN npm install -g @google/gemini-cli


# --- <Poetry (system-wide) + shared venv> ---
USER root

# Install Poetry to a shared location and expose to PATH
ENV POETRY_HOME=/opt/poetry
RUN curl -sSL https://install.python-poetry.org | python - \
    && ln -sf "$POETRY_HOME/bin/poetry" /usr/local/bin/poetry
ENV PATH="$POETRY_HOME/bin:$PATH"

# Create a single shared virtualenv and make it writable by dev
RUN python -m venv /opt/venv && chown -R dev:dev /opt/venv
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Tell Poetry to use the existing venv instead of creating its own
# (env var applies to all users; no per-user config needed)
ENV POETRY_VIRTUALENVS_CREATE=false
# (optional, but explicit)
ENV POETRY_VIRTUALENVS_IN_PROJECT=false

# Copy lockfiles into $HOME so they’re visible there, and install
# NOTE: these COPYs require the files to exist in the build context.
WORKDIR $HOME
USER dev
COPY pyproject.toml poetry.lock* ./
# Ensure base tools are present in the venv for faster/cleaner installs
RUN poetry install --no-root --no-interaction --no-ansi
# --- </Poetry (system-wide) + shared venv> ---


# make dev the default runtime user
USER root
RUN chown -R dev:dev $HOME

USER dev
WORKDIR /workspace
# run fixuid first; it remaps dev->host UID:GID, then execs your CMD as 'dev'
USER root
# Install proxy helper script into the image so compose can invoke it directly
COPY dev-proxy.sh /usr/local/bin/dev-proxy.sh
RUN chmod +x /usr/local/bin/dev-proxy.sh && chown dev:dev /usr/local/bin/dev-proxy.sh
USER dev
ENTRYPOINT ["fixuid","-q","--"]
CMD ["zsh"]  # or your app command


# === Release Stage ===
FROM python:3.13-slim AS release

# System deps (minimal)
RUN apt update -y && apt install --no-install-recommends -y curl

#TODO: copy files from dev