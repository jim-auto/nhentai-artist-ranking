# nhentai Artist Favorites Ranking

nhentai.net API v2 の公開メタデータを集計し、作品ごとの `num_favorites` を artist 単位に合算する静的ランキングです。

## 指標

- **favorites合計**: artistごとに取得した人気上位25作品の `num_favorites` 合計。主ランキング。
- **favorites中央値**: 作品ごとのお気に入り数の中央値。
- **最多作品**: artistの作品のうち最大の `num_favorites`。

全artistの全作品を毎回取得するのは過剰なアクセスになるため、artistタグ掲載数上位100組について、favorites順の上位25作品だけを比較対象にしています。画像・本文は取得・保存しません。

## 更新

```powershell
python scripts/build_favorites_ranking.py
```

既定では、公開されている日次更新スナップショットの月別 CSV をダウンロードし、`data/ranking.json` を生成します。GitHub Actions から週次更新する場合は `.github/workflows/update.yml` を利用します。

データ出典: [unofficial-nhentai-api](https://github.com/van-geaux/unofficial-nhentai-api) の月別 CSV（nhentai のメタデータを元にした非公式スナップショット）。

## 注意

成人向けサイト由来のメタデータを扱います。未成年を示唆するタグなどの内容を推奨・再配布する目的ではありません。利用者は地域の法令、対象サイトの規約、データ提供元のライセンスを確認してください。
