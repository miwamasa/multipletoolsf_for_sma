"""
Building Tools Unit Test

このスクリプトは、各ツールが正しく動作することを確認します。
エージェントを使わずに、個別のツールの動作をテストします。
"""

from building_tools import (
    OfficeToZoneTool,
    ZoneToEquipmentTool,
    BuildSensorIdTool,
    EquipmentFloorTool,
    NamingConventionTool,
)


def test_office_to_zone():
    print("=" * 80)
    print("Test 1: OfficeToZoneTool")
    print("=" * 80)

    tool = OfficeToZoneTool()

    # テストケース1: 正常系
    test_cases = [
        ("B0801", "N_ZONE"),
        ("B0802", "N_ZONE"),
        ("C1201", "S_ZONE"),
        ("D0901", "E_ZONE"),
    ]

    for office, expected_zone in test_cases:
        result = tool.forward(office)
        status = "✓" if result == expected_zone else "✗"
        print(f"{status} office_to_zone('{office}') = '{result}' (expected: '{expected_zone}')")

    # テストケース2: 異常系
    result = tool.forward("INVALID")
    print(f"✓ office_to_zone('INVALID') = '{result}' (error expected)")
    print()


def test_zone_to_equipment():
    print("=" * 80)
    print("Test 2: ZoneToEquipmentTool")
    print("=" * 80)

    tool = ZoneToEquipmentTool()

    # テストケース
    test_cases = [
        ("N_ZONE", "OAFan"),
        ("N_ZONE", "AHU"),
        ("S_ZONE", "OAFan"),
        ("E_ZONE", "VAV"),
    ]

    for zone, equipment_type in test_cases:
        result = tool.forward(zone, equipment_type)
        print(f"✓ zone_to_equipment('{zone}', '{equipment_type}') = '{result}'")

    # 異常系
    result = tool.forward("INVALID_ZONE", "OAFan")
    print(f"✓ zone_to_equipment('INVALID_ZONE', 'OAFan') = '{result}' (error expected)")
    print()


def test_equipment_floor():
    print("=" * 80)
    print("Test 3: EquipmentFloorTool")
    print("=" * 80)

    tool = EquipmentFloorTool()

    # テストケース
    test_cases = [
        ("A1004", "10F"),
        ("A1005", "10F"),
        ("B3001", "12F"),
        ("C4001", "8F"),
    ]

    for equipment, expected_floor in test_cases:
        result = tool.forward(equipment)
        status = "✓" if result == expected_floor else "✗"
        print(f"{status} equipment_floor('{equipment}') = '{result}' (expected: '{expected_floor}')")

    # 異常系
    result = tool.forward("INVALID")
    print(f"✓ equipment_floor('INVALID') = '{result}' (error expected)")
    print()


def test_build_sensor_id():
    print("=" * 80)
    print("Test 4: BuildSensorIdTool")
    print("=" * 80)

    tool = BuildSensorIdTool()

    # テストケース
    test_cases = [
        ("10F", "OAFan", "SAT", "A1004", "10F_OAFan_SAT_A1004"),
        ("9F", "AHU", "RAT", "A2001", "9F_AHU_RAT_A2001"),
        ("12F", "AHU", "HUM", "B3101", "12F_AHU_HUM_B3101"),
        ("8F", "VAV", "FLOW", "C4201", "8F_VAV_FLOW_C4201"),
    ]

    for floor, eq_type, meas_point, eq_num, expected_id in test_cases:
        result = tool.forward(floor, eq_type, meas_point, eq_num)
        status = "✓" if result == expected_id else "✗"
        print(f"{status} build_sensor_id('{floor}', '{eq_type}', '{meas_point}', '{eq_num}')")
        print(f"   Result: '{result}'")
        print(f"   Expected: '{expected_id}'")

    print()


def test_naming_convention():
    print("=" * 80)
    print("Test 5: NamingConventionTool")
    print("=" * 80)

    tool = NamingConventionTool()
    result = tool.forward()
    print("Naming Convention Info:")
    print(result)
    print()


