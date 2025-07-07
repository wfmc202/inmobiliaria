class Sector:
    def __init__(self, id, nombre_sector, ciudad, descripcion=None):
        self.id = id
        self.nombre_sector = nombre_sector
        self.ciudad = ciudad # Ej: "Ciudad de México", "Guadalajara"
        self.descripcion = descripcion # Opcional, para más detalles del sector

    def __repr__(self):
        return f"<Sector {self.id}: {self.nombre_sector} ({self.ciudad})>"

    def actualizar_detalles(self, nombre_sector=None, ciudad=None, descripcion=None):
        if nombre_sector:
            self.nombre_sector = nombre_sector
        if ciudad:
            self.ciudad = ciudad
        if descripcion is not None: # Permitir borrar la descripción pasándola como ""
            self.descripcion = descripcion

    # Podríamos añadir una lista de propiedades_ids si quisiéramos navegar desde el sector,
    # pero usualmente se filtra por propiedad.sector_id == sector.id
