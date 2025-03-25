import re
import time

import pyperclip

indent = "    "
def tag(tag_name, meta = ""):
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
            return f'<{tag_name}{meta}>\n{indented_content}\n</{tag_name}>'
        return _wrapper
    return _tag

@tag("rdf:RDF",meta="""xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
 xmlns:z="http://www.zotero.org/namespaces/export#"
 xmlns:dcterms="http://purl.org/dc/terms/"
 xmlns:dc="http://purl.org/dc/elements/1.1/"
 xmlns:bib="http://purl.org/net/biblio#"
 xmlns:foaf="http://xmlns.com/foaf/0.1/" """)
@tag("rdf:Description","rdf:about=\"#item_10000\"")
def RDF(title, conferenceTitle, pages, date,authorList):
    return ("<z:itemType>conferencePaper</z:itemType>"
            + Journal(conferenceTitle)
            + authors(authorList)
            + "<dc:subject>Domestic Conference</dc:subject>"
            + "<dc:subject>Reha</dc:subject>"
            +  f"<dc:title>{title}</dc:title>"
            +  f"<dc:date>{date}</dc:date>"
            +  "<dc:description></dc:description>"
            +  f"<bib:pages>{pages}</bib:pages>"
            + Conference(conferenceTitle)
            )



@tag("dcterms:isPartOf")
@tag("bib:Journal")
def Journal(kiyou):
    return  f"<dc:title>{kiyou}</dc:title>"

@tag("rdf:li")
@tag("foaf:Person")
def autor(name):
    return f"<foaf:surname>{name[1]}</foaf:surname>\n<foaf:givenName>{name[0]}</foaf:givenName>"

@tag("bib:authors")
@tag("rdf:Seq")
def authors(nameList):
    s = ""
    for name in nameList:
        s += autor(name)
    return s

@tag("bib:presentedAt")
def Conference(title):
    return f"<bib:Conference><dc:title>{title}</dc:title></bib:Conference>"

def split(pattern,s):
    return [t for t in re.split(pattern,s) if not re.fullmatch(pattern,t)]

def parseString(s:str):
    (authors,title,other) = s.split("\n")
    authorElemList = split(r"(，|, |,|， )",authors)
    authorList = []
    for authorElem in authorElemList:
        if authorElem[0] == ' ':
            authorElem = authorElem[1:]
        splitElem = split(" ",authorElem)
        if len(splitElem) == 2:
            (last,first) = splitElem
        else:
            last = splitElem[0]
            first = ""
        authorList.append([first,last])

    otherElemList = split('(,|, |，)',other)

    if len(otherElemList) == 4:
        (conferenceTitle,pagesElem,_,dateElem) = otherElemList[:4]
    else:
        conferenceTitle = ",".join(otherElemList[:-3])
        pagesElem = otherElemList[-3]
        dateElem = otherElemList[-1]
    pages = re.sub("pp.( )*","",pagesElem)
    date = re.sub("[年月]","-",dateElem.split("-")[0].replace("日",""))
    return title, conferenceTitle, pages, date,authorList


def saveFile(text,fileName):
        title, conferenceTitle, pages, date, authorList = parseString(text)
        s = RDF(title, conferenceTitle, pages, date, authorList)
        with open(fileName, "w", encoding='utf-8') as o:
            print(s, file = o)
            print(f"successfully saved to {fileName}")



def monitor_clipboard():
    """
    クリップボードを監視し、内容が変更されたら指定の動作を実行します。
    """
    print("クリップボード監視を開始しました。")
    count = 0
    # 初期のクリップボード内容を保存
    last_clipboard = pyperclip.paste()

    try:
        while True:
            # 現在のクリップボード内容を取得
            current_clipboard = pyperclip.paste()

            # クリップボードの内容が変更されたか確認
            if current_clipboard != last_clipboard:
                # 最後のクリップボード内容を更新
                last_clipboard = current_clipboard
                # ここに実行したい処理を追加

                count += 1
                saveFile(current_clipboard, f"export{count}.rdf")


            # 少し待機してCPU使用率を下げる
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\nクリップボード監視を終了しました。")

if __name__ == '__main__':
    monitor_clipboard()

