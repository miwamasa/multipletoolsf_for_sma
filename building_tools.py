"""
ビル管理システムの命名規則に関する情報を提供するツール群

各ツールは情報を分散して保持し、エージェントが推論を通じて
必要な情報を組み合わせられるように設計されています。
"""

from smolagents import Tool


class OfficeToZoneTool(Tool):
    name = "office_to_zone"
    description = """
    This tool returns the zone identifier for a given office address.

    Input: office_address (str) - Office address code (e.g., 'B0801', 'B0802', 'C1201')
    Output: zone identifier (str) - Zone name (e.g., 'N_ZONE', 'S_ZONE', 'E_ZONE')

    Use this tool when you need to find which zone an office belongs to.
    Example: office_to_zone('B0801') returns 'N_ZONE'
    """

    inputs = {
        "office_address": {
            "type": "string",
            "description": "The office address code (e.g., B0801, B0802)"
        }
    }
    output_type = "string"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # オフィスアドレス → ゾーンのマッピング
        self.office_zone_map = {
            "B0801": "N_ZONE",
            "B0802": "N_ZONE",
            "B0803": "N_ZONE",
            "C1201": "S_ZONE",
            "C1202": "S_ZONE",
            "D0901": "E_ZONE",
            "D0902": "E_ZONE",
        }

    def forward(self, office_address: str) -> str:
        office_address = office_address.strip().upper()
        zone = self.office_zone_map.get(office_address)
        if zone is None:
            return f"Error: Office address '{office_address}' not found in database"
        return zone


class ZoneToEquipmentTool(Tool):
    name = "zone_to_equipment"
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

    inputs = {
        "zone": {
            "type": "string",
            "description": "Zone identifier (e.g., N_ZONE, S_ZONE, E_ZONE)"
        },
        "equipment_type": {
            "type": "string",
            "description": "Equipment type: 'OAFan', 'AHU', or 'VAV'"
        }
    }
    output_type = "string"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # ゾーンと機器タイプ → 機器番号のマッピング
        self.zone_equipment_map = {
            ("N_ZONE", "OAFan"): ["A1004", "A1005"],
            ("N_ZONE", "AHU"): ["A2001", "A2002"],
            ("S_ZONE", "OAFan"): ["B3001"],
            ("S_ZONE", "AHU"): ["B3101", "B3102"],
            ("E_ZONE", "OAFan"): ["C4001"],
            ("E_ZONE", "VAV"): ["C4201", "C4202", "C4203"],
        }

    def forward(self, zone: str, equipment_type: str) -> str:
        zone = zone.strip().upper()
        equipment_type = equipment_type.strip()

        key = (zone, equipment_type)
        equipment_numbers = self.zone_equipment_map.get(key)

        if equipment_numbers is None:
            return f"Error: No equipment of type '{equipment_type}' found in zone '{zone}'"

        return f"Equipment numbers: {', '.join(equipment_numbers)}"


class BuildSensorIdTool(Tool):
    name = "build_sensor_id"
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

    inputs = {
        "floor": {
            "type": "string",
            "description": "Floor number with 'F' suffix (e.g., 10F)"
        },
        "equipment_type": {
            "type": "string",
            "description": "Equipment type: OAFan, AHU, or VAV"
        },
        "measurement_point": {
            "type": "string",
            "description": "Measurement point: SAT, RAT, OAT, HUM, or FLOW"
        },
        "equipment_number": {
            "type": "string",
            "description": "Equipment number (e.g., A1004)"
        }
    }
    output_type = "string"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 機器番号 → フロアのマッピング
        self.equipment_floor_map = {
            "A1004": "10F",
            "A1005": "10F",
            "A2001": "9F",
            "A2002": "9F",
            "B3001": "12F",
            "B3101": "12F",
            "B3102": "12F",
            "C4001": "8F",
            "C4201": "8F",
            "C4202": "8F",
            "C4203": "8F",
        }

    def forward(self, floor: str, equipment_type: str, measurement_point: str,
                equipment_number: str) -> str:
        # パラメータの検証
        equipment_number = equipment_number.strip()

        # 機器番号からフロアを検証（オプション）
        expected_floor = self.equipment_floor_map.get(equipment_number)
        if expected_floor and expected_floor != floor:
            return f"Warning: Equipment {equipment_number} is on {expected_floor}, not {floor}. Using {expected_floor}."

        # センサーIDの構築
        if expected_floor:
            floor = expected_floor

        sensor_id = f"{floor}_{equipment_type}_{measurement_point}_{equipment_number}"
        return sensor_id


class EquipmentFloorTool(Tool):
    name = "equipment_floor"
    description = """
    This tool returns the floor number where a specific equipment is located.

    Input: equipment_number (str) - Equipment number (e.g., 'A1004', 'B3001')
    Output: floor (str) - Floor number with 'F' suffix (e.g., '10F', '12F')

    Use this tool when you have an equipment number and need to know which floor it's on.
    Example: equipment_floor('A1004') returns '10F'
    """

    inputs = {
        "equipment_number": {
            "type": "string",
            "description": "Equipment number (e.g., A1004)"
        }
    }
    output_type = "string"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.equipment_floor_map = {
            "A1004": "10F",
            "A1005": "10F",
            "A2001": "9F",
            "A2002": "9F",
            "B3001": "12F",
            "B3101": "12F",
            "B3102": "12F",
            "C4001": "8F",
            "C4201": "8F",
            "C4202": "8F",
            "C4203": "8F",
        }

    def forward(self, equipment_number: str) -> str:
        equipment_number = equipment_number.strip().upper()
        floor = self.equipment_floor_map.get(equipment_number)
        if floor is None:
            return f"Error: Equipment number '{equipment_number}' not found"
        return floor


class NamingConventionTool(Tool):
    name = "naming_convention"
    description = """
    This tool explains the naming convention rules for building sensors and equipment.

    Input: None or query type (optional)
    Output: Explanation of naming conventions (str)

    Use this tool to understand:
    - How sensor IDs are structured
    - What each component means
    - Available equipment types and measurement points

    The general format is: {Floor}_{EquipmentType}_{MeasurementPoint}_{EquipmentNumber}
    Example: 10F_OAFan_SAT_A1004
        - 10F: 10th floor
        - OAFan: Outdoor Air Fan unit (外調機)
        - SAT: Supply Air Temperature (給気温度)
        - A1004: Equipment identifier
    """

    inputs = {}
    output_type = "string"

    def forward(self) -> str:
        return """
Building Sensor Naming Convention:

Format: {Floor}_{EquipmentType}_{MeasurementPoint}_{EquipmentNumber}

Components:
1. Floor: Floor number with 'F' suffix (e.g., 10F, 5F)
2. EquipmentType:
   - OAFan: Outdoor Air Handling Unit (外調機)
   - AHU: Air Handling Unit (空調機)
   - VAV: Variable Air Volume unit
3. MeasurementPoint:
   - SAT: Supply Air Temperature (給気温度)
   - RAT: Return Air Temperature (還気温度)
   - OAT: Outdoor Air Temperature (外気温度)
   - HUM: Humidity (湿度)
   - FLOW: Air Flow (風量)
4. EquipmentNumber: Unique identifier for the equipment (e.g., A1004)

Example: 10F_OAFan_SAT_A1004
This represents the Supply Air Temperature sensor of the Outdoor Air Fan unit
A1004 located on the 10th floor.

To find a sensor ID:
1. Find the zone for your office address
2. Find equipment serving that zone
3. Get the floor for that equipment
4. Build the sensor ID with the measurement point you need
"""
