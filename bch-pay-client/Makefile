.PHONY: help install test run-api run-discord run-telegram run-hybrid clean

help:
	@echo "Comandos disponibles:"
	@echo "  make install       Instala dependencias con pip"
	@echo "  make test          Ejecuta tests"
	@echo "  make run-api       Inicia agente API REST"
	@echo "  make run-discord   Inicia bot Discord"
	@echo "  make run-telegram  Inicia bot Telegram"
	@echo "  make run-hybrid    Inicia todos los agentes"
	@echo "  make clean         Elimina archivos temporales"

install:
	pip install -e ".[all]"
	pip install pytest

test:
	pytest tests/ -v

run-api:
	python examples/agent_api.py

run-discord:
	DISCORD_BOT_TOKEN=$(filter-out $@,$(MAKECMDGOALS)) python examples/agent_discord.py
	%:

run-telegram:
	TELEGRAM_BOT_TOKEN=$(filter-out $@,$(MAKECMDGOALS)) python examples/agent_telegram.py
	%:

run-hybrid:
	python examples/agent_hybrid.py

clean:
	rm -f bch_pay_client/__pycache__/*.pyc
	rm -rf __pycache__
	rm -f .coverage htmlcov/
	find . -name "*.pyc" -delete