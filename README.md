# pokemon-matchup

ポケモンチャンピオンズ向けの選出支援システムです。登録した自分のパーティーと
相手の6体をもとに、推奨する選出と先発を提案することを目指します。

現在はPythonプロジェクトの初期構成のみで、アプリケーション機能は未実装です。
最初はシングルバトルを対象とし、将来のダブルバトル対応も考慮して設計します。

## 必要な環境

- Python 3.12
- [uv](https://docs.astral.sh/uv/)

## セットアップ

```shell
uv sync --frozen
```

## 開発用コマンド

```shell
uv run black --check .
uv run ruff check .
uv run mypy src
uv run pytest
```

自動整形を適用する場合は次を実行します。

```shell
uv run black .
uv run ruff check --fix .
```

## ディレクトリ構成

```text
src/pokemon_matchup/  Pythonパッケージ
tests/                テスト
```

ゲームデータ、ドメインルール、ユースケース、UIは、実装時にそれぞれ分離します。
