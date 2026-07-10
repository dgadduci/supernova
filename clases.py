from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Categoria:
    id: int
    nombre: str

@dataclass
class Producto:
    id: int
    id_descripcion: int
    nombre: str
    descripcion: str
    precio: float
    stock: int

@dataclass
class Cliente:
    id: int
    nombre: str
    calle: str
    numeracion: str = None  # Usualmente es texto para permitir letras (ej. "123-A")
    piso: Optional[str] = None
    departamento: Optional[str] = None
    referencias: Optional[str] = None
    whatsapp: Optional[str] = None

@dataclass
class Comercio:
    id: int
    nombre: str
    cuit: str = None
    calle: str = None
    altura: int = None
    departamento: str = None
    whatsapp: str = None
    piso: Optional[int] = None  # Opcional, no todos los comercios tienen piso específico si es local comercial en planta baja
    dias_laboral: List[str] = field(default_factory=list) 
    horario_1_laboral: str = ""
    horario_2_laboral: Optional[str] = None  # Opcional, no todos tienen dos franjas horarias
    retiro_local: bool = False
    delivery: bool = False

@dataclass
class MedioDePago:
    id: int
    descripcion: str = ""
    titular: str = ""
    alias: str = ""
    
@dataclass
class FormaDeEntrega:
    id: id
    descripcion: str = ""

