-- shared/filters/drop-ojs-in-pdf.lua
-- Remove Observable JS cells from LaTeX/PDF output.
-- HTML output is left unchanged.

local function is_latex_output()
  if quarto and quarto.doc and quarto.doc.is_format then
    return quarto.doc.is_format("pdf") or quarto.doc.is_format("latex")
  end
  return FORMAT:match("latex") or FORMAT:match("pdf") or FORMAT:match("beamer")
end

local function has_class(el, class)
  if not el.classes then
    return false
  end
  for _, c in ipairs(el.classes) do
    if c == class then
      return true
    end
  end
  return false
end

local function looks_like_ojs(text)
  if not text then
    return false
  end

  return
    text:match("^%s*//%|") or
    text:match("viewof%s+") or
    text:match("Inputs%.") or
    text:match("Plot%.") or
    text:match("html`") or
    text:match("FileAttachment%(") or
    text:match("Mutable%s*%(")
end

local function block_is_ojs(block)
  if block.t ~= "CodeBlock" then
    return false
  end

  return
    has_class(block, "ojs") or
    has_class(block, "observable") or
    has_class(block, "observablehq") or
    looks_like_ojs(block.text)
end

local function blocks_have_ojs(blocks)
  if not blocks then
    return false
  end

  for _, block in ipairs(blocks) do
    if block_is_ojs(block) then
      return true
    end

    if block.content and blocks_have_ojs(block.content) then
      return true
    end
  end

  return false
end

function CodeBlock(el)
  if not is_latex_output() then
    return nil
  end

  if block_is_ojs(el) then
    return {}
  end
end

function Div(el)
  if not is_latex_output() then
    return nil
  end

  if has_class(el, "cell") and blocks_have_ojs(el.content) then
    return {}
  end

  if has_class(el, "book-applet") and blocks_have_ojs(el.content) then
    return {}
  end
end

function Pandoc(doc)
  if is_latex_output() then
    io.stderr:write("[drop-ojs-in-pdf] active, FORMAT = " .. FORMAT .. "\n")
  end
  return doc
end