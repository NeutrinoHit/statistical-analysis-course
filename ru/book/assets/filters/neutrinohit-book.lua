-- Shared cross-format components for NeutrinoHit books.
-- Subject-specific filters may add their own blocks, but biographies, media,
-- exercise labels and PDF chapter openers are defined here once.

local function has_class(el, name)
  return el.classes:includes(name)
end

local function add_class(el, name)
  if not has_class(el, name) then
    el.classes:insert(name)
  end
end

local function value(value)
  return value or ""
end

local function project_path(path)
  path = value(path)
  if FORMAT:match("latex") or FORMAT:match("epub") then
    return path:gsub("^%.%./", "")
  end
  return path
end

local function html_escape(text)
  return value(text)
    :gsub("&", "&amp;")
    :gsub("<", "&lt;")
    :gsub(">", "&gt;")
    :gsub('"', "&quot;")
end

local function latex_escape(text)
  return value(text)
    :gsub("\\", "\\textbackslash{}")
    :gsub("([%%#$&_{}])", "\\%1")
    :gsub("~", "\\textasciitilde{}")
    :gsub("%^", "\\textasciicircum{}")
end

local function heading(title, label)
  local content = {}
  if label ~= "" then
    content[#content + 1] = pandoc.Strong(label)
  end
  if title ~= "" then
    if #content > 0 then
      content[#content + 1] = pandoc.Str(". ")
    end
    content[#content + 1] = pandoc.Strong(title)
  end
  return pandoc.Para(content)
end

local function latex_box(blocks, identifier, options)
  local result = {}
  if identifier ~= "" then
    result[#result + 1] = pandoc.RawBlock(
      "latex", "\\hypertarget{" .. identifier .. "}{}"
    )
  end
  result[#result + 1] = pandoc.RawBlock(
    "latex", "\\begin{semanticpdfbox}" .. (options or "")
  )
  for _, block in ipairs(blocks) do
    result[#result + 1] = block
  end
  result[#result + 1] = pandoc.RawBlock("latex", "\\end{semanticpdfbox}")
  return result
end

local function biography_sources(div)
  local source = value(div.attributes.source)
  local source_label = value(div.attributes["source-label"])
  local photo_source = value(div.attributes["photo-source"])
  local photo_credit = value(div.attributes["photo-credit"])
  local inlines = {}

  if source ~= "" then
    inlines[#inlines + 1] = pandoc.Strong("Источник:")
    inlines[#inlines + 1] = pandoc.Space()
    inlines[#inlines + 1] = pandoc.Link(
      {pandoc.Str(source_label ~= "" and source_label or source)}, source
    )
  end
  if photo_source ~= "" then
    if #inlines > 0 then
      inlines[#inlines + 1] = pandoc.Str(";")
      inlines[#inlines + 1] = pandoc.Space()
    end
    inlines[#inlines + 1] = pandoc.Str("фото")
    inlines[#inlines + 1] = pandoc.Space()
    inlines[#inlines + 1] = pandoc.Link(
      {pandoc.Str(photo_credit ~= "" and photo_credit or "источник")},
      photo_source
    )
  elseif photo_credit ~= "" then
    if #inlines > 0 then
      inlines[#inlines + 1] = pandoc.Str(";")
      inlines[#inlines + 1] = pandoc.Space()
    end
    inlines[#inlines + 1] = pandoc.Str("фото:")
    inlines[#inlines + 1] = pandoc.Space()
    inlines[#inlines + 1] = pandoc.Str(photo_credit)
  end
  return inlines
end

local function render_biography(div)
  local name = value(div.attributes.name)
  local years = value(div.attributes.years)
  local photo_html = value(div.attributes.photo)
  local photo_fixed = project_path(div.attributes.photo)
  local photo_alt = value(div.attributes["photo-alt"])
  local photo_source = value(div.attributes["photo-source"])
  local sources = biography_sources(div)

  if FORMAT:match("html") or FORMAT:match("epub") then
    local photo = ""
    if photo_html ~= "" then
      local src = FORMAT:match("epub") and photo_fixed or photo_html
      local image = string.format(
        '<img class="biography-portrait" src="%s" alt="%s" />',
        html_escape(src), html_escape(photo_alt ~= "" and photo_alt or name)
      )
      if photo_source ~= "" then
        image = string.format(
          '<a href="%s" target="_blank" rel="noopener noreferrer">%s</a>',
          html_escape(photo_source), image
        )
      end
      photo = '<div class="biography-photo">' .. image .. '</div>'
    end

    local years_html = ""
    if years ~= "" then
      years_html = string.format(
        '<div class="biography-years">%s</div>', html_escape(years)
      )
    end
    local identifier = ""
    if div.identifier ~= "" then
      identifier = string.format(' id="%s"', html_escape(div.identifier))
    end
    local blocks = {
      pandoc.RawBlock(
        "html",
        '<div class="biography"' .. identifier .. '>' .. photo ..
        '<div class="biography-copy"><div class="biography-label">Биография</div>' ..
        '<div class="biography-name">' .. html_escape(name) .. '</div>' ..
        years_html
      )
    }
    for _, block in ipairs(div.content) do
      blocks[#blocks + 1] = block
    end
    if #sources > 0 then
      blocks[#blocks + 1] = pandoc.Div(
        {pandoc.Para(sources)}, pandoc.Attr("", {"biography-sources"})
      )
    end
    blocks[#blocks + 1] = pandoc.RawBlock("html", "</div></div>")
    return blocks
  end

  local blocks = {}
  if div.identifier ~= "" then
    blocks[#blocks + 1] = pandoc.RawBlock(
      "latex", "\\hypertarget{" .. div.identifier .. "}{}"
    )
  end
  blocks[#blocks + 1] = pandoc.RawBlock(
    "latex",
    "\\begin{semanticpdfbox}[colback=BookBiographySoft,borderline west={1.2mm}{0pt}{BookBiography},breakable=false]"
  )
  if photo_fixed ~= "" then
    blocks[#blocks + 1] = pandoc.RawBlock(
      "latex", "\\noindent\\begin{minipage}[t]{30mm}\\vspace{0pt}\\centering"
    )
    local image = pandoc.Image(
      {pandoc.Str(photo_alt ~= "" and photo_alt or name)}, photo_fixed, "",
      pandoc.Attr("", {"biography-portrait"}, {width = "28mm"})
    )
    if photo_source ~= "" then
      blocks[#blocks + 1] = pandoc.Para({pandoc.Link({image}, photo_source)})
    else
      blocks[#blocks + 1] = pandoc.Para({image})
    end
    blocks[#blocks + 1] = pandoc.RawBlock(
      "latex",
      "\\end{minipage}\\hfill\\begin{minipage}[t]{\\dimexpr\\linewidth-35mm\\relax}\\vspace{0pt}"
    )
  end
  blocks[#blocks + 1] = pandoc.RawBlock(
    "latex",
    "{\\sffamily\\bfseries\\footnotesize\\color{BookBiography} БИОГРАФИЯ\\par}" ..
    "\\vspace{0.8mm}{\\sffamily\\bfseries\\large\\color{BookInk} " ..
    latex_escape(name) .. "\\par}"
  )
  if years ~= "" then
    blocks[#blocks + 1] = pandoc.RawBlock(
      "latex",
      "{\\sffamily\\small\\color{BookMuted} " .. latex_escape(years) ..
      "\\par}\\vspace{1.4mm}"
    )
  end
  for _, block in ipairs(div.content) do
    blocks[#blocks + 1] = block
  end
  if #sources > 0 then
    blocks[#blocks + 1] = pandoc.RawBlock("latex", "{\\footnotesize\\color{BookMuted}")
    blocks[#blocks + 1] = pandoc.Para(sources)
    blocks[#blocks + 1] = pandoc.RawBlock("latex", "}")
  end
  if photo_fixed ~= "" then
    blocks[#blocks + 1] = pandoc.RawBlock("latex", "\\end{minipage}")
  end
  blocks[#blocks + 1] = pandoc.RawBlock("latex", "\\end{semanticpdfbox}")
  return blocks
end

local function render_animation(div)
  local title = value(div.attributes.title)
  local src = value(div.attributes.src)
  local epub_src = value(div.attributes["epub-src"])
  local poster_html = value(div.attributes.poster)
  local poster_fixed = project_path(div.attributes.poster)
  local url = value(div.attributes.url)
  local qr_fixed = project_path(div.attributes.qr)

  if FORMAT:match("html") or FORMAT:match("epub") then
    local browser_src = src
    local browser_poster = poster_html
    if FORMAT:match("epub") then
      browser_src = project_path(epub_src ~= "" and epub_src or src)
      browser_poster = poster_fixed
    end

    local media = ""
    if browser_src ~= "" then
      local poster = browser_poster ~= "" and
        string.format(' poster="%s"', html_escape(browser_poster)) or ""
      media = string.format(
        '<video controls="controls" loop="loop" muted="muted" playsinline="playsinline" preload="metadata"%s><source src="%s" type="video/mp4" /></video>',
        poster, html_escape(browser_src)
      )
    elseif url ~= "" then
      media = string.format(
        '<iframe class="animation-embed" src="%s" title="%s" loading="lazy" allowfullscreen="allowfullscreen"></iframe>',
        html_escape(url), html_escape(title)
      )
    elseif browser_poster ~= "" then
      media = string.format(
        '<img src="%s" alt="%s" />',
        html_escape(browser_poster), html_escape(title)
      )
    end

    local identifier = div.identifier ~= "" and
      string.format(' id="%s"', html_escape(div.identifier)) or ""
    local blocks = {
      pandoc.RawBlock("html", '<figure class="animation-block"' .. identifier .. '>' .. media)
    }
    for _, block in ipairs(div.content) do
      blocks[#blocks + 1] = block
    end
    if title ~= "" then
      blocks[#blocks + 1] = pandoc.RawBlock(
        "html", "<figcaption>" .. html_escape(title) .. "</figcaption>"
      )
    end
    blocks[#blocks + 1] = pandoc.RawBlock("html", "</figure>")
    return blocks
  end

  local blocks = {}
  if poster_fixed ~= "" then
    if FORMAT:match("latex") then
      blocks[#blocks + 1] = pandoc.RawBlock("latex", "\\begin{center}")
    end
    blocks[#blocks + 1] = pandoc.Para({
      pandoc.Image(
        {pandoc.Str(title)}, poster_fixed, title,
        pandoc.Attr("", {"animation-poster"}, {width = "74%"})
      )
    })
    if FORMAT:match("latex") then
      blocks[#blocks + 1] = pandoc.RawBlock("latex", "\\end{center}")
    end
  end

  local has_qr = qr_fixed ~= "" and url ~= ""
  if FORMAT:match("latex") and has_qr then
    blocks[#blocks + 1] = pandoc.RawBlock(
      "latex", "\\noindent\\begin{minipage}[c]{\\dimexpr\\linewidth-30mm\\relax}"
    )
  end
  if title ~= "" then
    blocks[#blocks + 1] = heading(title, "Интерактив")
  end
  for _, block in ipairs(div.content) do
    blocks[#blocks + 1] = block
  end
  if FORMAT:match("latex") and has_qr then
    blocks[#blocks + 1] = pandoc.RawBlock(
      "latex", "\\end{minipage}\\hfill\\begin{minipage}[c]{26mm}\\centering"
    )
  end
  if has_qr then
    blocks[#blocks + 1] = pandoc.Para({
      pandoc.Link({
        pandoc.Image(
          {pandoc.Str("QR-код интерактива")}, qr_fixed, "",
          pandoc.Attr("", {"animation-qr"}, {width = "24mm"})
        )
      }, url)
    })
  end
  if FORMAT:match("latex") and has_qr then
    blocks[#blocks + 1] = pandoc.RawBlock("latex", "\\end{minipage}")
  end

  if FORMAT:match("latex") then
    return latex_box(blocks, div.identifier, "[breakable=false]")
  end
  return pandoc.Div(
    blocks, pandoc.Attr(div.identifier, {"animation-block", "semantic-block"})
  )
end

local semantic_labels = {
  ["physical-comment"] = "Физический смысл",
  ["experimental-fact"] = "Экспериментальный факт",
  ["warning"] = "Важно"
}

function Div(div)
  if has_class(div, "biography") then
    return render_biography(div)
  end
  if has_class(div, "animation") then
    return render_animation(div)
  end
  if has_class(div, "book-lead") then
    add_class(div, "semantic-block")
    if FORMAT:match("latex") then
      return latex_box(div.content, div.identifier, "")
    end
    return div
  end
  for class, label in pairs(semantic_labels) do
    if has_class(div, class) then
      div.content:insert(1, heading(value(div.attributes.title), label))
      add_class(div, "semantic-block")
      if FORMAT:match("latex") then
        local options = ""
        if class == "experimental-fact" then
          options = "[colback=BookBlueSoft,borderline west={1.2mm}{0pt}{BookBlue}]"
        elseif class == "warning" then
          options = "[colback=BookCoralSoft,borderline west={1.2mm}{0pt}{BookCoral}]"
        end
        return latex_box(div.content, div.identifier, options)
      end
      return div
    end
  end
end

local inside_exercises = false
local exercise_box_open = false
local part_titles = {}

local function configure_book_profile(meta)
  local configured_titles = meta["book-part-titles"]
  if configured_titles then
    for _, item in ipairs(configured_titles) do
      part_titles[pandoc.utils.stringify(item)] = true
    end
  end
  return meta
end

local function close_exercise_box(blocks)
  if exercise_box_open and FORMAT:match("latex") then
    blocks[#blocks + 1] = pandoc.RawBlock("latex", "\\end{semanticpdfbox}")
    exercise_box_open = false
  end
end

function Header(header)
  local title = pandoc.utils.stringify(header.content)
  local prefix = {}

  if header.level == 1 then
    close_exercise_box(prefix)
    inside_exercises = false
  elseif header.level == 2 and title == "Задачи" then
    close_exercise_box(prefix)
    inside_exercises = true
  elseif inside_exercises and header.level == 2 and title:match("^Задача%s+%d+") then
    add_class(header, "unnumbered")
    add_class(header, "unlisted")
    add_class(header, "exercise-heading")
    if FORMAT:match("latex") then
      close_exercise_box(prefix)
      prefix[#prefix + 1] = pandoc.RawBlock(
        "latex",
        "\\begin{semanticpdfbox}[colback=BookCoralSoft,borderline west={1.2mm}{0pt}{BookCoral}]"
      )
      exercise_box_open = true
      local rendered = pandoc.write(
        pandoc.Pandoc({pandoc.Plain(header.content)}), "latex"
      ):gsub("%s+$", "")
      prefix[#prefix + 1] = pandoc.RawBlock(
        "latex",
        "\\noindent{\\sffamily\\bfseries\\fontsize{11.2}{13.5}\\selectfont " ..
        rendered .. "}\\par\\nopagebreak[4]\\vspace{1.2mm}"
      )
      return prefix
    end
    return header
  elseif inside_exercises and header.level == 2 then
    close_exercise_box(prefix)
    inside_exercises = false
  end

  if FORMAT:match("latex")
      and header.level == 1
      and header.identifier ~= ""
      and not part_titles[title]
      and not has_class(header, "unnumbered") then
    prefix[#prefix + 1] = header
    prefix[#prefix + 1] = pandoc.RawBlock("latex", "\\bookchapteropeningcontents")
    return prefix
  end

  if #prefix > 0 then
    prefix[#prefix + 1] = header
    return prefix
  end
  return header
end

function Pandoc(doc)
  if exercise_box_open and FORMAT:match("latex") then
    doc.blocks:insert(pandoc.RawBlock("latex", "\\end{semanticpdfbox}"))
    exercise_box_open = false
  end
  return doc
end

return {
  {Meta = configure_book_profile},
  {Div = Div, Header = Header, Pandoc = Pandoc}
}
