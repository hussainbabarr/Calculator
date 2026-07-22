"""Unit conversion helpers kept separate from the view."""

UNITS = {
    "Length": {"Meter": 1, "Kilometer": 1000, "Mile": 1609.344, "Foot": .3048, "Inch": .0254},
    "Weight": {"Kilogram": 1, "Gram": .001, "Pound": .45359237, "Ounce": .0283495},
    "Time": {"Second": 1, "Minute": 60, "Hour": 3600, "Day": 86400},
    "Speed": {"m/s": 1, "km/h": .2777778, "mph": .44704},
    "Data Storage": {"Byte": 1, "KB": 1024, "MB": 1048576, "GB": 1073741824},
    "Area": {"m²": 1, "km²": 1e6, "ft²": .092903},
    "Volume": {"Liter": 1, "Milliliter": .001, "Gallon": 3.78541},
    "Pressure": {"Pascal": 1, "Bar": 100000, "PSI": 6894.76},
    "Energy": {"Joule": 1, "Kilojoule": 1000, "Calorie": 4.184},
    "Power": {"Watt": 1, "Kilowatt": 1000, "Horsepower": 745.7},
}


def convert_unit(category: str, value: float, source: str, target: str) -> float:
    if category == "Temperature":
        celsius = value - 273.15 if source == "Kelvin" else (value - 32) * 5 / 9 if source == "Fahrenheit" else value
        return celsius + 273.15 if target == "Kelvin" else celsius * 9 / 5 + 32 if target == "Fahrenheit" else celsius
    units = UNITS[category]
    return value * units[source] / units[target]