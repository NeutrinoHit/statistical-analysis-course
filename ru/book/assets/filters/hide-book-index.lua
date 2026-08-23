local book_title = "Статистический анализ данных"

function Header(header)
  local is_book_index = header.level == 1
    and pandoc.utils.stringify(header.content) == book_title
  local combined_format = FORMAT:match("latex") or FORMAT:match("epub")

  if is_book_index and combined_format then
    return {}
  end
end
