import sqlite3

DB_NAME = "inmobiliaria.db"

def crear_conexion():
    """Crea una conexión a la base de datos SQLite."""
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        print(f"Conexión a SQLite DB '{DB_NAME}' exitosa.")
    except sqlite3.Error as e:
        print(f"Error al conectar a SQLite DB: {e}")
    return conn

def crear_tablas(conn):
    """Crea las tablas en la base de datos."""
    try:
        cursor = conn.cursor()

        # Tabla de Sectores
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sectores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_sector TEXT NOT NULL,
                ciudad TEXT NOT NULL,
                descripcion TEXT,
                UNIQUE(nombre_sector, ciudad)
            );
        """)
        print("Tabla 'sectores' creada o ya existente.")

        # Tabla de Agentes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agentes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                telefono TEXT,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("Tabla 'agentes' creada o ya existente.")

        # Tabla de Propiedades
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS propiedades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                descripcion TEXT,
                precio REAL NOT NULL,
                tipo TEXT NOT NULL CHECK(tipo IN ('venta', 'alquiler')),
                sector_id INTEGER NOT NULL,
                agente_id INTEGER NOT NULL,
                habitaciones INTEGER,
                banos INTEGER,
                superficie REAL,
                direccion_completa TEXT,
                fecha_publicacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sector_id) REFERENCES sectores (id),
                FOREIGN KEY (agente_id) REFERENCES agentes (id)
            );
        """)
        # Nota: La columna 'imagenes' de la clase Propiedad se manejará de forma diferente
        # podría ser una tabla separada (propiedad_imagenes) o una lista de URLs almacenada como JSON/TEXT.
        # Por simplicidad inicial, no la crearé directamente en esta tabla SQL.
        # Podríamos tener una tabla 'imagenes_propiedad' (id_propiedad, url_imagen, orden)
        print("Tabla 'propiedades' creada o ya existente.")

        # Tabla para Imágenes de Propiedades (Normalización)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS propiedad_imagenes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                propiedad_id INTEGER NOT NULL,
                url_imagen TEXT NOT NULL,
                orden INTEGER DEFAULT 0, -- Para ordenar las imágenes si es necesario
                FOREIGN KEY (propiedad_id) REFERENCES propiedades (id) ON DELETE CASCADE
            );
        """)
        print("Tabla 'propiedad_imagenes' creada o ya existente.")


        conn.commit()
    except sqlite3.Error as e:
        print(f"Error al crear tablas: {e}")

def inicializar_base_de_datos():
    """Inicializa la base de datos: crea conexión y tablas."""
    conn = crear_conexion()
    if conn is not None:
        crear_tablas(conn)
        conn.close()
        print(f"Base de datos '{DB_NAME}' inicializada y tablas creadas.")
    else:
        print("No se pudo establecer conexión con la base de datos.")

if __name__ == '__main__':
    print("Inicializando la base de datos...")
    inicializar_base_de_datos()

    # Insertar datos iniciales de ejemplo
    print("Intentando insertar datos iniciales de ejemplo...")
    conn_ejemplos = crear_conexion() # Reabrir conexión para los datos de ejemplo
    if conn_ejemplos:
        try:
            cursor = conn_ejemplos.cursor()
            # Insertar Sector de Ejemplo
            try:
                cursor.execute("INSERT INTO sectores (nombre_sector, ciudad, descripcion) VALUES (?, ?, ?)",
                               ("Centro Histórico", "Ciudad Capital", "Casco antiguo con monumentos"))
                print("Sector 'Centro Histórico' insertado.")
            except sqlite3.IntegrityError:
                print("Sector 'Centro Histórico' ya existe.")

            try:
                cursor.execute("INSERT INTO sectores (nombre_sector, ciudad, descripcion) VALUES (?, ?, ?)",
                               ("Zona Norte Residencial", "Ciudad Capital", "Área tranquila con parques"))
                print("Sector 'Zona Norte Residencial' insertado.")
            except sqlite3.IntegrityError:
                print("Sector 'Zona Norte Residencial' ya existe.")

            # Insertar Agente de Ejemplo
            try:
                cursor.execute("INSERT INTO agentes (nombre, email, telefono) VALUES (?, ?, ?)",
                               ("Carlos Pérez", "carlos.perez@inmobiliaria.test", "555-0011"))
                print("Agente 'Carlos Pérez' (ID probable 1) insertado.")
            except sqlite3.IntegrityError:
                print("Agente 'Carlos Pérez' ya existe.")

            try:
                cursor.execute("INSERT INTO agentes (nombre, email, telefono) VALUES (?, ?, ?)",
                               ("Laura Gómez", "laura.gomez@inmobiliaria.test", "555-0022"))
                print("Agente 'Laura Gómez' (ID probable 2) insertado.")
            except sqlite3.IntegrityError:
                print("Agente 'Laura Gómez' ya existe.")

            conn_ejemplos.commit()
            print("Datos iniciales de ejemplo procesados.")
        except sqlite3.Error as e:
            print(f"Error insertando datos de ejemplo: {e}")
        finally:
            conn_ejemplos.close()
