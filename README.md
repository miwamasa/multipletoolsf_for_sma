# ビル管理システム - Smolagents ツール連携デモ

## 概要

このプロジェクトは、ビル管理システムにおける建物、施設、センサーの命名規則に関する情報を複数のツールに分散させ、smolagentのCodeAgentがそれらを連携して使用する例を示します。

## 背景

ビル管理システムでは、以下のような複雑な命名規則があります：

- **センサーID**: `10F_OAFan_SAT_A1004`
  - 10F: 10階
  - OAFan: 外調機（Outdoor Air Fan unit）
  - SAT: 給気温度（Supply Air Temperature）
  - A1004: 機器番号

- **ゾーン情報**: オフィスアドレス（B0801, B0802）がゾーン（N_ZONE）に属する
- **機器配置**: ゾーン（N_ZONE）には外調機（A1004, A1005）が設置されている

ユーザーが「B0802に関連する外調機の給気温度が知りたい」と質問した場合、エージェントは複数の情報源を組み合わせて`10F_OAFan_SAT_A1004`を導き出す必要があります。

## ツール設計の原則

### 1. 情報の分散化

各ツールは限定的な情報のみを保持します：

- **OfficeToZoneTool**: オフィスアドレス → ゾーン
- **ZoneToEquipmentTool**: ゾーン + 機器タイプ → 機器番号リスト
- **EquipmentFloorTool**: 機器番号 → フロア
- **BuildSensorIdTool**: 全パラメータ → センサーID
- **NamingConventionTool**: 命名規則の説明

### 2. 明確なインターフェイス

各ツールの`description`には以下を含めます：

```python
description = """
1. ツールの目的（1行で簡潔に）

2. 入力パラメータ
   - パラメータ名: 説明と例

3. 出力
   - 何が返されるか

4. 使用タイミング
   - このツールを使うべき状況

5. 使用例
   - 具体的な入力と出力の例
"""
```

### 3. エージェントの推論を促す設計

ツールは最終的な答えを直接返すのではなく、エージェントが複数のツールを組み合わせて推論できるように設計されています。

## ツール詳細

### OfficeToZoneTool

**目的**: オフィスアドレスからゾーン識別子を取得

**入力**:
- `office_address` (str): オフィスアドレスコード（例: 'B0801', 'B0802'）

**出力**:
- ゾーン識別子（例: 'N_ZONE', 'S_ZONE'）

**Description のポイント**:
- 入力形式を明確に示す（'B0801'のような形式）
- 出力例を具体的に示す
- 「どんな時に使うか」を明記

```python
description = """
This tool returns the zone identifier for a given office address.

Input: office_address (str) - Office address code (e.g., 'B0801', 'B0802', 'C1201')
Output: zone identifier (str) - Zone name (e.g., 'N_ZONE', 'S_ZONE', 'E_ZONE')

Use this tool when you need to find which zone an office belongs to.
Example: office_to_zone('B0801') returns 'N_ZONE'
"""
```

### ZoneToEquipmentTool

**目的**: ゾーンと機器タイプから機器番号を取得

**入力**:
- `zone` (str): ゾーン識別子（例: 'N_ZONE'）
- `equipment_type` (str): 機器タイプ（'OAFan', 'AHU', 'VAV'）

**出力**:
- 機器番号のリスト（例: ['A1004', 'A1005']）

**Description のポイント**:
- 機器タイプの選択肢を明記（OAFan, AHU, VAVと、それぞれの意味）
- 複数の機器が返される可能性を示唆
- 日本語の対応も示す（外調機、空調機など）

```python
description = """
This tool returns equipment numbers for a specific zone and equipment type.

Input:
    - zone (str) - Zone identifier (e.g., 'N_ZONE', 'S_ZONE')
    - equipment_type (str) - Equipment type code:
        * 'OAFan' for outdoor air handling units (外調機)
        * 'AHU' for air handling units (空調機)
        * 'VAV' for variable air volume units
Output: list of equipment numbers (str) - e.g., ['A1004', 'A1005']

Use this tool when you know the zone and need to find equipment serving that zone.
Example: zone_to_equipment('N_ZONE', 'OAFan') returns equipment numbers like 'A1004'
"""
```

### EquipmentFloorTool

**目的**: 機器番号からフロア番号を取得

**入力**:
- `equipment_number` (str): 機器番号（例: 'A1004'）

**出力**:
- フロア番号（例: '10F'）

**Description のポイント**:
- シンプルな1対1のマッピングであることを明示
- フロア表記の形式（'F'サフィックス付き）を示す

### BuildSensorIdTool

