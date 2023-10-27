# NDLOCRと後処理プログラムの説明
## 必要なもの
- Python3の実行環境（3.8.2で動作確認）
- Googleアカウント


## OCR実行方法 (GPUを使う場合)
https://github.com/ndl-lab/ndlocr_cli
を参照

## OCR実行方法（Google Colabを使う場合）
1. input_dirの作成

    OCR対象の画像ファイル、もしくはPDFファイルを格納したディレクトリ（input_dir）を以下のように作成する。ファイル名は"R(7桁の連番)_pp.jpg"とする。

    ```
    input_dir
    └── img
        ├── R0000001_pp.jpg
        ├── R0000002_pp.jpg
        └── R0000003_pp.jpg
    ```

2. input_dirをGoogle Driveにアップロードする。

3. NDLOCRの実行（画像ファイルのOCRの場合）

    1. NDLOCRのノートブック（https://colab.research.google.com/github/nakamura196/ndl_ocr/blob/main/ndl_ocr_v2.ipynb#scrollTo=ADBGbIClAgdX） を開く。

    2. 「1. 初期セットアップ」を実行する。

    3. 「複数の既にダウンロード済みの画像ファイルを対象にする場合」を実行する。（processはレイアウト抽出と文字認識のみ、rubyにはチェックしない）

## 後処理
1. 作成されたフォルダの中にあるxmlファイルをGoogle Driveからローカルに保存する。

    - xmlファイルの場所
        ```
        output_dir
        ├── input_dir
        :   ├── xml
        :   :   └── innput_dir.xml
        ```
    - 保存する場所は、このREADMEやrun.shと同じ場所だと分かりやすい。

2. run.shの実行

    ```
    $ sh run.sh [xml_file] [out_file] [1 or 2 (段数)]

        ex:
        $ sh run.sh input_dir.xml out.txt 1
    ```

## エラーパターンの追加
error.csvにエラーパターンを追記することで、一括で修正できる。
（修正前の文字列）,（修正後の文字列）

## 改行検知が上手く行かない場合

