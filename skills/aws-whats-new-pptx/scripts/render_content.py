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
    - ## 개요 or ### 개요 → skipped (Row 0 header duplicate)
    - URLs (https://...) → clickable hyperlinks
    - {date} placeholder in slide → replaced via --date option
"""

import argparse
import re
import sys
from pathlib import Path

URL_PATTERN = re.compile(r'(https?://[^\s<>"]+)')
MD_LINK_PATTERN = re.compile(r'\[([^\]]+)\]\((https?://[^\s)]+)\)')
LINK_PATTERN = re.compile(
    r'\[([^\]]+)\]\((https?://[^\s)]+)\)'  # [text](url) markdown link
    r'|'
    r'(https?://[^\s<>"]+)'                 # bare URL
)

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
    """Split a line into text, markdown links, and bare URL segments."""
    parts = []
    last_end = 0

    for m in LINK_PATTERN.finditer(text):
        if m.start() > last_end:
            parts.append(_run(text[last_end:m.start()], sz, bold))

        rid = f'rId{100 + len(urls)}'
        if m.group(1) is not None:
            # Markdown link: [display](url)
            display, url = m.group(1), m.group(2)
        else:
            # Bare URL
            display = url = m.group(3)

        urls.append((rid, url))
        parts.append(_run(display, sz, bold, hlink_rid=rid))
        last_end = m.end()

    if last_end < len(text):
        parts.append(_run(text[last_end:], sz, bold))

    return ''.join(parts)


MAX_WIDTH_14PT = 135  # visual width units per line at 14pt (CJK=2, ASCII=1)
MAX_WIDTH_12PT = 157  # visual width units per line at 12pt
MAX_LINES_14PT = 23   # max visual lines at 14pt (measured from slide)
MAX_LINES_12PT = 27   # max visual lines at 12pt (proportional estimate)


def _visual_width(text):
    """Estimate visual width: CJK/fullwidth=2, ASCII/halfwidth=1."""
    return sum(2 if ord(ch) > 0x7F else 1 for ch in text)


def estimate_visual_lines(lines, max_width):
    """Estimate visual line count on slide, accounting for text wrapping."""
    import math
    total = 0
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('유형:'):
            continue
        if not stripped:
            total += 1
        else:
            total += max(1, math.ceil(_visual_width(stripped) / max_width))
    return total


def determine_font_size(lines):
    """Auto-determine font size and split need based on visual line count."""
    if estimate_visual_lines(lines, MAX_WIDTH_14PT) <= MAX_LINES_14PT:
        return 1400, False
    if estimate_visual_lines(lines, MAX_WIDTH_12PT) <= MAX_LINES_12PT:
        return 1200, False
    return 1400, True  # needs split into 2 slides


def extract_date(lines):
    """Extract and remove '게시일:' line and trailing blank line from content."""
    date_text = None
    remaining = []
    skip_next_blank = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('게시일:'):
            date_text = stripped.replace('게시일:', '').strip()
            skip_next_blank = True
        elif skip_next_blank and not stripped:
            skip_next_blank = False
        else:
            skip_next_blank = False
            remaining.append(line)
    return date_text, remaining


def render_txbody(lines, sz):
    """Convert content lines to XML <a:txBody> for Row 1."""
    # Strip leading 유형: lines and blank lines to prevent empty <a:br> at top
    while lines and (not lines[0].strip() or lines[0].strip().startswith('유형:')):
        lines.pop(0)

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
            if text in ('개요', '상세 내용'):
                continue
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

    # Remove trailing BR after last content line
    if parts[-1].startswith('<a:br>'):
        parts.pop()

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


def replace_date(slide_content, date_text):
    """Replace '{date}' placeholder in slide."""
    return slide_content.replace('<a:t>{date}</a:t>', f'<a:t>{_escape(date_text)}</a:t>', 1)


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


def replace_script(slide_xml_path, script_text):
    """Replace {script} placeholder in the linked notesSlide."""
    path = Path(slide_xml_path)
    rels_path = path.parent / '_rels' / f'{path.name}.rels'
    if not rels_path.exists():
        return False

    rels_content = rels_path.read_text(encoding='utf-8')
    m = re.search(r'Target="([^"]*notesSlide[^"]*)"', rels_content)
    if not m:
        return False

    notes_path = (path.parent / m.group(1)).resolve()
    if not notes_path.exists():
        return False

    notes_content = notes_path.read_text(encoding='utf-8')
    if '{script}' not in notes_content:
        return False

    escaped = _escape(script_text).replace('\n', '&#xA;')
    notes_content = notes_content.replace('<a:t>{script}</a:t>', f'<a:t>{escaped}</a:t>')
    notes_path.write_text(notes_content, encoding='utf-8')
    print(f'Script inserted into {notes_path.name}')
    return True


def render_slide(slide_path, lines, font_size='auto', title=None, header=None, date=None, script=None):
    """One-shot render: title + header + date + Row 1 content + hyperlinks."""
    path = Path(slide_path)
    content = path.read_text(encoding='utf-8')

    # Extract date from content first (removes 게시일 line + trailing blank)
    extracted_date, lines = extract_date(lines)
    date_value = date or extracted_date

    if font_size == 'auto':
        sz, needs_split = determine_font_size(lines)
    else:
        sz, needs_split = int(font_size), False

    if needs_split:
        vl = estimate_visual_lines(lines, MAX_WIDTH_14PT)
        print(f'SPLIT_NEEDED: {vl} visual lines (14pt max {MAX_LINES_14PT}, 12pt max {MAX_LINES_12PT})')
        return False, sz, True

    if title:
        content = replace_title(content, title)

    if header:
        content = replace_header(content, header)

    if date_value:
        content = replace_date(content, date_value)

    txbody, urls = render_txbody(lines, sz)
    result = replace_row1(content, txbody)
    if result is None:
        print(f'Error: Could not find Row 1 <a:txBody> in {slide_path}', file=sys.stderr)
        return False, sz, False

    path.write_text(result, encoding='utf-8')
    register_hyperlinks(path, urls)

    if script:
        replace_script(path, script)

    non_empty = len([l for l in lines if l.strip() and not l.strip().startswith('유형:')])
    vl = estimate_visual_lines(lines, MAX_WIDTH_14PT if sz == 1400 else MAX_WIDTH_12PT)
    print(f'Rendered {non_empty} lines ({vl} visual) at {sz / 100:.0f}pt into {path.name}'
          f' ({len(urls)} hyperlinks)')
    return True, sz, False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='One-shot PPTX content slide renderer')
    parser.add_argument('slide_xml', help='Path to slide XML file')
    parser.add_argument('content_file', nargs='?', default='-',
                        help='Content file path, or - for stdin (default: stdin)')
    parser.add_argument('--title', help='Slide title (replaces {Title})')
    parser.add_argument('--header', default='개요', help='Row 0 header text (default: 개요)')
    parser.add_argument('--font-size', default='auto',
                        help='Font size: auto, 1400 (14pt), or 1200 (12pt)')
    parser.add_argument('--date', help='Date text (replaces {date} placeholder)')
    parser.add_argument('--script', help='Script file for presenter notes (replaces {script})')
    args = parser.parse_args()

    if args.content_file == '-':
        lines = sys.stdin.read().splitlines()
    else:
        lines = Path(args.content_file).read_text(encoding='utf-8').splitlines()

    script_text = None
    if args.script:
        script_text = Path(args.script).read_text(encoding='utf-8')

    ok, sz, needs_split = render_slide(args.slide_xml, lines, args.font_size, args.title, args.header, args.date, script_text)
    if needs_split:
        sys.exit(2)
    if not ok:
        sys.exit(1)