**目的**: 機器情報と測定点から完全なセンサーIDを構築

**入力**:
- `floor` (str): フロア番号（例: '10F'）
- `equipment_type` (str): 機器タイプ（'OAFan', 'AHU', 'VAV'）
- `measurement_point` (str): 測定点（'SAT', 'RAT', 'OAT', 'HUM', 'FLOW'）
- `equipment_number` (str): 機器番号（例: 'A1004'）

**出力**:
- 完全なセンサーID（例: '10F_OAFan_SAT_A1004'）

**Description のポイント**:
- 測定点の選択肢を網羅的に列挙
- 各測定点の意味を日本語でも説明
- センサーIDの構築フォーマットを明示

```python
description = """
This tool constructs the full sensor ID from equipment information and measurement point.

Input:
    - floor (str) - Floor number (e.g., '10F', '5F')
    - equipment_type (str) - Equipment type ('OAFan', 'AHU', 'VAV')
    - measurement_point (str) - What is being measured:
        * 'SAT' for Supply Air Temperature (給気温度)
        * 'RAT' for Return Air Temperature (還気温度)
        * 'OAT' for Outdoor Air Temperature (外気温度)
        * 'HUM' for Humidity (湿度)
        * 'FLOW' for Air Flow (風量)
    - equipment_number (str) - Equipment number (e.g., 'A1004')
Output: Full sensor ID (str) - e.g., '10F_OAFan_SAT_A1004'

Use this tool when you have all equipment details and need to construct the sensor identifier.
The format is: {floor}_{equipment_type}_{measurement_point}_{equipment_number}
"""
```

### NamingConventionTool

**目的**: 命名規則のドキュメントを提供

**入力**: なし

**出力**: 命名規則の完全な説明

**Description のポイント**:
- このツールが「知識」を提供することを明示
- 他のツールをどう使うべきかのガイダンスを含む
- 全体的なワークフローを説明

## 使用例

### 例1: B0802に関連する外調機の給気温度センサー

**質問**: 「B0802に関連する外調機の給気温度が知りたい」

**エージェントの推論フロー**:

1. **OfficeToZoneTool** を使用
   - 入力: `B0802`
   - 出力: `N_ZONE`

2. **ZoneToEquipmentTool** を使用
   - 入力: `zone=N_ZONE`, `equipment_type=OAFan`
   - 出力: `Equipment numbers: A1004, A1005`

3. **EquipmentFloorTool** を使用（A1004を選択）
   - 入力: `A1004`
   - 出力: `10F`

4. **BuildSensorIdTool** を使用
   - 入力: `floor=10F`, `equipment_type=OAFan`, `measurement_point=SAT`, `equipment_number=A1004`
   - 出力: `10F_OAFan_SAT_A1004`

**最終回答**: `10F_OAFan_SAT_A1004`

### 例2: C1201の空調機の還気温度センサー

**質問**: 「オフィスC1201を担当するAHUの還気温度センサーのIDは？」

**エージェントの推論フロー**:

1. **OfficeToZoneTool**: `C1201` → `S_ZONE`
2. **ZoneToEquipmentTool**: `S_ZONE`, `AHU` → `B3101, B3102`
3. **EquipmentFloorTool**: `B3101` → `12F`
4. **BuildSensorIdTool**: `12F`, `AHU`, `RAT`, `B3101` → `12F_AHU_RAT_B3101`

## セットアップと実行

### 必要なライブラリ

```bash
pip install smolagents
```

### 環境変数

HuggingFace APIを使用する場合:

```bash
export HF_TOKEN="your_huggingface_token"
```

### 実行方法

#### ステップバイステップのデモ

```bash
python agent_example.py
```

このスクリプトは以下を実行します：
- 複数のクエリに対するエージェントの動作
- ステップバイステップでのツール連携の確認

#### カスタムクエリ

```python
from smolagents import CodeAgent, HfApiModel
from building_tools import *

tools = [
    OfficeToZoneTool(),
    ZoneToEquipmentTool(),
    BuildSensorIdTool(),
    EquipmentFloorTool(),
    NamingConventionTool(),
]

agent = CodeAgent(tools=tools, model=HfApiModel())

result = agent.run("あなたのクエリをここに入力")
print(result)
```

## ツール設計のベストプラクティス

### 1. Description は具体的に

❌ **悪い例**:
```python
description = "Gets zone for office"
```

✅ **良い例**:
```python
description = """
This tool returns the zone identifier for a given office address.

Input: office_address (str) - Office address code (e.g., 'B0801', 'B0802', 'C1201')
Output: zone identifier (str) - Zone name (e.g., 'N_ZONE', 'S_ZONE', 'E_ZONE')

Use this tool when you need to find which zone an office belongs to.
Example: office_to_zone('B0801') returns 'N_ZONE'
"""
```