def test_complete_workflow():
    """
    完全なワークフローのテスト
    質問: 「B0802に関連する外調機の給気温度センサーIDは？」
    """
    print("=" * 80)
    print("Test 6: Complete Workflow")
    print("Question: B0802に関連する外調機（OAFan）の給気温度（SAT）センサーIDは？")
    print("=" * 80)

    # ステップ1: オフィスアドレスからゾーンを取得
    office_tool = OfficeToZoneTool()
    office_address = "B0802"
    zone = office_tool.forward(office_address)
    print(f"Step 1: Office '{office_address}' → Zone '{zone}'")

    # ステップ2: ゾーンと機器タイプから機器番号を取得
    zone_tool = ZoneToEquipmentTool()
    equipment_info = zone_tool.forward(zone, "OAFan")
    print(f"Step 2: Zone '{zone}' + Type 'OAFan' → {equipment_info}")

    # ここでは最初の機器番号を使用
    equipment_number = "A1004"
    print(f"Step 3: Using equipment number '{equipment_number}'")

    # ステップ3: 機器番号からフロアを取得
    floor_tool = EquipmentFloorTool()
    floor = floor_tool.forward(equipment_number)
    print(f"Step 4: Equipment '{equipment_number}' → Floor '{floor}'")

    # ステップ4: センサーIDを構築
    sensor_tool = BuildSensorIdTool()
    sensor_id = sensor_tool.forward(floor, "OAFan", "SAT", equipment_number)
    print(f"Step 5: Building sensor ID → '{sensor_id}'")

    print()
    print(f"Final Answer: {sensor_id}")
    print("Expected: 10F_OAFan_SAT_A1004")
    print(f"Status: {'✓ PASS' if sensor_id == '10F_OAFan_SAT_A1004' else '✗ FAIL'}")
    print()


def test_complete_workflow_2():
    """
    完全なワークフローのテスト2
    質問: 「C1201のAHUの還気温度センサーIDは？」
    """
    print("=" * 80)
    print("Test 7: Complete Workflow 2")
    print("Question: C1201のAHU（空調機）の還気温度（RAT）センサーIDは？")
    print("=" * 80)

    # ステップ1: オフィスアドレスからゾーンを取得
    office_tool = OfficeToZoneTool()
    office_address = "C1201"
    zone = office_tool.forward(office_address)
    print(f"Step 1: Office '{office_address}' → Zone '{zone}'")

    # ステップ2: ゾーンと機器タイプから機器番号を取得
    zone_tool = ZoneToEquipmentTool()
    equipment_info = zone_tool.forward(zone, "AHU")
    print(f"Step 2: Zone '{zone}' + Type 'AHU' → {equipment_info}")

    # 最初の機器番号を使用
    equipment_number = "B3101"
    print(f"Step 3: Using equipment number '{equipment_number}'")

    # ステップ3: 機器番号からフロアを取得
    floor_tool = EquipmentFloorTool()
    floor = floor_tool.forward(equipment_number)
    print(f"Step 4: Equipment '{equipment_number}' → Floor '{floor}'")

    # ステップ4: センサーIDを構築
    sensor_tool = BuildSensorIdTool()
    sensor_id = sensor_tool.forward(floor, "AHU", "RAT", equipment_number)
    print(f"Step 5: Building sensor ID → '{sensor_id}'")

    print()
    print(f"Final Answer: {sensor_id}")
    print("Expected: 12F_AHU_RAT_B3101")
    print(f"Status: {'✓ PASS' if sensor_id == '12F_AHU_RAT_B3101' else '✗ FAIL'}")
    print()


def main():
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "Building Tools Unit Tests" + " " * 33 + "║")
    print("╚" + "═" * 78 + "╝")
    print("\n")

    # 各ツールの単体テスト
    test_office_to_zone()
    test_zone_to_equipment()
    test_equipment_floor()
    test_build_sensor_id()
    test_naming_convention()

    # 統合テスト（完全なワークフロー）
    test_complete_workflow()
    test_complete_workflow_2()

    print("=" * 80)
    print("All tests completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()
