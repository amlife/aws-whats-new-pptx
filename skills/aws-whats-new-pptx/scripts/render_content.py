"""Render markdown summary into a PPTX content slide.

One-shot slide renderer: replaces Title, Row 0 header, and Row 1 body
in a single call. Supports hyperlinks, auto font-size, and stdin input.

Usage:
    python render_content.py <slide_xml> [content_file] [options]

    # Render from file with auto font-size
    python render_content.py working/ppt/slides/slide2.xml content.dat \\
        --title "Amazon RDS 업데이트" --header "개요" --font-size auto

    # Render from stdin
    echo "content" | python render_content.py slide2.xml - --title "제목"

Content format:
    - **bold text** → bold run
    - ## or ### heading → bold run (markers stripped)
    - • bullet text → bullet point
    - - bullet text → bullet point (converted to •)
    - empty line → blank line
    - Lines starting with "유형:" → skipped (internal metadata)
    - URLs (https://...) → clickable hyperlinks
"""

import argparse
import re
import sys
from pathlib import Path

URL_PATTERN = re.compile(r'(https?://[^\s<>"]+)')

EMBER_FONTS = (
    '<a:latin typeface="Amazon Ember" panose="020B0603020204020204" pitchFamily="34" charset="0"/>'
    '<a:ea typeface="Amazon Ember" panose="020B0603020204020204" pitchFamily="34" charset="0"/>'
    '<a:cs typeface="Amazon Ember" panose="020B0603020204020204" pitchFamily="34" charset="0"/>'
)


def _escape(text):
    return (
        text.replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
        .replace('"', '&quot;')
        .replace('\u2019', '&#x2019;')
        .replace('\u201C', '&#x201C;')
        .replace('\u201D', '&#x201D;')
    )


def _rpr(sz, bold=False, hlink_rid=None):
    b = ' b="1"' if bold else ''
    hlink = f'<a:hlinkClick xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" r:id="{hlink_rid}"/>' if hlink_rid else ''
    return f'<a:rPr lang="ko-KR" sz="{sz}"{b} dirty="0">{hlink}{EMBER_FONTS}</a:rPr>'


def _br(sz):
    return f'<a:br>{_rpr(sz)}</a:br>'


def _run(text, sz, bold=False, hlink_rid=None):
    return f'<a:r>{_rpr(sz, bold, hlink_rid)}<a:t>{_escape(text)}</a:t></a:r>'


def _render_line_with_links(text, sz, bold, urls):
    """Split a line into text and URL segments, creating hyperlink runs for URLs."""
    parts = []
    last_end = 0

    for m in URL_PATTERN.finditer(text):
        if m.start() > last_end:
            parts.append(_run(text[last_end:m.start()], sz, bold))

        url = m.group(0)
        rid = f'rId{100 + len(urls)}'
        urls.append((rid, url))
        parts.append(_run(url, sz, bold, hlink_rid=rid))
        last_end = m.end()

    if last_end < len(text):
        parts.append(_run(text[last_end:], sz, bold))

    return ''.join(parts)


def determine_font_size(lines):
    """Auto-determine font size based on content line count."""
    count = len([l for l in lines if l.strip()])
    if count <= 25:
        return 1400
    if count <= 35:
        return 1200
    return 1400  # >35 lines: use 14pt with 2-slide split (handled externally)


def render_txbody(lines, sz):
    """Convert content lines to XML <a:txBody> for Row 1."""
    parts = ['<a:txBody><a:bodyPr/><a:lstStyle/><a:p>']
    urls = []

    for line in lines:
        stripped = line.strip()

        if not stripped:
            parts.append(_br(sz))
            continue

        if stripped.startswith('유형:'):
            continue

        if stripped.startswith('##'):
            text = stripped.lstrip('#').strip()
            parts.append(_render_line_with_links(text, sz, bold=True, urls=urls))
            parts.append(_br(sz))
        elif stripped.startswith('**') and stripped.endswith('**'):
            text = stripped[2:-2]
            parts.append(_render_line_with_links(text, sz, bold=True, urls=urls))
            parts.append(_br(sz))
        elif stripped.startswith('- '):
            text = '• ' + stripped[2:]
            parts.append(_render_line_with_links(text, sz, bold=False, urls=urls))
            parts.append(_br(sz))
        else:
            parts.append(_render_line_with_links(stripped, sz, bold=False, urls=urls))
            parts.append(_br(sz))

    parts.append(f'<a:endParaRPr lang="ko-KR" sz="{sz}" dirty="0">{EMBER_FONTS}</a:endParaRPr>')
    parts.append('</a:p></a:txBody>')
    return ''.join(parts), urls


