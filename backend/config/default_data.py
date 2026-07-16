from dataclasses import dataclass


@dataclass(frozen=True)
class PresentacionPorDefecto:
    codigo: str
    descripcion: str
    activo: bool
    orden: int


PRESENTACIONES_POR_DEFECTO: tuple[PresentacionPorDefecto, ...] = (
    PresentacionPorDefecto(
        codigo="unidad",
        descripcion="Unidad",
        activo=True,
        orden=1,
    ),
    PresentacionPorDefecto(
        codigo="porcion",
        descripcion="Porción",
        activo=True,
        orden=2,
    ),
    PresentacionPorDefecto(
        codigo="chica",
        descripcion="Chica",
        activo=True,
        orden=3,
    ),
    PresentacionPorDefecto(
        codigo="mediana",
        descripcion="Mediana",
        activo=True,
        orden=4,
    ),
    PresentacionPorDefecto(
        codigo="grande",
        descripcion="Grande",
        activo=True,
        orden=5,
    ),
    PresentacionPorDefecto(
        codigo="familiar",
        descripcion="Familiar",
        activo=True,
        orden=6,
    ),
    PresentacionPorDefecto(
        codigo="lata",
        descripcion="Lata",
        activo=True,
        orden=7,
    ),
    PresentacionPorDefecto(
        codigo="500_ml",
        descripcion="500 ml",
        activo=True,
        orden=8,
    ),
    PresentacionPorDefecto(
        codigo="1_litro",
        descripcion="1 litro",
        activo=True,
        orden=9,
    ),
    PresentacionPorDefecto(
        codigo="1_5_litros",
        descripcion="1,5 litros",
        activo=True,
        orden=10,
    ),
    PresentacionPorDefecto(
        codigo="2_litros",
        descripcion="2 litros",
        activo=True,
        orden=11,
    ),
)