# ComfyUI Regex Replace Node

A custom node for [ComfyUI](https://github.com/comfyanonymous/ComfyUI) that merges multiple string inputs and removes matched portions using regular expressions.

複数のテキスト入力をマージし、正規表現にマッチした部分を削除する ComfyUI カスタムノードです。

---

## Features / 機能

- Merge up to N string inputs with a fixed `,` separator
- Remove matched text using a regular expression pattern
- Automatically cleans up extra spaces, commas, and `//`|`#` line comments, as well as `/* … */` block comments
- Deduplicate tags (optional, off by default) — trims whitespace and removes duplicate entries while preserving order
- Displays both the merged text and the replaced text directly on the node
- Dynamically add/remove input sockets via the **"Update num of inputs"** button

---

- 複数の文字列入力を `","` 固定区切りでマージ
- 正規表現パターンを使用して、マッチしたテキストを削除
- 余分なスペース、カンマ、`//`|`#` 行コメント、`/* … */` ブロックコメントを自動的にクリーンアップ
- 重複タグの除去（任意、デフォルト OFF）— 前後の空白をトリムし、順序を保ちながら重複を削除
- ノード上にマージされたテキストと置換されたテキストの両方を表示
- **"入力数を更新"** ボタンで、動的に入力ソケットを追加/削除可能

---

## Installation / インストール

### Option 1 — Clone into custom_nodes

```bash
cd ComfyUI/custom_nodes
git clone https://huggingface.co/kurodnp/comfyui-regex-replace-node regex_replace_node
```

### Option 2 — Manual

1. Download or copy this repository into `ComfyUI/custom_nodes/regex_replace_node/`
2. Restart ComfyUI

No extra Python dependencies are required (uses the standard library `re` module).


---

## Node: Regex Replace

### Widgets (display order) / ウィジェット（表示順）

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `input_count` | INT | 4 | Number of input sockets (min: 1). Press **Update num of inputs** to apply. / 入力ソケットの数（最小: 1）。**入力数を更新** を押して適用します。 |
| *(button)* | — | — | **Update num of inputs / 入力数を更新** — syncs sockets to `input_count`. / ソケット数を `input_count` に合わせます。 |
| `pattern` | STRING | *(empty)* | Regex pattern — matched text is deleted. Leave blank to skip. / 正規表現パターン — マッチしたテキストが削除されます。空欄の場合はスキップされます。 |
| `deduplicate` | BOOLEAN | OFF | Remove duplicate tags after cleanup. / クリーンアップ後に重複タグを除去します。 |

### Inputs / 入力ソケット

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `text_1` … `text_N` | STRING (socket) | At least 1 | Texts to merge. Empty inputs are skipped. / マージするテキスト。空の入力はスキップされます。 |

### Outputs

| Name | Type | Description |
|------|------|-------------|
| `結果テキスト` | STRING | Cleaned text after regex replacement (and deduplication if enabled). / 正規表現置換後（有効時は重複除去後）のクリーンアップ済みテキスト |

### Node preview widgets (read-only)

After execution, two preview widgets appear on the node:
処理が終了すると、ノード上に2つのプレビューウィジェットが表示されます：

| Widget | Content |
|--------|---------|
| merged text / マージ後テキスト | Raw merged text before regex replacement / 正規表現置換前のマージ済みテキスト |
| replaced text / 置換後テキスト | Final text after replacement, cleanup, and deduplication / 正規表現置換・クリーンアップ・重複除去後の最終テキスト |

---

## Post-processing / 後処理

After the regex replacement the node always applies these cleanup steps:
正規表現置換後、ノードは常に下記のクリーンアップ手順を適用します：

1. Remove `//` and `#` line comments and newlines
2. Remove `/* … */` block comments
3. Collapse consecutive whitespace
4. Collapse repeated commas (`,,` → `,`)
5. *(if `deduplicate` is ON)* Split by `,`, trim each tag, remove duplicates (order preserved), rejoin

---

## Usage Example / 使用例

**Inputs:**

| Socket | Value |
|--------|-------|
| text_1 | `masterpiece, best quality , , , , # line comment, extra tag, , , ` |
| text_2 | `// draft comment` |
| text_3 | `1girl,,,,,, ,, /* comment block */ solo` |
| text_4 | `masterpiece` |

**Settings:**

| Widget | Value |
|--------|-------|
| pattern | *(empty)* |
| deduplicate | ON |

**Output:**

```
masterpiece,best quality,extra tag,1girl,solo
```

(`masterpiece` from text_4 is removed as a duplicate)

---

## File Structure / ファイル構成

```
regex_replace_node/
├── __init__.py          # Node logic (Python)
└── web/
    └── js/
        └── regexReplace.js  # Frontend extension (dynamic sockets + preview widgets)
```

---

## License

MIT
