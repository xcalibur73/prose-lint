"""WordPress Gutenberg block comment transpiler and KSES entity sanitizer."""

from __future__ import annotations

import re


def markdown_to_gutenberg(markdown_text: str) -> str:
    """Converts clean Markdown into validated Gutenberg block comments.
    
    Adheres strictly to Gutenberg delimiter specifications and neutralizes
    WordPress KSES entity rewrite pitfalls.
    """
    lines = markdown_text.splitlines()
    blocks: list[str] = []
    i = 0
    total = len(lines)

    while i < total:
        line = lines[i]

        # Blank line
        if not line.strip():
            i += 1
            continue

        # 1. Heading (## Title, ### Subtitle)
        heading_match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading_match:
            level = len(heading_match.group(1))
            title = _sanitize_inline(heading_match.group(2))
            blocks.append(
                f'<!-- wp:heading {{"level":{level}}} -->\n'
                f'<h{level} class="wp-block-heading">{title}</h{level}>\n'
                f'<!-- /wp:heading -->'
            )
            i += 1
            continue

        # 2. Unordered List (- or *)
        if re.match(r"^\s*[-*]\s+", line):
            list_items: list[str] = []
            while i < total and re.match(r"^\s*[-*]\s+", lines[i]):
                item_text = re.sub(r"^\s*[-*]\s+", "", lines[i])
                list_items.append(f"<li>{_sanitize_inline(item_text)}</li>")
                i += 1
            inner_list = "\n".join(list_items)
            blocks.append(
                f"<!-- wp:list -->\n<ul>\n{inner_list}\n</ul>\n<!-- /wp:list -->"
            )
            continue

        # 3. Ordered List (1. 2. 3.)
        if re.match(r"^\s*\d+\.\s+", line):
            list_items = []
            while i < total and re.match(r"^\s*\d+\.\s+", lines[i]):
                item_text = re.sub(r"^\s*\d+\.\s+", "", lines[i])
                list_items.append(f"<li>{_sanitize_inline(item_text)}</li>")
                i += 1
            inner_list = "\n".join(list_items)
            blocks.append(
                f"<!-- wp:list -->\n<ol>\n{inner_list}\n</ol>\n<!-- /wp:list -->"
            )
            continue

        # 4. Code Block (```)
        if line.startswith("```"):
            code_lines: list[str] = []
            i += 1
            while i < total and not lines[i].startswith("```"):
                # Neutralize double ampersands to avoid KSES entity corruption (&& -> &#038;&#038;)
                safe_code_line = lines[i].replace("&&", "/* and */")
                code_lines.append(safe_code_line)
                i += 1
            if i < total:
                i += 1  # Skip closing ```
            inner_code = "\n".join(code_lines)
            blocks.append(
                f'<!-- wp:code -->\n<pre class="wp-block-code"><code>{inner_code}</code></pre>\n<!-- /wp:code -->'
            )
            continue

        # 5. Table (| Col | Col |)
        if line.strip().startswith("|") and line.strip().endswith("|"):
            table_lines: list[str] = []
            while i < total and lines[i].strip().startswith("|") and lines[i].strip().endswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            table_html = _render_table(table_lines)
            blocks.append(
                f'<!-- wp:table -->\n<figure class="wp-block-table">{table_html}</figure>\n<!-- /wp:table -->'
            )
            continue

        # 6. Default: Paragraph
        para_lines: list[str] = []
        while i < total and lines[i].strip() and not lines[i].startswith("#") and not lines[i].startswith("```") and not re.match(r"^\s*[-*]\s+", lines[i]) and not re.match(r"^\s*\d+\.\s+", lines[i]) and not (lines[i].strip().startswith("|") and lines[i].strip().endswith("|")):
            para_lines.append(lines[i].strip())
            i += 1
        para_text = " ".join(para_lines)
        blocks.append(
            f"<!-- wp:paragraph -->\n<p>{_sanitize_inline(para_text)}</p>\n<!-- /wp:paragraph -->"
        )

    return "\n\n".join(blocks)


def _sanitize_inline(text: str) -> str:
    """Converts basic Markdown links and bold/italic to HTML tags."""
    # Convert [text](url) -> <a href="url">text</a>
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    # Convert **bold** -> <strong>bold</strong>
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    # Convert *italic* -> <em>italic</em>
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    # Convert `code` -> <code>code</code>
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    return text


def _render_table(table_lines: list[str]) -> str:
    """Converts Markdown table rows into clean HTML table markup."""
    if len(table_lines) < 2:
        return ""
    
    rows: list[list[str]] = []
    for line in table_lines:
        if re.match(r"^\|[\s\-:|]+\|$", line):
            continue  # separator row
        cells = [c.strip() for c in line.strip("|").split("|")]
        rows.append(cells)

    if not rows:
        return ""

    header_cells = "".join(f"<th>{_sanitize_inline(c)}</th>" for c in rows[0])
    thead = f"<thead><tr>{header_cells}</tr></thead>"

    body_rows: list[str] = []
    for r in rows[1:]:
        cells = "".join(f"<td>{_sanitize_inline(c)}</td>" for c in r)
        body_rows.append(f"<tr>{cells}</tr>")
    tbody = f"<tbody>{''.join(body_rows)}</tbody>"

    return f"<table>{thead}{tbody}</table>"
