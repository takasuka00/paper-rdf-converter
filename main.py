import re
import time
from typing import List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path

import pyperclip


@dataclass
class PaperInfo:
    """学術論文の情報を格納するデータクラス"""
    title: str
    conference_title: str
    pages: str
    date: str
    authors: List[Tuple[str, str]]  # (姓, 名)のタプルのリスト
    doi: Optional[str] = None


# オリジナルのタグデコレーター実装
indent = "    "


def tag(tag_name, meta="", last='\n'):
    """XMLタグを作成するデコレーター"""
    if meta != "":
        meta = " " + meta

    def _tag(f):
        def _wrapper(*args, **keywords):
            v = f(*args, **keywords)
            # 受け取った文字列の各行にインデントを追加
            indented_content = ""
            for line in v.split('\n'):
                indented_content += f"{indent}{line}\n"
            indented_content = indented_content.rstrip()  # 最後の余分な改行を削除
            if last != '\n':
                indented_content = indented_content.lstrip()
            return f'<{tag_name}{meta}>{last}{indented_content}{last}</{tag_name}>'

        return _wrapper

    return _tag


class RDFGenerator:
    """RDF形式のXMLを生成するクラス（デコレーター使用版）"""

    DEFAULT_TAGS = ["Domestic Conference", "Reha"]

    @tag("rdf:RDF", meta="""xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
 xmlns:z="http://www.zotero.org/namespaces/export#"
 xmlns:dcterms="http://purl.org/dc/terms/"
 xmlns:dc="http://purl.org/dc/elements/1.1/"
 xmlns:bib="http://purl.org/net/biblio#"
 xmlns:foaf="http://xmlns.com/foaf/0.1/" """)
    @tag("rdf:Description", "rdf:about=\"#item_100000\"")
    def generate_rdf(self, title, conference_title, pages, date, author_list, doi):
        """RDF形式のXMLを生成"""
        tag_string = ""
        for tag_item in self.DEFAULT_TAGS:
            tag_string += f"<dc:subject>{tag_item}</dc:subject>\n"

        doi_string = ""
        if doi is not None:
            doi_string = f"<dc:identifier>DOI {doi}</dc:identifier>\n"

        return ("<z:itemType>conferencePaper</z:itemType>\n"
                + self.journal(conference_title) + "\n"
                + self.authors(author_list) + "\n"
                + tag_string
                + f"<dc:title>{title}</dc:title>\n"
                + f"<dc:date>{date}</dc:date>\n"
                + doi_string
                + "<dc:description></dc:description>\n"
                + f"<bib:pages>{pages}</bib:pages>\n"
                + self.conference(conference_title)
                )

    @tag("dcterms:isPartOf")
    @tag("bib:Journal")
    @tag("dc:title", last="")
    def journal(self, conference_title):
        """ジャーナル情報を生成"""
        return f"{conference_title}"

    @tag("rdf:li")
    @tag("foaf:Person")
    def author(self, name):
        """個別の著者情報を生成"""
        return f"{self.author_surname(name[1])}\n{self.author_given_name(name[0])}"

    @tag("foaf:surname",last="")
    def author_surname(self, name):
        """著者の姓を生成"""
        return name

    @tag("foaf:givenName",last="")
    def author_given_name(self, name):
        """著者の名を生成"""
        return name

    @tag("bib:authors")
    @tag("rdf:Seq")
    def authors(self, name_list):
        """著者リストを生成"""
        s = ""
        for name in name_list:
            s += self.author(name)
        return s

    @tag("bib:presentedAt")
    @tag("bib:Conference")
    @tag("dc:title")
    def conference(self, title):
        """カンファレンス情報を生成"""
        return f"{title}"

    def generate(self, paper: PaperInfo) -> str:
        """PaperInfoからRDFを生成"""
        return self.generate_rdf(
            paper.title,
            paper.conference_title,
            paper.pages,
            paper.date,
            paper.authors,
            paper.doi
        )


