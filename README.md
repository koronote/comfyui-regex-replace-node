# ComfyUI Regex Replace Node

A custom node for [ComfyUI](https://github.com/comfyanonymous/ComfyUI) that merges multiple string inputs and removes matched portions using regular expressions.

複数のテキスト入力をマージし、正規表現にマッチした部分を削除する ComfyUI カスタムノードです。

---

## Features / 機能

- Merge up to N string inputs with a configurable separator
- Remove matched text using a regular expression pattern
- Automatically cleans up extra spaces, commas, and `//` line comments
- Displays both the merged text and the replaced text directly on the node
- Dynamically add/remove input sockets via the **"入力数を更新"** button

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
| `text_1` … `text_N` | STRING (socket) | At least 1 | Texts to merge. Empty inputs are skipped. |
| `input_count` | INT (widget) | ✓ | Number of input sockets (default: 4, min: 1). Press **入力数を更新** to apply. |
| `separator` | STRING (widget) | ✓ | Delimiter inserted between merged texts (default: `, `). |
| `pattern` | STRING (widget) | ✓ | Regex pattern — matched text is deleted. Leave blank to skip. |

### Outputs

| Name | Type | Description |
|------|------|-------------|
| `結果テキスト` | STRING | Cleaned text after regex replacement. |

### Node preview widgets (read-only)

After execution, two preview widgets appear on the node:

| Widget | Content |
|--------|---------|
| マージ後テキスト | Raw merged text before regex replacement |
| 置換後テキスト | Final text after replacement and cleanup |

---

## Post-processing / 後処理

After the regex replacement the node always applies these cleanup steps:

1. Remove `//` line comments and newlines
2. Remove `#` line comments and newlines
3. Remove `/* … */` block comments
4. Collapse consecutive whitespace
5. Collapse repeated commas (`,,` → `,`)
6. Normalize comma spacing (`, `)

---

## Usage Example / 使用例

**Inputs:**

| Socket | Value |
|--------|-------|
| text_1 | `masterpiece, best quality` |
| text_2 | `// draft comment` |
| text_3 | `1girl, solo` |

**Settings:**

| Widget | Value |
|--------|-------|
| separator | `, ` |
| pattern | *(empty)* |

**Output:**

```
masterpiece, best quality, 1girl, solo
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
