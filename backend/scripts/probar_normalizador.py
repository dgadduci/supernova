from backend.utils.text_normalizer import normalizar_texto


def main() -> None:
    ejemplos = [
        "  Pizzas  ",
        "PÍZZAS",
        "Empanada   de   Jamón y Queso",
        "MUZZARELLA",
        "  Coca Cola   1,5 L  ",
    ]

    for ejemplo in ejemplos:
        print(f"{ejemplo!r} -> {normalizar_texto(ejemplo)!r}")


if __name__ == "__main__":
    main()