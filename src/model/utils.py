from src.model.enums import MeteoFranceDataType

def meteofrance_data_type_to_str(meteofrance_data_type: MeteoFranceDataType) -> str:
    match meteofrance_data_type:
        case MeteoFranceDataType.SIM2_QUOT:
            return "QUOT-SIM2"
        case MeteoFranceDataType.SIM2_MENS:
            return "MENS-SIM2"
        case MeteoFranceDataType.QUOT:
            return "QUOT"
        case MeteoFranceDataType.MENS:
            return "MENS"
        case _:
            raise NotImplementedError("MeteoFrance Data Type pas implémenté : " + meteofrance_data_type)