class PaperInfoParser:
    """文字列から論文情報を解析するクラス"""

    @staticmethod
    def parse(text: str) -> PaperInfo:
        """テキストから論文情報を解析"""
        lines = text.strip().split("\n")
        if len(lines) < 3:
            raise ValueError("入力テキストの形式が正しくありません")

        authors_line = lines[0]
        title = lines[1].strip()
        other_info = lines[2].strip()
        doi = PaperInfoParser._extract_doi(lines[3:])

        authors = PaperInfoParser._parse_authors(authors_line)
        conference_title, pages, date = PaperInfoParser._parse_other_info(other_info)

        return PaperInfo(
            title=title,
            conference_title=conference_title,
            pages=pages,
            date=date,
            authors=authors,
            doi=doi
        )

    @staticmethod
    def _extract_doi(remaining_lines: List[str]) -> Optional[str]:
        """DOI情報を抽出"""
        if not remaining_lines:
            return None

        doi_line = remaining_lines[0]
        if doi_line.startswith("DOI:"):
            return doi_line[4:].strip()
        return None

    @staticmethod
    def _parse_authors(authors_line: str) -> List[Tuple[str, str]]:
        """著者情報を解析"""
        # "and "を除去
        cleaned_authors = authors_line.replace("and ", "")

        # 区切り文字で分割
        author_elements = PaperInfoParser._split_by_pattern(r"(，|, |,|， )", cleaned_authors)

        authors = []
        for author_elem in author_elements:
            author_elem = author_elem.strip()
            name_parts = PaperInfoParser._split_by_pattern(r" ", author_elem)

            if len(name_parts) >= 2:
                last_name, first_name = name_parts[0], name_parts[1]
            else:
                last_name, first_name = name_parts[0], ""

            authors.append((first_name, last_name))

        return authors

    @staticmethod
    def _parse_other_info(other_info: str) -> Tuple[str, str, str]:
        """その他の情報（カンファレンス、ページ、日付）を解析"""
        elements = PaperInfoParser._split_by_pattern(r'(,|, |，)', other_info)

        if len(elements) == 4:
            conference_title, pages_elem, _, date_elem = elements[:4]
        else:
            conference_title = ",".join(elements[:-3])
            pages_elem = elements[-3]
            date_elem = elements[-1]

        pages = re.sub(r"pp\.( )*", "", pages_elem)
        date = PaperInfoParser._normalize_date(date_elem)

        return conference_title.strip(), pages.strip(), date

    @staticmethod
    def _normalize_date(date_elem: str) -> str:
        """日付を正規化"""
        date_part = date_elem.split("-")[0]
        return re.sub(r"[年月]", "-", date_part.replace("日", ""))

    @staticmethod
    def _split_by_pattern(pattern: str, text: str) -> List[str]:
        """パターンで分割し、空要素とパターンマッチを除去"""
        return [t for t in re.split(pattern, text) if t and not re.fullmatch(pattern, t)]


class FileManager:
    """ファイル操作を管理するクラス"""

    @staticmethod
    def save_rdf(rdf_content: str, filename: str) -> None:
        """RDFコンテンツをファイルに保存"""
        filepath = Path(filename)
        try:
            filepath.write_text(rdf_content, encoding='utf-8')
            print(f"正常に保存されました: {filename}")
        except Exception as e:
            print(f"ファイル保存エラー: {e}")

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """ファイル名を安全な形式にサニタイズ"""
        # 無効な文字を除去
        invalid_chars = r'[<>:"/\\|?*\r\n]'
        sanitized = re.sub(invalid_chars, '', filename)
        # 末尾のピリオドやスペースを除去
        sanitized = sanitized.strip('. ')
        return sanitized or "untitled"


class ClipboardMonitor:
    """クリップボードを監視するクラス"""

    def __init__(self, check_interval: float = 0.5):
        self.check_interval = check_interval
        self.rdf_generator = RDFGenerator()
        self.parser = PaperInfoParser()
        self.file_manager = FileManager()

    def start_monitoring(self) -> None:
        """クリップボード監視を開始"""
        print("クリップボード監視を開始しました。")
        count = 0
        last_clipboard = pyperclip.paste()

        try:
            while True:
                current_clipboard = pyperclip.paste()

                if current_clipboard != last_clipboard:
                    last_clipboard = current_clipboard
                    count += 1
                    self._process_clipboard_content(current_clipboard, count)

                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            print("\nクリップボード監視を終了しました。")

    def _process_clipboard_content(self, content: str, count: int) -> None:
        """クリップボードの内容を処理"""
        try:
            paper_info = self.parser.parse(content)
            rdf_content = self.rdf_generator.generate(paper_info)

            safe_title = self.file_manager.sanitize_filename(paper_info.title)
            filename = f"{count}_{safe_title}.rdf"

            self.file_manager.save_rdf(rdf_content, filename)

        except Exception as e:
            print(f"処理エラー: {e}")


def main():
    """メイン関数"""
    monitor = ClipboardMonitor()
    monitor.start_monitoring()


if __name__ == '__main__':
    main()