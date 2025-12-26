INDICES = {
    "NDVI": {
        "num": "B08",
        "den": "B04",
        "legend": [
            (-1.0, 0.0, "Brak roślinności"),
            (0.0, 0.2, "Bardzo słaba roślinność"),
            (0.2, 0.4, "Umiarkowana roślinność"),
            (0.4, 0.6, "Dobra roślinność"),
            (0.6, 1.0, "Bardzo dobra roślinność"),
        ],
        "cmap": "RdYlGn",
    },
    "NDWI": {
        "num": "B03",
        "den": "B08",
        "legend": [
            (-1.0, 0.0, "Suchy obszar"),
            (0.0, 0.3, "Wilgotny teren"),
            (0.3, 1.0, "Woda"),
        ],
        "cmap": "Blues",
    },
    "NDBI": {
        "num": "B11",
        "den": "B08",
        "legend": [
            (-1.0, 0.0, "Teren niezabudowany"),
            (0.0, 0.3, "Zabudowa rozproszona"),
            (0.3, 1.0, "Zabudowa intensywna"),
        ],
        "cmap": "inferno",
    },
}
