.DEFAULT_GOAL := help

QUARTO ?= quarto
PYTHON ?= $(shell pyenv which python 2>/dev/null || command -v python3)
QUARTO_PYTHON ?= $(PYTHON)
CHAPTER_PYTHON ?= $(PYTHON)

-include Makefile.local

export QUARTO_PYTHON

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

SITE_OUTPUTS := \
	_site/index.html \
	_site/ru/book/index.html \
	_site/ru/book/statistical-data-analysis.pdf \
	$(addprefix _site/ru/book/chapters/,$(addsuffix .pdf,$(RU_PDF_CHAPTERS))) \
	_site/en/book/index.html \
	_site/ru/slides/index.html \
	_site/en/slides/index.html

.PHONY: help check-env check-book-sources ci-setup site home figures book-qr \
	ru-slides en-slides \
	ru-html ru-preview ru-pdf ru-chapters ru-epub en-html en-pdf en-epub \
	ru-notebook en-notebook clean

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
	@if [ "$(GITHUB_ACTIONS)" = true ]; then \
	  $(QUARTO) install tinytex --no-prompt && \
	  sh scripts/setup_book_tex.sh; \
	elif command -v lualatex >/dev/null 2>&1; then \
	  echo 'LuaLaTeX уже установлен.'; \
	else \
	  $(QUARTO) install tinytex --no-prompt; \
	fi

site: check-env check-book-sources book-qr ## Собрать полный сайт в _site
	rm -rf _site $(BOOK_RU_DIR)/_book $(BOOK_EN_DIR)/_book $(SLIDES_RU_DIR)/_site $(SLIDES_EN_DIR)/_site
	$(QUARTO) render
	$(PYTHON) scripts/build_figures.py
	$(QUARTO) render $(BOOK_RU_DIR) --to html
	$(QUARTO) render $(BOOK_RU_DIR) --to pdf
	$(PYTHON) scripts/finalize_chapter_bibliographies.py
	$(CHAPTER_PYTHON) scripts/render_book_chapters.py ru $(RU_PDF_CHAPTERS)
	$(QUARTO) render $(BOOK_EN_DIR) --to html
	$(QUARTO) render $(SLIDES_RU_DIR)
	$(QUARTO) render $(SLIDES_EN_DIR)
	@for f in $(SITE_OUTPUTS); do test -s "$$f" || { echo "Нет или пуст: $$f"; exit 1; }; done

home: check-env ## Собрать только страницу курса (_site/index.html, апплеты, shared)
	$(QUARTO) render

ru-slides: check-env ## Собрать русские слайды
	$(QUARTO) render $(SLIDES_RU_DIR)
	mkdir -p _site/shared
	cp -R shared/applets _site/shared/

en-slides: check-env ## Собрать английские слайды
	$(QUARTO) render $(SLIDES_EN_DIR)
	mkdir -p _site/shared
	cp -R shared/applets _site/shared/

ru-html: check-env check-book-sources book-qr ## Собрать HTML русской книги
	$(QUARTO) render $(BOOK_RU_DIR) --to html
	$(PYTHON) scripts/finalize_chapter_bibliographies.py

ru-preview: check-env check-book-sources book-qr ## Собрать и открыть локальную HTML-книгу
	$(QUARTO) preview $(BOOK_RU_DIR) --to html

ru-pdf: check-env check-book-sources book-qr ## Собрать PDF русской книги
	$(QUARTO) render $(BOOK_RU_DIR) --to pdf
	@if [ -f _site/ru/book/index.html ]; then $(PYTHON) scripts/finalize_chapter_bibliographies.py; fi

ru-chapters: ru-pdf ## Собрать отдельные PDF готовых русских глав
	$(CHAPTER_PYTHON) scripts/render_book_chapters.py ru $(RU_PDF_CHAPTERS)

ru-epub: check-env check-book-sources book-qr ## Собрать EPUB русской книги
	$(QUARTO) render $(BOOK_RU_DIR) --to epub
	$(PYTHON) scripts/finalize_epub.py _site/ru/book/statistical-data-analysis.epub
	@if command -v epubcheck >/dev/null 2>&1; then epubcheck _site/ru/book/statistical-data-analysis.epub; else echo "epubcheck не найден: внутренняя проверка выполнена"; fi

en-html: check-env ## Собрать HTML английской книги
	# Quarto does not replace notebook figures left in _site by an earlier render.
	rm -rf _site/en/book
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

ru-notebook: check-env ## Собрать один русский notebook: make ru-notebook NOTEBOOK=probability_demo
	@test -n "$(NOTEBOOK)" || { echo "Укажи NOTEBOOK=<slug>"; exit 1; }
	scripts/render_notebook_standalone.sh ru $(NOTEBOOK)

en-notebook: check-env ## Собрать один английский notebook: make en-notebook NOTEBOOK=probability_demo
	@test -n "$(NOTEBOOK)" || { echo "Укажи NOTEBOOK=<slug>"; exit 1; }
	scripts/render_notebook_standalone.sh en $(NOTEBOOK)

clean: ## Очистить артефакты сборки
	rm -rf _site .quarto $(BOOK_RU_DIR)/_book $(BOOK_RU_DIR)/.quarto $(BOOK_EN_DIR)/_book $(BOOK_EN_DIR)/.quarto .make-tmp
