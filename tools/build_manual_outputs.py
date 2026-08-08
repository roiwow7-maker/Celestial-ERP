from __future__ import annotations

import argparse
import html
import re
import textwrap
from pathlib import Path


DEFAULT_INPUT = Path("docs/MANUAL_COMPLETO_CELESTIAL_ERP.md")
DEFAULT_HTML = Path("docs/Celestial_ERP_Manual_Completo.html")
DEFAULT_PDF = Path("docs/Celestial_ERP_Manual_Completo.pdf")


def markdown_to_html(markdown_text: str) -> str:
    lines = markdown_text.splitlines()
    output: list[str] = []
    in_code = False
    in_ul = False
    in_ol = False
    in_table = False

    def close_lists() -> None:
        nonlocal in_ul, in_ol
        if in_ul:
            output.append("</ul>")
            in_ul = False
        if in_ol:
            output.append("</ol>")
            in_ol = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            close_lists()
            if in_code:
                output.append("</code></pre>")
            else:
                output.append("<pre><code>")
            in_code = not in_code
            continue
        if in_code:
            output.append(html.escape(line))
            continue
        if not stripped:
            close_lists()
            if in_table:
                output.append("</tbody></table>")
                in_table = False
            continue
        if stripped.startswith("|") and stripped.endswith("|"):
            close_lists()
            cells = [html.escape(cell.strip()) for cell in stripped.strip("|").split("|")]
            if set(cells[0].replace("-", "")) == {""} if cells else False:
                continue
            if not in_table:
                output.append("<table><tbody>")
                in_table = True
            output.append("<tr>" + "".join(f"<td>{cell}</td>" for cell in cells) + "</tr>")
            continue
        if in_table:
            output.append("</tbody></table>")
            in_table = False
        heading = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if heading:
            close_lists()
            level = len(heading.group(1))
            output.append(f"<h{level}>{html.escape(heading.group(2))}</h{level}>")
            continue
        ordered = re.match(r"^\d+\.\s+(.*)$", stripped)
        if ordered:
            if not in_ol:
                close_lists()
                output.append("<ol>")
                in_ol = True
            output.append(f"<li>{html.escape(ordered.group(1))}</li>")
            continue
        if stripped.startswith("- "):
            if not in_ul:
                close_lists()
                output.append("<ul>")
                in_ul = True
            output.append(f"<li>{html.escape(stripped[2:])}</li>")
            continue
        close_lists()
        output.append(f"<p>{html.escape(stripped)}</p>")

    close_lists()
    if in_table:
        output.append("</tbody></table>")

    return "\n".join(output)


def build_html(markdown_path: Path, html_path: Path) -> None:
    body = markdown_to_html(markdown_path.read_text(encoding="utf-8"))
    document = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Manual completo Celestial ERP</title>
