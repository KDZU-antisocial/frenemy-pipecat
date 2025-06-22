check:
	uv pip check
	uv pip list
	uv pip install -r requirements.txt --dry-run

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
		if grep -q "DEEPGRAM_API_KEY=" .env && ! grep -q "DEEPGRAM_API_KEY=your_deepgram_key_here" .env; then \
			echo "✅ DEEPGRAM_API_KEY is set"; \
		else \
			echo "❌ DEEPGRAM_API_KEY not configured"; \
		fi; \
		if grep -q "CARTESIA_API_KEY=" .env && ! grep -q "CARTESIA_API_KEY=your_cartesia_key_here" .env; then \
			echo "✅ CARTESIA_API_KEY is set"; \
		else \
			echo "❌ CARTESIA_API_KEY not configured"; \
		fi; \
	else \
		echo "❌ .env file not found. Run 'make env-setup' first"; \
	fi

# Development helpers
dev-setup: env-setup
	@echo "🚀 Setting up development environment..."
	uv sync
	@echo "✅ Development environment ready!"

test-env: env-load
	@echo "🧪 Testing environment..."
	python3 test_deepgram.py

# Quick start commands
web: env-load
	@echo "🌐 Starting web voice chat..."
	python3 src/main.py

terminal: env-load
	@echo "💻 Starting terminal voice chat..."
	python3 terminal_voice_chat.py

bicycle: env-load
	@echo "🚲 Starting bicycle assembly guide..."
	python3 bicycle_voice_chat.py 