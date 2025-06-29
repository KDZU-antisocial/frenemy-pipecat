check:
	@echo "🔍 Checking Python dependencies..."
	@if command -v uv >/dev/null 2>&1; then \
		uv pip check; \
		uv pip list; \
		uv pip install -r requirements.txt --dry-run; \
	else \
		echo "❌ uv not found. Installing uv is recommended for better dependency management."; \
		echo "📦 Install uv with: curl -LsSf https://astral.sh/uv/install.sh | sh"; \
		echo "🔄 Or visit: https://docs.astral.sh/uv/getting-started/installation/"; \
		echo ""; \
		echo "Falling back to pip..."; \
		pip check; \
		pip list; \
		pip install -r requirements.txt --dry-run; \
	fi

# System dependency management
sys-check:
	@echo "🔍 Checking system dependencies..."
	@echo "Checking for Homebrew..."
	@if ! command -v brew >/dev/null 2>&1; then \
		echo "❌ Homebrew not found. Please install from https://brew.sh/"; \
		exit 1; \
	else \
		echo "✅ Homebrew found"; \
	fi
	@echo "Checking for opus..."
	@if ! command -v opus >/dev/null 2>&1; then \
		echo "❌ opus not found"; \
	else \
		echo "✅ opus found"; \
	fi
	@echo "Checking for ffmpeg..."
	@if ! command -v ffmpeg >/dev/null 2>&1; then \
		echo "❌ ffmpeg not found"; \
	else \
		echo "✅ ffmpeg found"; \
	fi
	@echo "Checking for pkg-config..."
	@if ! command -v pkg-config >/dev/null 2>&1; then \
		echo "❌ pkg-config not found"; \
	else \
		echo "✅ pkg-config found"; \
	fi
	@echo "Checking for sox..."
	@if ! command -v sox >/dev/null 2>&1; then \
		echo "❌ sox not found"; \
	else \
		echo "✅ sox found"; \
	fi

sys-install:
	@echo "📦 Installing system dependencies..."
	@if command -v brew >/dev/null 2>&1; then \
		echo "Installing opus, ffmpeg, pkg-config, and sox via Homebrew..."; \
		brew install opus ffmpeg pkg-config sox; \
		echo "✅ System dependencies installed"; \
	else \
		echo "❌ Homebrew not found. Please install from https://brew.sh/"; \
		echo "Then run: brew install opus ffmpeg pkg-config sox"; \
		exit 1; \
	fi

# Environment setup and management
env-setup:
	@echo "🔧 Setting up environment..."
	@if [ ! -f .env ]; then \
		cp env.template .env; \
		echo "✅ Created .env from template"; \
		echo "📝 Please edit .env with your API keys"; \
	else \
		echo "✅ .env file already exists"; \
	fi

env-load:
	@echo "📤 Loading environment variables..."
	@if [ -f .env ]; then \
		export $$(grep -v '^#' .env | xargs); \
		echo "✅ Environment variables loaded"; \
		echo "🔑 DEEPGRAM_API_KEY: $${DEEPGRAM_API_KEY:0:10}..."; \
		echo "🔑 CARTESIA_API_KEY: $${CARTESIA_API_KEY:0:10}..."; \
	else \
		echo "❌ .env file not found. Run 'make env-setup' first"; \
	fi

env-check:
	@echo "🔍 Checking environment variables..."
	@if [ -f .env ]; then \
		if grep -q "DEEPGRAM_API_KEY=" .env && ! grep -q "DEEPGRAM_API_KEY=your_deepgram_api_key_here" .env; then \
			echo "✅ DEEPGRAM_API_KEY is set"; \
		else \
			echo "❌ DEEPGRAM_API_KEY not configured"; \
		fi; \
		if grep -q "CARTESIA_API_KEY=" .env && ! grep -q "CARTESIA_API_KEY=your_cartesia_api_key_here" .env; then \
			echo "✅ CARTESIA_API_KEY is set"; \
		else \
			echo "❌ CARTESIA_API_KEY not configured"; \
		fi; \
	else \
		echo "❌ .env file not found. Run 'make env-setup' first"; \
	fi

# Development helpers
dev-setup: sys-check env-setup
	@echo "🚀 Setting up development environment..."
	@echo "Installing Python dependencies..."
	@if command -v uv >/dev/null 2>&1; then \
		echo "✅ Using uv for dependency management..."; \
		uv pip install -r requirements.txt; \
	else \
		echo "⚠️  uv not found. Installing uv is recommended for better dependency management."; \
		echo "📦 Install uv with: curl -LsSf https://astral.sh/uv/install.sh | sh"; \
		echo "🔄 Or visit: https://docs.astral.sh/uv/getting-started/installation/"; \
		echo ""; \
		echo "Falling back to pip..."; \
		pip install -r requirements.txt; \
	fi
	@echo "✅ Development environment ready!"

