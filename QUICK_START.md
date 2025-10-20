# クイックスタートガイド

## セットアップ

```bash
# 1. 必要なライブラリをインストール
pip install -r requirements.txt

# 2. ツールの動作確認
python test_tools.py
```

## ツールの構成

```
multipletoolsf_for_sma/
├── building_tools.py      # 5つのツールクラス
├── agent_example.py       # CodeAgentを使用した実行例
├── test_tools.py         # ツールの単体テスト
├── requirements.txt      # 依存ライブラリ
├── README.md            # 詳細なドキュメント
└── QUICK_START.md       # このファイル
```

## 基本的な使い方

### 1. ツールを個別に使う

```python
from building_tools import OfficeToZoneTool

# オフィスアドレスからゾーンを取得
tool = OfficeToZoneTool()
zone = tool.forward("B0802")
print(zone)  # 出力: N_ZONE
```

### 2. エージェントと連携して使う

```python
from smolagents import CodeAgent, HfApiModel
from building_tools import *

# ツールを準備
tools = [
    OfficeToZoneTool(),
    ZoneToEquipmentTool(),
    BuildSensorIdTool(),
    EquipmentFloorTool(),
    NamingConventionTool(),
]

# エージェントを作成
agent = CodeAgent(tools=tools, model=HfApiModel())

# 質問を投げる
result = agent.run("B0802に関連する外調機の給気温度センサーIDを教えてください")
print(result)
```

## 各ツールの役割

| ツール名 | 機能 | 入力 | 出力 |
|---------|------|------|------|
| **OfficeToZoneTool** | オフィス → ゾーン | オフィスアドレス (例: B0802) | ゾーン (例: N_ZONE) |
| **ZoneToEquipmentTool** | ゾーン + 機器タイプ → 機器番号 | ゾーン, 機器タイプ | 機器番号リスト |
| **EquipmentFloorTool** | 機器番号 → フロア | 機器番号 (例: A1004) | フロア (例: 10F) |
| **BuildSensorIdTool** | 全情報 → センサーID | フロア, 機器タイプ, 測定点, 機器番号 | センサーID |
| **NamingConventionTool** | 命名規則の説明 | なし | 命名規則のドキュメント |

## 機器タイプと測定点

### 機器タイプ

- `OAFan`: 外調機（Outdoor Air Fan unit）
- `AHU`: 空調機（Air Handling Unit）
- `VAV`: 可変風量ユニット（Variable Air Volume unit）

### 測定点

- `SAT`: 給気温度（Supply Air Temperature）
- `RAT`: 還気温度（Return Air Temperature）
- `OAT`: 外気温度（Outdoor Air Temperature）
- `HUM`: 湿度（Humidity）
- `FLOW`: 風量（Air Flow）

## 例題

### 例題1: B0802に関連する外調機の給気温度

**手順**:
1. B0802 → N_ZONE (OfficeToZoneTool)
2. N_ZONE + OAFan → A1004, A1005 (ZoneToEquipmentTool)
3. A1004 → 10F (EquipmentFloorTool)
4. 10F + OAFan + SAT + A1004 → **10F_OAFan_SAT_A1004** (BuildSensorIdTool)

**答え**: `10F_OAFan_SAT_A1004`

### 例題2: C1201の空調機の還気温度

**手順**:
1. C1201 → S_ZONE
2. S_ZONE + AHU → B3101, B3102
3. B3101 → 12F
4. 12F + AHU + RAT + B3101 → **12F_AHU_RAT_B3101**

**答え**: `12F_AHU_RAT_B3101`

## デザインパターン: 情報の分散化

このプロジェクトの重要なポイントは、**情報を意図的に分散させる**ことです。

### なぜ分散させるのか？

1. **エージェントの推論を促す**: 一つのツールが全ての答えを持たないため、エージェントは複数のツールを組み合わせて考える必要があります

2. **保守性の向上**: 各ツールが単一の責任を持つため、変更や拡張が容易です

3. **再利用性**: 個々のツールは独立しているため、他の用途でも再利用できます

### 良い例 vs 悪い例

❌ **悪い例**: 1つのツールで全てを解決
```python
class GetSensorIdTool:
    def forward(self, office_address, equipment_type, measurement_point):
        # オフィス → ゾーン → 機器番号 → フロア → センサーID
        # 全てを内部で処理してしまう
        return sensor_id
```

✅ **良い例**: 複数のツールで情報を分散
```python
# 各ツールは限定的な情報のみを持つ
OfficeToZoneTool()      # オフィス → ゾーン
ZoneToEquipmentTool()   # ゾーン → 機器番号
EquipmentFloorTool()    # 機器番号 → フロア
BuildSensorIdTool()     # 全情報 → センサーID
```

## トラブルシューティング

### エージェントが動作しない

- HuggingFace APIを使用する場合、環境変数 `HF_TOKEN` を設定してください
  ```bash
  export HF_TOKEN="your_token_here"
  ```

### ツールの動作を確認したい

- `test_tools.py` を実行して、各ツールが正しく動作するか確認できます
  ```bash
  python test_tools.py
  ```

## 次のステップ

詳細なドキュメントや拡張アイデアについては、`README.md` を参照してください。

- データベース統合
- リアルタイムセンサー値の取得
- 時系列データの分析
- 異常検知機能