### 2. 入力パラメータの制約を明示

```python
inputs = {
    "office_address": {
        "type": "string",
        "description": "The office address code (e.g., B0801, B0802)"
    }
}
```

### 3. エラーハンドリング

ツールは適切なエラーメッセージを返すべきです：

```python
def forward(self, office_address: str) -> str:
    office_address = office_address.strip().upper()
    zone = self.office_zone_map.get(office_address)
    if zone is None:
        return f"Error: Office address '{office_address}' not found in database"
    return zone
```

### 4. ドメイン用語の説明

日本語と英語の両方で専門用語を説明：

```python
* 'OAFan' for outdoor air handling units (外調機)
* 'SAT' for Supply Air Temperature (給気温度)
```

### 5. 使用例を含める

各ツールの description に具体的な使用例を含めることで、エージェントの理解を助けます：

```python
Example: zone_to_equipment('N_ZONE', 'OAFan') returns equipment numbers like 'A1004'
```

## データモデル

### オフィスアドレス → ゾーン

| オフィスアドレス | ゾーン |
|--------------|--------|
| B0801        | N_ZONE |
| B0802        | N_ZONE |
| B0803        | N_ZONE |
| C1201        | S_ZONE |
| C1202        | S_ZONE |
| D0901        | E_ZONE |
| D0902        | E_ZONE |

### ゾーン + 機器タイプ → 機器番号

| ゾーン  | 機器タイプ | 機器番号        |
|---------|----------|---------------|
| N_ZONE  | OAFan    | A1004, A1005  |
| N_ZONE  | AHU      | A2001, A2002  |
| S_ZONE  | OAFan    | B3001         |
| S_ZONE  | AHU      | B3101, B3102  |
| E_ZONE  | OAFan    | C4001         |
| E_ZONE  | VAV      | C4201-C4203   |

### 機器番号 → フロア

| 機器番号 | フロア |
|---------|--------|
| A1004   | 10F    |
| A1005   | 10F    |
| A2001   | 9F     |
| A2002   | 9F     |
| B3001   | 12F    |
| B3101   | 12F    |
| B3102   | 12F    |
| C4001   | 8F     |
| C4201   | 8F     |
| C4202   | 8F     |
| C4203   | 8F     |

## 拡張アイデア

### 1. データベース統合

現在はハードコードされたデータを使用していますが、実際のシステムではデータベースから取得：

```python
def forward(self, office_address: str) -> str:
    # SQLやAPIから取得
    query = "SELECT zone FROM office_zones WHERE address = ?"
    result = db.execute(query, [office_address])
    return result
```

### 2. リアルタイムセンサー値の取得

センサーIDが分かったら、実際の値を取得するツールを追加：

```python
class GetSensorValueTool(Tool):
    name = "get_sensor_value"
    description = """
    Returns the current value from a sensor.
    Input: sensor_id (str) - Full sensor ID (e.g., '10F_OAFan_SAT_A1004')
    Output: Current sensor value with units
    """
```

### 3. 時系列データの取得

```python
class GetSensorHistoryTool(Tool):
    name = "get_sensor_history"
    description = """
    Returns historical data for a sensor.
    Input:
        - sensor_id (str)
        - start_time (str)
        - end_time (str)
    Output: Time series data
    """
```

### 4. 異常検知

```python
class DetectAnomalyTool(Tool):
    name = "detect_anomaly"
    description = """
    Checks if sensor readings are within normal range.
    Input: sensor_id (str)
    Output: Anomaly status and details
    """
```

## トラブルシューティング

### エージェントが適切なツールを選択しない

- Description をより具体的にする
- 使用例を追加する
- ツールの責任範囲を明確にする

### ツールの連携がうまくいかない

- 各ツールの出力形式を統一する
- エラーメッセージを分かりやすくする
- 中間結果を確認できるログを追加

### パフォーマンスの問題

- キャッシュを実装する
- データベースクエリを最適化する
- 不要なツール呼び出しを減らす

## まとめ

このプロジェクトは、複雑なドメイン知識を複数のツールに分散させ、エージェントが推論を通じて問題を解決する方法を示しています。

**重要なポイント**:
1. 各ツールは単一の責任を持つ
2. Description は詳細かつ具体的に
3. 入力/出力の形式を明確にする
4. ドメイン用語を説明する
5. 使用例を含める

これにより、エージェントは複雑なクエリを分解し、適切なツールを組み合わせて答えを導き出すことができます。
