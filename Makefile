.DEFAULT_GOAL := help

QUARTO ?= quarto
PYTHON ?= $(shell pyenv which python 2>/dev/null || command -v python3)
QUARTO_PYTHON ?= $(PYTHON)
CHAPTER_PYTHON ?= $(PYTHON)

-include Makefile.local

export QUARTO_PYTHON

RU_NOTEBOOKS := probability_demo uniform_sample_demo binomial_sample_demo poisson_sample_demo normal_sample_demo binomial_pmf_demo poisson_pmf_demo normal_density_demo poisson_gaussian_demo likelihood_demo fitting_demo intervals_demo feldman_cousins_demo hypothesis_tests_demo systematics_demo neutrino_cases_demo
EN_NOTEBOOKS := $(RU_NOTEBOOKS)
BOOK_RU_DIR := ru/book
BOOK_EN_DIR := en/book
SLIDES_RU_DIR := ru/slides
SLIDES_EN_DIR := en/slides
RU_PDF_CHAPTERS := \
	01_why_statistics \
	02_random_distributions \
	03_characteristic_functions \
	04_central_limit_theorem \
	05_non_gaussian_clt_violations \
	06_error_propagation \
	07_two_dimensional_gaussian \
	08_monte_carlo_method \
	09_maximum_likelihood \
	10_estimator_properties_profile_likelihood \
	11_least_squares_linear_fit \
	12_least_squares_systematics \
	13_goodness_of_fit_and_significance

.PHONY: help check-env check-book-sources ci-setup site all books notebooks figures book-qr slides \
	ru-slides en-slides \
	ru ru-html ru-pdf ru-chapters ru-epub en en-html en-pdf en-epub \
	ru-notebooks en-notebooks ru-notebook en-notebook \
	clean clean-site clean-ru clean-en clean-notebooks clean-figures clean-cache

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
	fi

ci-setup: check-env ## Установить зависимости для CI
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt
	@if command -v lualatex >/dev/null 2>&1; then \
	  echo 'LuaLaTeX уже установлен.'; \
	else \
	  $(QUARTO) install tinytex --no-prompt; \
	fi

site: check-env check-book-sources book-qr ## Собрать полный сайт в _site
	rm -rf _site $(BOOK_RU_DIR)/_book $(BOOK_EN_DIR)/_book $(SLIDES_RU_DIR)/_site $(SLIDES_EN_DIR)/_site
	mkdir -p _site/shared
	cp pages/index.html pages/applets.html pages/robots.txt _site/
	$(PYTHON) scripts/build_figures.py
	cp -R shared/analytics shared/styles shared/applets _site/shared/
	$(QUARTO) render $(BOOK_RU_DIR) --to html
	$(QUARTO) render $(BOOK_RU_DIR) --to pdf
	$(CHAPTER_PYTHON) scripts/render_book_chapters.py ru $(RU_PDF_CHAPTERS)
	$(QUARTO) render $(BOOK_EN_DIR) --to html
	$(QUARTO) render $(SLIDES_RU_DIR)
	$(QUARTO) render $(SLIDES_EN_DIR)
	test -s _site/index.html
	test -s _site/ru/book/index.html
	test -s _site/ru/book/statistical-data-analysis.pdf
	@for chapter in $(RU_PDF_CHAPTERS); do test -s _site/ru/book/chapters/$$chapter.pdf; done
	test -s _site/en/book/index.html

all: figures books ## Собрать фигуры и обе книги

books: ru en ## Собрать обе книги

slides: ru-slides en-slides ## Собрать сайты со слайдами RU и EN

ru-slides: check-env ## Собрать русские слайды
	$(QUARTO) render $(SLIDES_RU_DIR)
	mkdir -p _site/shared
	cp -R shared/applets _site/shared/

en-slides: check-env ## Собрать английские слайды
	$(QUARTO) render $(SLIDES_EN_DIR)
	mkdir -p _site/shared
	cp -R shared/applets _site/shared/

ru: check-env check-book-sources book-qr ## Собрать русскую книгу целиком
	$(QUARTO) render $(BOOK_RU_DIR)

