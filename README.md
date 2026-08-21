# nhentai Artist Ranking

nhentai.net の公開メタデータを集計し、artist タグを作品数順に並べる静的ランキングです。

## 指標

- **作品数**: artist タグが付いたギャラリー数。主ランキング。
- **総ページ数**: 作品のページ数の合計。規模の補助指標。
- **直近12か月**: 集計基準日から遡った12か月に登録された作品数。
- **指数**: 作品数を主軸に、ページ数と直近12か月を少し加味した表示用スコア。

favorites / views の完全な履歴は公開データで一貫して取得できないため、「人気」ではなく「メタデータ上の掲載規模」として解釈してください。画像・本文は取得・保存しません。

## 更新

```powershell
python scripts/build_ranking.py
```

既定では、公開されている日次更新スナップショットの月別 CSV をダウンロードし、`data/ranking.json` を生成します。GitHub Actions から週次更新する場合は `.github/workflows/update.yml` を利用します。

データ出典: [unofficial-nhentai-api](https://github.com/van-geaux/unofficial-nhentai-api) の月別 CSV（nhentai のメタデータを元にした非公式スナップショット）。

## 注意

成人向けサイト由来のメタデータを扱います。未成年を示唆するタグなどの内容を推奨・再配布する目的ではありません。利用者は地域の法令、対象サイトの規約、データ提供元のライセンスを確認してください。

