-- PDF-only visual mapping for custom book divs.
-- HTML is untouched: book.css continues to control the browser version.

local stringify = pandoc.utils.stringify

local function has_class(div, class_name)
  for _, c in ipairs(div.classes) do
    if c == class_name then return true end
  end
  return false
end

local function latex_escape_text(s)
  -- Titles extracted with stringify contain plain text only. Escape the characters
  -- that are most likely to be meaningful to LaTeX.
  local replacements = {
    ["\\"] = "\\textbackslash{}",
    ["{"] = "\\{",
    ["}"] = "\\}",
    ["#"] = "\\#",
    ["$"] = "\\$",
    ["%"] = "\\%",
    ["&"] = "\\&",
    ["_"] = "\\_",
    ["^"] = "\\^{}",
    ["~"] = "\\~{}"
  }
  return (s:gsub("[\\{}#$%%&_~%^]", replacements))
end

local function simple_title_from_block(block)
  if not block then return nil end
  if block.t == "Header" or block.t == "Para" or block.t == "Plain" then
    local s = stringify(block)
    if s and #s > 0 and #s <= 90 then return s end
  end
  return nil
end

local function figure_caption_blocks(fig)
  if not fig.caption then return pandoc.List() end
  if fig.caption.long and #fig.caption.long > 0 then
    return fig.caption.long
  end
  if fig.caption.short and #fig.caption.short > 0 then
    return pandoc.List({pandoc.Plain(fig.caption.short)})
  end
  return pandoc.List()
end

local function flatten_figure(fig, gallery)
  local out = pandoc.List()
  local env = gallery and "bookgalleryitem" or nil

  if env then out:insert(pandoc.RawBlock("latex", "\\begin{" .. env .. "}")) end
  out:insert(pandoc.RawBlock("latex", "\\begin{center}"))

  for _, b in ipairs(fig.content) do
    out:insert(b)
  end

  out:insert(pandoc.RawBlock("latex", "\\end{center}"))

  local cap = figure_caption_blocks(fig)
  if #cap > 0 then
    local captex = pandoc.write(pandoc.Pandoc(cap), "latex")
    captex = captex:gsub("%s+$", "")
    out:insert(pandoc.RawBlock("latex", "\\BookInlineFigureCaption{" .. captex .. "}"))
  end

  if fig.identifier and fig.identifier ~= "" then
    out:insert(pandoc.RawBlock("latex", "\\label{" .. fig.identifier .. "}"))
  end

  if env then out:insert(pandoc.RawBlock("latex", "\\end{" .. env .. "}")) end
  return out
end

local function flatten_figures(blocks, gallery)
  local out = pandoc.List()
  for _, b in ipairs(blocks) do
    if b.t == "Figure" then
      out:extend(flatten_figure(b, gallery))
    else
      out:insert(b)
    end
  end
  return out
end

local function wrap_blocks(blocks, env, opt_title, flatten)
  local out = pandoc.List()
  local begin
  if opt_title and opt_title ~= "" then
    begin = "\\begin{" .. env .. "}[" .. latex_escape_text(opt_title) .. "]"
  else
    begin = "\\begin{" .. env .. "}"
  end
  out:insert(pandoc.RawBlock("latex", begin))
  if flatten then
    out:extend(flatten_figures(blocks, false))
  else
    out:extend(blocks)
  end
  out:insert(pandoc.RawBlock("latex", "\\end{" .. env .. "}"))
  return out
end

local function title_box(div, env, default_title, remove_first_header, flatten)
  local blocks = pandoc.List(div.content)
  local title = default_title

  if #blocks > 0 then
    local candidate = simple_title_from_block(blocks[1])
    if candidate and (blocks[1].t == "Header" or remove_first_header) then
      title = candidate
      blocks:remove(1)
    end
  end

  return wrap_blocks(blocks, env, title, flatten)
end

function Div(div)
  if FORMAT ~= "latex" then return nil end

  if has_class(div, "chapter-opening") then
    -- The first short paragraph/span is the box label ("Аннотация").
    return title_box(div, "bookchapteropening", nil, true, true)
  end

  if has_class(div, "book-note") then
    return wrap_blocks(div.content, "booknote", nil, true)
  end

  if has_class(div, "book-derivation") then
    -- Keep the internal derivation heading, but add the small blue label used by
    -- the reference PDF.
    return wrap_blocks(div.content, "bookderivation", nil, true)
  end

  if has_class(div, "chapter-summary") then
    return title_box(div, "bookchaptersummary", "Итоги главы", false, true)
  end

  if has_class(div, "figure-panel") then
    -- Quarto turns the image into a LaTeX float after this filter runs. A float
    -- cannot be placed inside a tcolorbox, so PDF keeps the numbered figure and
    -- its following explanation without an outer panel.
    return div.content
  end

  if has_class(div, "result-gallery") then
    -- Full-width stacked gallery items are deliberately used in PDF. This keeps
    -- large scientific plots legible and matches the supplied reference edition
    -- better than squeezing two figures into narrow columns.
    return flatten_figures(div.content, true)
  end

  if has_class(div, "book-applet") then
    return title_box(div, "bookapplet", nil, false, true)
  end

  return nil
end
