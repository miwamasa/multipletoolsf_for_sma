"""
Building Management Agent Example

このスクリプトは、ビル管理システムの命名規則ツールを使用して、
エージェントが複数のツールを連携させて質問に答える例を示します。
"""

from smolagents import CodeAgent, HfApiModel
from building_tools import (
    OfficeToZoneTool,
    ZoneToEquipmentTool,
    BuildSensorIdTool,
    EquipmentFloorTool,
    NamingConventionTool,
)


def main():
    # ツールのインスタンス化
    tools = [
        OfficeToZoneTool(),
        ZoneToEquipmentTool(),
        BuildSensorIdTool(),
        EquipmentFloorTool(),
        NamingConventionTool(),
    ]

    # モデルの設定（HuggingFace APIを使用）
    # 注: 実際の使用には HF_TOKEN 環境変数が必要です
    model = HfApiModel()

    # CodeAgentの作成
    agent = CodeAgent(
        tools=tools,
        model=model,
        max_steps=10,
        verbose=True,
    )

    print("=" * 80)
    print("Building Management Agent - Demo")
    print("=" * 80)
    print()

    # テストクエリ1: B0802に関連する外調機の給気温度
    query1 = "B0802に関連する外調機（OAFan）の給気温度（SAT）のセンサーIDを教えてください"
    print(f"Query 1: {query1}")
    print("-" * 80)

    try:
        result1 = agent.run(query1)
        print(f"\nResult: {result1}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "=" * 80)
    print()

    # テストクエリ2: C1201のAHUの還気温度
    query2 = "オフィスC1201を担当するAHU（空調機）の還気温度（RAT）センサーのIDは何ですか？"
    print(f"Query 2: {query2}")
    print("-" * 80)

    try:
        result2 = agent.run(query2)
        print(f"\nResult: {result2}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "=" * 80)
    print()

    # テストクエリ3: ステップバイステップでの動作確認
    print("Step-by-step demonstration:")
    print("-" * 80)

    # ステップ1: オフィスアドレスからゾーンを取得
    office_tool = OfficeToZoneTool()
    zone = office_tool.forward("B0802")
    print(f"Step 1 - Office B0802 is in zone: {zone}")

    # ステップ2: ゾーンと機器タイプから機器番号を取得
    zone_tool = ZoneToEquipmentTool()
    equipment_info = zone_tool.forward(zone, "OAFan")
    print(f"Step 2 - Equipment in {zone} for OAFan: {equipment_info}")

    # ステップ3: 機器番号からフロアを取得
    floor_tool = EquipmentFloorTool()
    floor = floor_tool.forward("A1004")
    print(f"Step 3 - Equipment A1004 is on floor: {floor}")

    # ステップ4: センサーIDを構築
    sensor_tool = BuildSensorIdTool()
    sensor_id = sensor_tool.forward(floor, "OAFan", "SAT", "A1004")
    print(f"Step 4 - Full sensor ID: {sensor_id}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