en: check-env ## Собрать английскую книгу целиком
	$(QUARTO) render $(BOOK_EN_DIR)

ru-html: check-env check-book-sources book-qr ## Собрать HTML русской книги
	$(QUARTO) render $(BOOK_RU_DIR) --to html

ru-pdf: check-env check-book-sources book-qr ## Собрать PDF русской книги
	$(QUARTO) render $(BOOK_RU_DIR) --to pdf

ru-chapters: ru-pdf ## Собрать отдельные PDF готовых русских глав
	$(CHAPTER_PYTHON) scripts/render_book_chapters.py ru $(RU_PDF_CHAPTERS)

ru-epub: check-env check-book-sources book-qr ## Собрать EPUB русской книги
	$(QUARTO) render $(BOOK_RU_DIR) --to epub
	$(PYTHON) scripts/finalize_epub.py _site/ru/book/statistical-data-analysis.epub
	@if command -v epubcheck >/dev/null 2>&1; then epubcheck _site/ru/book/statistical-data-analysis.epub; else echo "epubcheck не найден: внутренняя проверка выполнена"; fi

en-html: check-env ## Собрать HTML английской книги
	$(QUARTO) render $(BOOK_EN_DIR) --to html

en-pdf: check-env ## Собрать PDF английской книги
	$(QUARTO) render $(BOOK_EN_DIR) --to pdf

en-epub: check-env ## Собрать EPUB английской книги
	$(QUARTO) render $(BOOK_EN_DIR) --to epub

figures: check-env ## Сгенерировать общие фигуры
	$(PYTHON) scripts/build_figures.py

book-qr: check-env ## Создать недостающие QR-коды для книги
	$(PYTHON) scripts/generate_book_qr.py

check-book-sources: check-env ## Проверить структуру исходников русской книги
	$(PYTHON) scripts/check_book_sources.py

ru-notebooks: check-env ## Пересобрать все русские ноутбуки как отдельные входы
	@for nb in $(RU_NOTEBOOKS); do \
	  scripts/render_notebook_standalone.sh ru $$nb; \
	done

en-notebooks: check-env ## Пересобрать все английские ноутбуки как отдельные входы
	@for nb in $(EN_NOTEBOOKS); do \
	  scripts/render_notebook_standalone.sh en $$nb; \
	done

ru-notebook: check-env ## Собрать один русский notebook: make ru-notebook NOTEBOOK=probability_demo
	@test -n "$(NOTEBOOK)" || { echo "Укажи NOTEBOOK=<slug>"; exit 1; }
	scripts/render_notebook_standalone.sh ru $(NOTEBOOK)

en-notebook: check-env ## Собрать один английский notebook: make en-notebook NOTEBOOK=probability_demo
	@test -n "$(NOTEBOOK)" || { echo "Укажи NOTEBOOK=<slug>"; exit 1; }
	scripts/render_notebook_standalone.sh en $(NOTEBOOK)

clean: clean-site clean-ru clean-en clean-notebooks clean-figures clean-cache ## Очистить артефакты сборки

clean-site: ## Очистить полный сайт
	rm -rf _site .quarto

clean-ru: ## Очистить артефакты русской книги
	rm -rf _site/ru/book $(BOOK_RU_DIR)/_book $(BOOK_RU_DIR)/.quarto

clean-en: ## Очистить артефакты английской книги
	rm -rf _site/en/book $(BOOK_EN_DIR)/_book $(BOOK_EN_DIR)/.quarto

clean-notebooks: ## Очистить standalone-артефакты ноутбуков
	rm -rf $(BOOK_RU_DIR)/notebooks/*.html $(BOOK_RU_DIR)/notebooks/*.pdf $(BOOK_RU_DIR)/notebooks/*_files $(BOOK_EN_DIR)/notebooks/*.html $(BOOK_EN_DIR)/notebooks/*.pdf $(BOOK_EN_DIR)/notebooks/*_files

clean-figures: ## Очистить shared/figures/generated
	rm -rf shared/figures/generated/*

clean-cache: ## Очистить временные кэши
	rm -rf .make-tmp