def replace_row1(slide_content, new_txbody):
    """Replace Row 1 <a:txBody> in slide XML content string."""
    for pattern in [
        re.compile(
            r'<a:txBody>\s*<a:bodyPr/>\s*<a:lstStyle/>\s*<a:p>\s*'
            r'<a:endParaRPr[^/]*/>\s*</a:p>\s*</a:txBody>',
            re.DOTALL
        ),
        re.compile(
            r'<a:txBody>\s*<a:bodyPr/>\s*<a:lstStyle/>\s*<a:p>\s*'
            r'<a:endParaRPr[^>]*>.*?</a:endParaRPr>\s*</a:p>\s*</a:txBody>',
            re.DOTALL
        ),
        re.compile(
            r'<a:txBody><a:bodyPr/><a:lstStyle/><a:p>.*?</a:p></a:txBody>',
            re.DOTALL
        ),
    ]:
        match = pattern.search(slide_content)
        if match:
            return slide_content[:match.start()] + new_txbody + slide_content[match.end():]
    return None


def replace_title(slide_content, title):
    """Replace {Title} placeholder in Title shape."""
    return re.sub(r'<a:t>\{Title\}</a:t>', f'<a:t>{_escape(title)}</a:t>', slide_content)


def replace_header(slide_content, header):
    """Replace '개요' in Row 0 header."""
    return slide_content.replace('<a:t>개요</a:t>', f'<a:t>{_escape(header)}</a:t>', 1)


def register_hyperlinks(slide_xml_path, urls):
    """Add hyperlink Relationships to the slide's _rels file."""
    if not urls:
        return

    rels_path = slide_xml_path.parent / '_rels' / f'{slide_xml_path.name}.rels'
    if not rels_path.exists():
        return

    rels_content = rels_path.read_text(encoding='utf-8')
    hlink_type = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink'

    for rid, url in urls:
        if rid not in rels_content:
            new_rel = f'<Relationship Id="{rid}" Type="{hlink_type}" Target="{_escape(url)}" TargetMode="External"/>'
            rels_content = rels_content.replace('</Relationships>', f'  {new_rel}\n</Relationships>')

    rels_path.write_text(rels_content, encoding='utf-8')


def render_slide(slide_path, lines, font_size='auto', title=None, header=None):
    """One-shot render: title + header + Row 1 content + hyperlinks."""
    path = Path(slide_path)
    content = path.read_text(encoding='utf-8')

    sz = determine_font_size(lines) if font_size == 'auto' else int(font_size)

    if title:
        content = replace_title(content, title)

    if header:
        content = replace_header(content, header)

    txbody, urls = render_txbody(lines, sz)
    result = replace_row1(content, txbody)
    if result is None:
        print(f'Error: Could not find Row 1 <a:txBody> in {slide_path}', file=sys.stderr)
        return False, sz

    path.write_text(result, encoding='utf-8')
    register_hyperlinks(path, urls)

    non_empty = len([l for l in lines if l.strip() and not l.strip().startswith('유형:')])
    print(f'Rendered {non_empty} lines at {sz / 100:.0f}pt into {path.name}'
          f' ({len(urls)} hyperlinks)')
    return True, sz


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='One-shot PPTX content slide renderer')
    parser.add_argument('slide_xml', help='Path to slide XML file')
    parser.add_argument('content_file', nargs='?', default='-',
                        help='Content file path, or - for stdin (default: stdin)')
    parser.add_argument('--title', help='Slide title (replaces {Title})')
    parser.add_argument('--header', default='개요', help='Row 0 header text (default: 개요)')
    parser.add_argument('--font-size', default='auto',
                        help='Font size: auto, 1400 (14pt), or 1200 (12pt)')
    args = parser.parse_args()

    if args.content_file == '-':
        lines = sys.stdin.read().splitlines()
    else:
        lines = Path(args.content_file).read_text(encoding='utf-8').splitlines()

    ok, sz = render_slide(args.slide_xml, lines, args.font_size, args.title, args.header)
    if not ok:
        sys.exit(1)