<style>
body {{
    font-family: Arial, Helvetica, sans-serif;
    color: #24303f;
    background: #f4f1ec;
    line-height: 1.5;
    margin: 0;
}}
main {{
    max-width: 980px;
    margin: 0 auto;
    padding: 42px 32px 72px;
    background: #fffdf9;
}}
h1, h2, h3 {{ color: #2f5260; }}
h1 {{ border-bottom: 3px solid #8db7c1; padding-bottom: 12px; }}
h2 {{ margin-top: 32px; border-bottom: 1px solid #d4ccc1; padding-bottom: 6px; }}
code, pre {{ background: #eef4f2; color: #24303f; }}
pre {{ padding: 12px; border: 1px solid #d4ccc1; border-radius: 6px; overflow-x: auto; }}
table {{ width: 100%; border-collapse: collapse; margin: 12px 0; }}
td, th {{ border: 1px solid #d4ccc1; padding: 8px; vertical-align: top; }}
@media print {{
    body {{ background: white; }}
    main {{ padding: 0; }}
    h1, h2 {{ break-after: avoid; }}
}}
</style>
</head>
<body>
<main>
{body}
</main>
</body>
</html>
"""
    html_path.write_text(document, encoding="utf-8")


def pdf_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def markdown_to_pdf_lines(markdown_text: str) -> list[str]:
    lines: list[str] = []
    in_code = False
    for raw in markdown_text.splitlines():
        stripped = raw.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if not stripped:
            lines.append("")
            continue
        if in_code:
            lines.extend(textwrap.wrap(raw, width=92, replace_whitespace=False) or [""])
            continue
        heading = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if heading:
            lines.append("")
            lines.append(heading.group(2).upper() if len(heading.group(1)) <= 2 else heading.group(2))
            lines.append("")
            continue
        if stripped.startswith("|"):
            normalized = " ".join(part.strip() for part in stripped.strip("|").split("|"))
            if set(normalized.replace(" ", "")) <= {"-"}:
                continue
            lines.extend(textwrap.wrap(normalized, width=92))
            continue
        lines.extend(textwrap.wrap(stripped, width=92) or [""])
    return lines


def write_pdf(lines: list[str], pdf_path: Path) -> None:
    page_width = 595
    page_height = 842
    margin_x = 48
    start_y = 790
    line_height = 14
    max_lines = 52
    pages = [lines[index : index + max_lines] for index in range(0, len(lines), max_lines)]
    objects: list[str] = []

    def add_object(content: str) -> int:
        objects.append(content)
        return len(objects)

    font_obj = add_object("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
    page_refs: list[int] = []
    content_refs: list[int] = []

    for page_lines in pages:
        stream_lines = ["BT", f"/F1 10 Tf", f"{margin_x} {start_y} Td", "14 TL"]
        for line in page_lines:
            safe = pdf_escape(line.encode("cp1252", errors="replace").decode("cp1252"))
            stream_lines.append(f"({safe}) Tj")
            stream_lines.append("T*")
        stream_lines.append("ET")
        stream = "\n".join(stream_lines)
        content_obj = add_object(f"<< /Length {len(stream.encode('cp1252'))} >>\nstream\n{stream}\nendstream")
        content_refs.append(content_obj)
        page_obj = add_object(
            f"<< /Type /Page /Parent 0 0 R /MediaBox [0 0 {page_width} {page_height}] "
            f"/Resources << /Font << /F1 {font_obj} 0 R >> >> /Contents {content_obj} 0 R >>"
        )
        page_refs.append(page_obj)

    pages_obj = add_object("placeholder")
    catalog_obj = add_object(f"<< /Type /Catalog /Pages {pages_obj} 0 R >>")
    kids = " ".join(f"{page} 0 R" for page in page_refs)
    objects[pages_obj - 1] = f"<< /Type /Pages /Kids [{kids}] /Count {len(page_refs)} >>"
    for page_obj in page_refs:
        objects[page_obj - 1] = objects[page_obj - 1].replace("/Parent 0 0 R", f"/Parent {pages_obj} 0 R")

    output = bytearray()
    output.extend(b"%PDF-1.4\n")
    offsets = [0]
    for index, content in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{index} 0 obj\n".encode("ascii"))
        output.extend(content.encode("cp1252", errors="replace"))
        output.extend(b"\nendobj\n")
    xref_offset = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root {catalog_obj} 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("ascii")
    )
    pdf_path.write_bytes(output)


def build_pdf(markdown_path: Path, pdf_path: Path) -> None:
    lines = markdown_to_pdf_lines(markdown_path.read_text(encoding="utf-8"))
    write_pdf(lines, pdf_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Genera HTML y PDF del manual completo Celestial ERP.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--html", type=Path, default=DEFAULT_HTML)
    parser.add_argument("--pdf", type=Path, default=DEFAULT_PDF)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    build_html(args.input, args.html)
    build_pdf(args.input, args.pdf)
    print(f"HTML generado: {args.html}")
    print(f"PDF generado: {args.pdf}")


if __name__ == "__main__":
    main()
