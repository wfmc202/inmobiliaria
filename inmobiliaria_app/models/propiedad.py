from datetime import datetime

class Propiedad:
    def __init__(self, id, titulo, descripcion, precio, tipo, sector_id, agente_id,
                 habitaciones, banos, superficie, direccion_completa, fecha_publicacion=None, imagenes=None):
        self.id = id
        self.titulo = titulo
        self.descripcion = descripcion
        self.precio = precio  # Podría ser un float o Decimal
        self.tipo = tipo  # "venta" o "alquiler"
        self.sector_id = sector_id  # ID del sector al que pertenece
        self.agente_id = agente_id  # ID del agente que la publica
        self.habitaciones = habitaciones  # int
        self.banos = banos  # int
        self.superficie = superficie  # float, en m²
        self.direccion_completa = direccion_completa # str, dirección textual
        self.imagenes = imagenes if imagenes is not None else []  # Lista de URLs o paths a imágenes
        self.fecha_publicacion = fecha_publicacion if fecha_publicacion is not None else datetime.utcnow()
        self.fecha_actualizacion = datetime.utcnow()

    def __repr__(self):
        return f"<Propiedad {self.id}: {self.titulo}>"

    def actualizar_detalles(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)
        self.fecha_actualizacion = datetime.utcnow()

    def agregar_imagen(self, url_imagen):
        self.imagenes.append(url_imagen)
        self.fecha_actualizacion = datetime.utcnow()

    # Más métodos podrían ser añadidos aquí, como validaciones, etc.
