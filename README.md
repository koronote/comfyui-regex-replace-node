# ComfyUI Regex Replace Node

A custom node for [ComfyUI](https://github.com/comfyanonymous/ComfyUI) that merges multiple string inputs and removes matched portions using regular expressions.

複数のテキスト入力をマージし、正規表現にマッチした部分を削除する ComfyUI カスタムノードです。

---

## Features / 機能

- Merge up to N string inputs with a configurable separator
- Remove matched text using a regular expression pattern
- Automatically cleans up extra spaces, commas, and `//`|`#` line comments, as well as `/* … */` block comments
- Displays both the merged text and the replaced text directly on the node
- Dynamically add/remove input sockets via the **"Update num of inputs"** button

---
- 複数の文字列入力を、設定可能な区切り文字でマージ
- 正規表現パターンを使用して、マッチしたテキストを削除
- 余分なスペース、カンマ、`//`|`#` 行コメント、`/* … */` ブロックコメントを自動的にクリーンアップ
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

### Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `text_1` … `text_N` | STRING (socket) | At least 1 | Texts to merge. Empty inputs are skipped. / マージするテキスト。空の入力はスキップされます。 |
| `input_count` | INT (widget) | ✓ | Number of input sockets (default: 4, min: 1). Press **Update num of inputs** to apply. / 入力ソケットの数 (デフォルト: 4, 最小: 1)。**入力数を更新** を押して適用します。 |
| `separator` | STRING (widget) | ✓ | Delimiter inserted between merged texts (default: `, `). / マージされたテキストの間に挿入される区切り文字 (デフォルト: `, `)。 |
| `pattern` | STRING (widget) | ✓ | Regex pattern — matched text is deleted. Leave blank to skip. / 正規表現パターン — マッチしたテキストが削除されます。空欄の場合はスキップされます。 |

### Outputs

| Name | Type | Description |
|------|------|-------------|
| `replaced text / 置換後テキスト` | STRING | Cleaned text after regex replacement. / 正規表現置換後のクリーンアップ済みテキスト |

### Node preview widgets (read-only)

After execution, two preview widgets appear on the node:
処理が終了すると、ノード上に2つのプレビューワジェットが表示されます：

| Widget | Content |
|--------|---------|
| merged text / マージ後テキスト | Raw merged text before regex replacement / 正規表現置換前のマージ済みテキスト |
| replaced text / 置換後テキスト | Final text after replacement and cleanup / 正規表現置換後のクリーンアップ済みテキスト |

---

## Post-processing / 後処理

After the regex replacement the node always applies these cleanup steps:
正規表現置換後、ノードは常に下記のクリーンアップ手順を適用します：

1. Remove `//` line comments and newlines
2. Remove `#` line comments and newlines
3. Remove `/* … */` block comments
4. Collapse consecutive whitespace
5. Collapse repeated commas (`,,` → `,`)

---

## Usage Example / 使用例

**Inputs:**

| Socket | Value |
|--------|-------|
| text_1 | `masterpiece, best quality , , , , # line comment, extra tag, , , ` |
| text_2 | `// draft comment` |
| text_3 | `1girl,,,,,, ,, /* comment block */ solo` |

**Settings:**

| Widget | Value |
|--------|-------|
| separator | `, ` |
| pattern | *(empty)* |

**Output:**

```
masterpiece,best quality,1girl,solo
```

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