# Complete setup including system dependencies
full-setup: sys-install dev-setup
	@echo "🎉 Complete setup finished!"
	@echo "Next steps:"
	@echo "1. Edit .env with your API keys"
	@echo "2. Run 'make env-check' to verify"
	@echo "3. Run 'make web', 'make terminal', or 'make rover' to start"

# Python execution helper
python-run:
	@if command -v uv >/dev/null 2>&1; then \
		uv run python; \
	else \
		echo "⚠️  uv not found. Installing uv is recommended for better dependency management."; \
		echo "📦 Install uv with: curl -LsSf https://astral.sh/uv/install.sh | sh"; \
		echo "🔄 Or visit: https://docs.astral.sh/uv/getting-started/installation/"; \
		echo ""; \
		echo "Falling back to python3..."; \
		python3; \
	fi

test-env: env-load
	@echo "🧪 Testing environment..."
	@if command -v uv >/dev/null 2>&1; then \
		uv run python test_deepgram.py; \
	else \
		echo "⚠️  uv not found. Installing uv is recommended for better dependency management."; \
		echo "📦 Install uv with: curl -LsSf https://astral.sh/uv/install.sh | sh"; \
		echo "🔄 Or visit: https://docs.astral.sh/uv/getting-started/installation/"; \
		echo ""; \
		echo "Falling back to python3..."; \
		python3 test_deepgram.py; \
	fi

# Quick start commands
web: env-load
	@echo "🌐 Starting web voice chat..."
	@if command -v uv >/dev/null 2>&1; then \
		uv run python src/main.py; \
	else \
		echo "⚠️  uv not found. Installing uv is recommended for better dependency management."; \
		echo "📦 Install uv with: curl -LsSf https://astral.sh/uv/install.sh | sh"; \
		echo "🔄 Or visit: https://docs.astral.sh/uv/getting-started/installation/"; \
		echo ""; \
		echo "Falling back to python3..."; \
		python3 src/main.py; \
	fi

terminal: env-load
	@echo "💻 Starting terminal voice chat..."
	@if command -v uv >/dev/null 2>&1; then \
		uv run python terminal_voice_chat.py; \
	else \
		echo "⚠️  uv not found. Installing uv is recommended for better dependency management."; \
		echo "📦 Install uv with: curl -LsSf https://astral.sh/uv/install.sh | sh"; \
		echo "🔄 Or visit: https://docs.astral.sh/uv/getting-started/installation/"; \
		echo ""; \
		echo "Falling back to python3..."; \
		python3 terminal_voice_chat.py; \
	fi

rover: env-load
	@echo "🚗 Starting rover assembly guide..."
	@if command -v uv >/dev/null 2>&1; then \
		uv run python rover_voice_chat.py; \
	else \
		echo "⚠️  uv not found. Installing uv is recommended for better dependency management."; \
		echo "📦 Install uv with: curl -LsSf https://astral.sh/uv/install.sh | sh"; \
		echo "🔄 Or visit: https://docs.astral.sh/uv/getting-started/installation/"; \
		echo ""; \
		echo "Falling back to python3..."; \
		python3 rover_voice_chat.py; \
	fi

# Additional uv-specific commands
uv-sync:
	@echo "🔄 Syncing dependencies with uv..."
	@if command -v uv >/dev/null 2>&1; then \
		uv sync; \
	else \
		echo "❌ uv not found. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"; \
		echo "🔄 Or visit: https://docs.astral.sh/uv/getting-started/installation/"; \
	fi

uv-add:
	@echo "📦 Add a new dependency with uv..."
	@if command -v uv >/dev/null 2>&1; then \
		uv add $(package); \
	else \
		echo "❌ uv not found. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"; \
		echo "🔄 Or visit: https://docs.astral.sh/uv/getting-started/installation/"; \
	fi

uv-remove:
	@echo "🗑️ Remove a dependency with uv..."
	@if command -v uv >/dev/null 2>&1; then \
		uv remove $(package); \
	else \
		echo "❌ uv not found. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"; \
		echo "🔄 Or visit: https://docs.astral.sh/uv/getting-started/installation/"; \
	fi

# Install uv command
install-uv:
	@echo "📦 Installing uv package manager..."
	@if command -v uv >/dev/null 2>&1; then \
		echo "✅ uv is already installed"; \
	else \
		echo "Installing uv..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
		echo "✅ uv installed successfully!"; \
		echo "🔄 Please restart your terminal or run: source ~/.zshrc"; \
	fi 