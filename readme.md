# Academic Paper RDF Converter

📝 学術論文の情報をクリップボードから自動検出し、RDF形式に変換するPythonツール

## 概要

Academic Paper RDF Converterは、学術論文の書誌情報をクリップボードから監視し、自動的にRDF/XML形式に変換してファイルに保存するツールです。ZoteroなどのBibliography管理システムでの利用を想定しています。

## 必要な環境

- Python 3.7+
- 必要なパッケージ：
  - `pyperclip`

## インストール

1. リポジトリをクローン：
```bash
git clone https://github.com/yourusername/academic-paper-rdf-converter.git
cd academic-paper-rdf-converter
```

2. 必要なパッケージをインストール：
```bash
pip install pyperclip
```

## 使用方法

### 基本的な使用方法

1. プログラムを実行：
```bash
python main.py
```

2. 以下の形式で学術論文の情報をクリップボードにコピー：
```
田中太郎, 佐藤花子, 山田次郎
深層学習を用いた自然言語処理手法の改良
第30回人工知能学会全国大会, pp.123-126, 2024年6月
DOI:10.1234/example.2024.123
```

3. 自動的にRDFファイルが生成されます（例：`1_深層学習を用いた自然言語処理手法の改良.rdf`）

### 入力形式

クリップボードにコピーするテキストは以下の形式に従ってください：

```
著者1, 著者2, 著者3          # 1行目：著者情報
論文タイトル                  # 2行目：論文タイトル
カンファレンス名, ページ, 日付  # 3行目：その他の情報
DOI:10.1234/example.doi      # 4行目：DOI（オプション）
```

#### 著者名の形式
- カンマ区切りで複数著者を記載
- 「姓 名」の順序で記載
- 「and」は自動的に除去されます

#### 日付の形式
- 「YYYY年MM月DD日」形式
- 「YYYY-MM-DD」形式
- その他の一般的な日付形式

## 出力例

入力：
```
田中太郎, 佐藤花子
機械学習による画像認識の高精度化
コンピュータビジョンとパターン認識会議, pp.45-52, 2024年3月15日
DOI:10.1109/CVPR.2024.12345
```

出力RDFファイル：
```xml
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
 xmlns:z="http://www.zotero.org/namespaces/export#"
 xmlns:dcterms="http://purl.org/dc/terms/"
 xmlns:dc="http://purl.org/dc/elements/1.1/"
 xmlns:bib="http://purl.org/net/biblio#"
 xmlns:foaf="http://xmlns.com/foaf/0.1/" >
    <rdf:Description rdf:about="#item_100000">
        <z:itemType>conferencePaper</z:itemType>
        <!-- その他のRDF要素 -->
    </rdf:Description>
</rdf:RDF>
```

## 設定のカスタマイズ

### デフォルトタグの変更

`DEFAULT_TAGS`を編集：

```python
DEFAULT_TAGS = ["Your Tag", "Another Tag"]
```

### クリップボード監視間隔の変更

```python
monitor = ClipboardMonitor(check_interval=1.0)  # 1秒間隔
```

## プロジェクト構造

```
academic-paper-rdf-converter/
├── main.py               # メインプログラム
├── README.md             # このファイル
└── requirements.txt      # 依存関係
```

## 技術的詳細

### アーキテクチャ

- **PaperInfo**: 論文情報を格納するデータクラス
- **RDFTagBuilder**: XMLタグ構築用ユーティリティ
- **RDFGenerator**: RDF/XML生成エンジン
- **PaperInfoParser**: テキスト解析エンジン
- **FileManager**: ファイル操作管理
- **ClipboardMonitor**: クリップボード監視システム

### 対応する書誌情報形式

- IEEE形式
- ACM形式
- 日本の学会形式
- その他の一般的な学術論文形式

## トラブルシューティング

### よくある問題

**Q: クリップボード監視が動作しない**
- A: `pyperclip`が正しくインストールされているか確認してください

**Q: 日本語のファイル名が文字化けする**
- A: システムの文字エンコーディングを確認してください

**Q: DOIが正しく解析されない**
- A: DOI行が「DOI:」で始まっているか確認してください

### エラーメッセージ

- `処理エラー: 入力テキストの形式が正しくありません` → 入力形式を確認
- `ファイル保存エラー:` → ファイル権限またはディスク容量を確認

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。


## 謝辞

- [pyperclip](https://pypi.org/project/pyperclip/) - クリップボード操作ライブラリ
- [Zotero](https://www.zotero.org/) - 参考文献管理システム