.DEFAULT_GOAL := help

QUARTO ?= quarto
PYTHON ?= $(shell pyenv which python 2>/dev/null || command -v python3)
QUARTO_PYTHON ?= $(PYTHON)
MPLCONFIGDIR ?= $(CURDIR)/.make-tmp/mpl
QUARTO_HOME ?= $(CURDIR)/.make-tmp/quarto-home
QUARTO_ENV ?= HOME="$(QUARTO_HOME)" XDG_CACHE_HOME="$(QUARTO_HOME)/.cache"

-include Makefile.local

export QUARTO_PYTHON
export MPLCONFIGDIR

RU_NOTEBOOKS := probability_demo uniform_sample_demo binomial_sample_demo poisson_sample_demo normal_sample_demo binomial_pmf_demo poisson_pmf_demo normal_density_demo poisson_gaussian_demo likelihood_demo fitting_demo intervals_demo feldman_cousins_demo hypothesis_tests_demo systematics_demo neutrino_cases_demo
EN_NOTEBOOKS := $(RU_NOTEBOOKS)
BOOK_RU_DIR := ru/book
BOOK_EN_DIR := en/book
SLIDES_RU_DIR := ru/slides
SLIDES_EN_DIR := en/slides

.PHONY: help check-env all books notebooks figures slides-site \
	ru-slides en-slides \
	pages-site \
	ru ru-html ru-pdf en en-html en-pdf \
	ru-notebooks en-notebooks \
	ru-notebook en-notebook clean clean-ru clean-en clean-notebooks clean-figures clean-cache

help: ## Показать цели сборки
	@printf '%s\n' 'Доступные цели:'
	@awk 'BEGIN {FS = ":.*## "}; /^[a-zA-Z0-9_.-]+:.*## / {printf "  %-24s %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@printf '\n%s\n' 'Отдельный notebook:'
	@printf '  make ru-notebook NOTEBOOK=probability_demo\n'
	@printf '  make en-notebook NOTEBOOK=probability_demo\n'

check-env: ## Проверить Quarto и Python
	@command -v "$(QUARTO)" >/dev/null 2>&1 || { echo "Не найден quarto: $(QUARTO)"; exit 1; }
	@if ! command -v "$(PYTHON)" >/dev/null 2>&1 && [ ! -x "$(PYTHON)" ]; then \
	  echo "Не найден Python: $(PYTHON)"; exit 1; \
	  exit 1; \
	fi
	@mkdir -p "$(MPLCONFIGDIR)"
	@mkdir -p "$(QUARTO_HOME)/Library/Caches" "$(QUARTO_HOME)/.cache"

all: figures books ## Собрать фигуры и обе книги

books: ru en ## Собрать обе книги

pages-site: figures ru-html en-html slides-site ## Собрать локальный артефакт GitHub Pages в .make-tmp/pages-site
	scripts/assemble_pages_site.sh

slides-site: ru-slides en-slides ## Собрать сайты со слайдами RU и EN

ru-slides: check-env ## Собрать русские слайды
	$(QUARTO_ENV) $(QUARTO) render $(SLIDES_RU_DIR)

en-slides: check-env ## Собрать английские слайды
	$(QUARTO_ENV) $(QUARTO) render $(SLIDES_EN_DIR)

ru: check-env ## Собрать русскую книгу целиком
	$(QUARTO_ENV) $(QUARTO) render $(BOOK_RU_DIR)

en: check-env ## Собрать английскую книгу целиком
	$(QUARTO_ENV) $(QUARTO) render $(BOOK_EN_DIR)

ru-html: check-env ## Собрать HTML русской книги
	$(QUARTO_ENV) $(QUARTO) render $(BOOK_RU_DIR) --to html

ru-pdf: check-env ## Собрать PDF русской книги
	$(QUARTO_ENV) $(QUARTO) render $(BOOK_RU_DIR) --to pdf

en-html: check-env ## Собрать HTML английской книги
	$(QUARTO_ENV) $(QUARTO) render $(BOOK_EN_DIR) --to html

en-pdf: check-env ## Собрать PDF английской книги
	$(QUARTO_ENV) $(QUARTO) render $(BOOK_EN_DIR) --to pdf

figures: check-env ## Сгенерировать общие фигуры
	$(PYTHON) scripts/build_figures.py

ru-notebooks: check-env ## Пересобрать все русские ноутбуки как отдельные входы
	@for nb in $(RU_NOTEBOOKS); do \
	  $(QUARTO_ENV) scripts/render_notebook_standalone.sh ru $$nb; \
	done

en-notebooks: check-env ## Пересобрать все английские ноутбуки как отдельные входы
	@for nb in $(EN_NOTEBOOKS); do \
	  $(QUARTO_ENV) scripts/render_notebook_standalone.sh en $$nb; \
	done

ru-notebook: check-env ## Собрать один русский notebook: make ru-notebook NOTEBOOK=probability_demo
	@test -n "$(NOTEBOOK)" || { echo "Укажи NOTEBOOK=<slug>"; exit 1; }
	$(QUARTO_ENV) scripts/render_notebook_standalone.sh ru $(NOTEBOOK)

en-notebook: check-env ## Собрать один английский notebook: make en-notebook NOTEBOOK=probability_demo
	@test -n "$(NOTEBOOK)" || { echo "Укажи NOTEBOOK=<slug>"; exit 1; }
	$(QUARTO_ENV) scripts/render_notebook_standalone.sh en $(NOTEBOOK)

clean: clean-ru clean-en clean-notebooks clean-figures clean-cache ## Очистить артефакты сборки

clean-ru: ## Очистить артефакты русской книги
	rm -rf $(BOOK_RU_DIR)/_book $(BOOK_RU_DIR)/.quarto

clean-en: ## Очистить артефакты английской книги
	rm -rf $(BOOK_EN_DIR)/_book $(BOOK_EN_DIR)/.quarto

clean-notebooks: ## Очистить standalone-артефакты ноутбуков
	rm -rf $(BOOK_RU_DIR)/notebooks/*.html $(BOOK_RU_DIR)/notebooks/*.pdf $(BOOK_RU_DIR)/notebooks/*_files $(BOOK_EN_DIR)/notebooks/*.html $(BOOK_EN_DIR)/notebooks/*.pdf $(BOOK_EN_DIR)/notebooks/*_files

clean-figures: ## Очистить shared/figures/generated
	rm -rf shared/figures/generated/*

clean-cache: ## Очистить временные кэши
	rm -rf .make-tmp
