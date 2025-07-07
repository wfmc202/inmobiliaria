from datetime import datetime

class Agente:
    def __init__(self, id, nombre, email, telefono, fecha_registro=None):
        self.id = id
        self.nombre = nombre
        self.email = email
        self.telefono = telefono
        self.fecha_registro = fecha_registro if fecha_registro is not None else datetime.utcnow()
        self.propiedades_publicadas_ids = [] # Lista de IDs de propiedades publicadas por este agente

    def __repr__(self):
        return f"<Agente {self.id}: {self.nombre}>"

    def actualizar_contacto(self, nombre=None, email=None, telefono=None):
        if nombre:
            self.nombre = nombre
        if email:
            self.email = email
        if telefono:
            self.telefono = telefono

    def agregar_propiedad_publicada(self, propiedad_id):
        if propiedad_id not in self.propiedades_publicadas_ids:
            self.propiedades_publicadas_ids.append(propiedad_id)

    # Más métodos relacionados con el agente pueden ir aquí.
