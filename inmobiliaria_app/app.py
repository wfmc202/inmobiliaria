import sqlite3
from flask import Flask, request, jsonify, render_template

# Configuración inicial de la aplicación Flask
app = Flask(__name__)
DB_NAME = "../inmobiliaria.db" # Ruta relativa desde app.py a la BD
# app.config['DATABASE'] = DB_NAME # Otra forma de configurar, útil con extensiones

def get_db_connection():
    """Establece conexión con la base de datos."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row # Permite acceder a las columnas por nombre
    return conn

# --- Endpoints para Sectores ---

@app.route('/sectores', methods=['POST'])
def crear_sector():
    """
    Crea un nuevo sector.
    Espera un JSON con: nombre_sector (str), ciudad (str), [descripcion (str, opcional)]
    """
    datos = request.get_json()
    if not datos or not datos.get('nombre_sector') or not datos.get('ciudad'):
        return jsonify({"error": "Faltan datos requeridos: nombre_sector y ciudad"}), 400

    nombre_sector = datos['nombre_sector']
    ciudad = datos['ciudad']
    descripcion = datos.get('descripcion')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sectores (nombre_sector, ciudad, descripcion) VALUES (?, ?, ?)",
            (nombre_sector, ciudad, descripcion)
        )
        conn.commit()
        sector_id = cursor.lastrowid
        conn.close()
        return jsonify({"mensaje": "Sector creado exitosamente", "id": sector_id, "nombre_sector": nombre_sector, "ciudad": ciudad}), 201
    except sqlite3.IntegrityError: # Ocurre si se viola la constraint UNIQUE(nombre_sector, ciudad)
        conn.close()
        return jsonify({"error": f"El sector '{nombre_sector}' en la ciudad '{ciudad}' ya existe."}), 409 # 409 Conflict
    except sqlite3.Error as e:
        if conn:
            conn.close()
        return jsonify({"error": f"Error en la base de datos: {str(e)}"}), 500


@app.route('/sectores', methods=['GET'])
def listar_sectores():
    """Lista todos los sectores."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre_sector, ciudad, descripcion FROM sectores")
        sectores = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(sectores), 200
    except sqlite3.Error as e:
        if conn:
            conn.close()
        return jsonify({"error": f"Error en la base de datos: {str(e)}"}), 500

# --- Endpoints para Agentes (se añadirán aquí) ---

@app.route('/agentes', methods=['POST'])
def registrar_agente():
    """
    Registra un nuevo agente.
    Espera un JSON con: nombre (str), email (str), [telefono (str, opcional)]
    """
    datos = request.get_json()
    if not datos or not datos.get('nombre') or not datos.get('email'):
        return jsonify({"error": "Faltan datos requeridos: nombre y email"}), 400

    nombre = datos['nombre']
    email = datos['email']
    telefono = datos.get('telefono')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO agentes (nombre, email, telefono) VALUES (?, ?, ?)",
            (nombre, email, telefono)
        )
        conn.commit()
        agente_id = cursor.lastrowid
        conn.close()
        return jsonify({"mensaje": "Agente registrado exitosamente", "id": agente_id, "nombre": nombre, "email": email}), 201
    except sqlite3.IntegrityError: # Ocurre si se viola la constraint UNIQUE(email)
        conn.close()
        return jsonify({"error": f"El email '{email}' ya está registrado."}), 409
    except sqlite3.Error as e:
        if conn:
            conn.close()
        return jsonify({"error": f"Error en la base de datos: {str(e)}"}), 500

@app.route('/agentes', methods=['GET'])
def listar_agentes():
    """Lista todos los agentes."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, email, telefono, fecha_registro FROM agentes")
        agentes = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(agentes), 200
    except sqlite3.Error as e:
        if conn:
            conn.close()
        return jsonify({"error": f"Error en la base de datos: {str(e)}"}), 500

@app.route('/agentes/<int:agente_id>', methods=['GET'])
def obtener_agente(agente_id):
    """Obtiene detalles de un agente específico por su ID."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, email, telefono, fecha_registro FROM agentes WHERE id = ?", (agente_id,))
        agente = cursor.fetchone()
        conn.close()
        if agente:
            return jsonify(dict(agente)), 200
        else:
            return jsonify({"error": "Agente no encontrado"}), 404
    except sqlite3.Error as e:
        if conn:
            conn.close()
        return jsonify({"error": f"Error en la base de datos: {str(e)}"}), 500

# --- Endpoints para Propiedades ---

@app.route('/propiedades', methods=['POST'])
def crear_propiedad():
    """
    Crea una nueva propiedad.
    Espera JSON con: titulo, precio, tipo ('venta'/'alquiler'), sector_id,
                     [descripcion, habitaciones, banos, superficie, direccion_completa, imagenes (lista de URLs)]
    Requiere header 'X-Agente-ID' para autenticación.
    """
    # Autenticación básica simulada
    agente_id_auth = request.headers.get('X-Agente-ID')
    if not agente_id_auth:
        return jsonify({"error": "Autenticación requerida: Falta header X-Agente-ID"}), 401

    try:
        agente_id_auth = int(agente_id_auth)
    except ValueError:
        return jsonify({"error": "Header X-Agente-ID inválido: debe ser un número entero."}), 400

    datos = request.get_json()
    # 'agente_id' ya no se toma del body, sino del header. 'sector_id' sí.
    requeridos = ['titulo', 'precio', 'tipo', 'sector_id']
    if not datos or not all(field in datos for field in requeridos):
        return jsonify({"error": f"Faltan datos requeridos en el cuerpo JSON: {', '.join(requeridos)}"}), 400

    if datos['tipo'] not in ['venta', 'alquiler']:
        return jsonify({"error": "El tipo de propiedad debe ser 'venta' o 'alquiler'"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Validar existencia del agente_id_auth
    cursor.execute("SELECT id FROM agentes WHERE id = ?", (agente_id_auth,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"error": f"Agente con ID {agente_id_auth} (del header X-Agente-ID) no encontrado o no válido."}), 403 # 403 Forbidden

    # Validar existencia de sector_id
    cursor.execute("SELECT id FROM sectores WHERE id = ?", (datos['sector_id'],))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"error": f"Sector con id {datos['sector_id']} no encontrado."}), 404

    try:
        # Insertar propiedad principal
        sql = """INSERT INTO propiedades
                 (titulo, descripcion, precio, tipo, sector_id, agente_id,
                  habitaciones, banos, superficie, direccion_completa, fecha_actualizacion)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)"""
        params = (
            datos['titulo'], datos.get('descripcion'), datos['precio'], datos['tipo'],
            datos['sector_id'], agente_id_auth, # Usar agente_id_auth del header
            datos.get('habitaciones'), datos.get('banos'),
            datos.get('superficie'), datos.get('direccion_completa')
        )
        cursor.execute(sql, params)
        propiedad_id = cursor.lastrowid

        # Insertar imágenes si se proporcionan
        imagenes_urls = datos.get('imagenes', [])
        if imagenes_urls and isinstance(imagenes_urls, list):
            for i, url_imagen in enumerate(imagenes_urls):
                if isinstance(url_imagen, str): # Asegurar que es una URL válida podría ser más robusto
                    cursor.execute(
                        "INSERT INTO propiedad_imagenes (propiedad_id, url_imagen, orden) VALUES (?, ?, ?)",
                        (propiedad_id, url_imagen, i)
                    )

        conn.commit()
        conn.close()
        # Devolver la propiedad creada (sin las imágenes aquí por simplicidad, se pueden obtener con GET)
        return jsonify({
            "mensaje": "Propiedad creada exitosamente",
            "id": propiedad_id,
            **datos # Devuelve los datos enviados para confirmación
        }), 201

    except sqlite3.Error as e:
        if conn:
            conn.rollback() # Importante hacer rollback en caso de error
            conn.close()
        return jsonify({"error": f"Error en la base de datos al crear propiedad: {str(e)}"}), 500


@app.route('/propiedades', methods=['GET'])
def listar_propiedades():
    """
    Lista todas las propiedades.
    Admite filtros opcionales en query string: sector_id, tipo, precio_min, precio_max.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Modificamos la query para incluir nombres de sector y agente
    query = """
        SELECT
            p.*,
            s.nombre_sector,
            s.ciudad as sector_ciudad,
            a.nombre as agente_nombre,
            a.email as agente_email
        FROM propiedades p
        JOIN sectores s ON p.sector_id = s.id
        JOIN agentes a ON p.agente_id = a.id
    """
    filters = []
    params = []

    # Filtros
    if 'sector_id' in request.args:
        filters.append("p.sector_id = ?")
        params.append(request.args['sector_id'])
    if 'tipo' in request.args:
        filters.append("p.tipo = ?")
        params.append(request.args['tipo'])
    if 'precio_min' in request.args:
        filters.append("p.precio >= ?")
        params.append(request.args['precio_min'])
    if 'precio_max' in request.args:
        filters.append("p.precio <= ?")
        params.append(request.args['precio_max'])
    # Se podrían añadir más filtros: habitaciones, agente_id, etc.
    if 'keyword' in request.args and request.args['keyword']: # Filtro por palabra clave
        keyword = f"%{request.args['keyword']}%"
        # Añadir OR para buscar en múltiples campos (titulo y descripción)
        # Asegurarse de que el keyword filter se agrupa correctamente con AND si hay otros filtros
        keyword_filter_group = "(p.titulo LIKE ? OR p.descripcion LIKE ?)"
        filters.append(keyword_filter_group)
        params.extend([keyword, keyword])


    if filters:
        query += " WHERE " + " AND ".join(filters)

    query += " ORDER BY p.fecha_actualizacion DESC" # Ordenar por más recientes

    try:
        cursor.execute(query, params)
        propiedades_raw = cursor.fetchall()

        propiedades_list = []
        for prop_row in propiedades_raw:
            prop_dict = dict(prop_row)
            # Obtener imágenes para cada propiedad
            # Esta subconsulta N+1 podría optimizarse más adelante si el rendimiento se vuelve un problema
            # (ej. agrupando URLs en la query principal o con otra query que traiga todas las imágenes de una vez)
            cursor.execute("SELECT url_imagen, orden FROM propiedad_imagenes WHERE propiedad_id = ? ORDER BY orden", (prop_dict['id'],))
            imagenes = [{"url": img_row['url_imagen'], "orden": img_row['orden']} for img_row in cursor.fetchall()]
            prop_dict['imagenes'] = imagenes
            propiedades_list.append(prop_dict)

        conn.close()
        return jsonify(propiedades_list), 200
    except sqlite3.Error as e:
        if conn:
            conn.close()
        return jsonify({"error": f"Error en la base de datos al listar propiedades: {str(e)}"}), 500


@app.route('/propiedades/<int:propiedad_id>', methods=['GET'])
def obtener_propiedad(propiedad_id):
    """Obtiene detalles de una propiedad específica, incluyendo sus imágenes."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Modificamos la query para incluir nombres de sector y agente
        query = """
            SELECT
                p.*,
                s.nombre_sector,
                s.ciudad as sector_ciudad,
                a.nombre as agente_nombre,
                a.email as agente_email
            FROM propiedades p
            LEFT JOIN sectores s ON p.sector_id = s.id  -- LEFT JOIN por si acaso un sector/agente es borrado y la FK no está bien manejada
            LEFT JOIN agentes a ON p.agente_id = a.id
            WHERE p.id = ?
        """
        cursor.execute(query, (propiedad_id,))
        propiedad = cursor.fetchone()

        if not propiedad:
            conn.close()
            return jsonify({"error": "Propiedad no encontrada"}), 404

        propiedad_dict = dict(propiedad)

        # Obtener imágenes
        cursor.execute("SELECT url_imagen, orden FROM propiedad_imagenes WHERE propiedad_id = ? ORDER BY orden", (propiedad_id,))
        imagenes = [{"url": img_row['url_imagen'], "orden": img_row['orden']} for img_row in cursor.fetchall()]
        propiedad_dict['imagenes'] = imagenes

        conn.close()
        return jsonify(propiedad_dict), 200
    except sqlite3.Error as e:
        if conn:
            conn.close()
        return jsonify({"error": f"Error en la base de datos: {str(e)}"}), 500


@app.route('/propiedades/<int:propiedad_id>', methods=['PUT'])
def actualizar_propiedad(propiedad_id):
    """
    Actualiza una propiedad existente.
    Espera JSON con los campos a actualizar. No permite cambiar agente_id ni sector_id directamente.
    Requiere header 'X-Agente-ID'. Solo el agente dueño puede actualizar.
    """
    # Autenticación básica simulada
    agente_id_auth = request.headers.get('X-Agente-ID')
    if not agente_id_auth:
        return jsonify({"error": "Autenticación requerida: Falta header X-Agente-ID"}), 401
    try:
        agente_id_auth = int(agente_id_auth)
    except ValueError:
        return jsonify({"error": "Header X-Agente-ID inválido: debe ser un número entero."}), 400

    datos = request.get_json()
    if not datos:
        return jsonify({"error": "No se enviaron datos para actualizar"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Verificar si la propiedad existe y obtener su agente_id original
    cursor.execute("SELECT id, agente_id FROM propiedades WHERE id = ?", (propiedad_id,))
    propiedad_actual = cursor.fetchone()
    if not propiedad_actual:
        conn.close()
        return jsonify({"error": "Propiedad no encontrada"}), 404

    # Autorización: Verificar si el agente autenticado es el dueño de la propiedad
    if propiedad_actual['agente_id'] != agente_id_auth:
        conn.close()
        return jsonify({"error": "Autorización denegada: No tiene permiso para modificar esta propiedad."}), 403

    # Campos permitidos para actualización
    # Permitimos cambiar sector_id, pero no agente_id (ya que está ligado al "dueño")
    campos_actualizables = ['titulo', 'descripcion', 'precio', 'tipo', 'sector_id',
                            'habitaciones', 'banos', 'superficie', 'direccion_completa']

    sql_set_parts = []
    params = []

    for campo in campos_actualizables:
        if campo in datos:
            sql_set_parts.append(f"{campo} = ?")
            params.append(datos[campo])

    if not sql_set_parts:
        conn.close()
        return jsonify({"error": "No hay campos válidos para actualizar"}), 400

    sql_set_parts.append("fecha_actualizacion = CURRENT_TIMESTAMP") # Actualizar siempre la fecha

    sql = f"UPDATE propiedades SET {', '.join(sql_set_parts)} WHERE id = ?"
    params.append(propiedad_id)

    try:
        cursor.execute(sql, params)
        # Manejo de imágenes: si se envían 'imagenes', se reemplazan todas las existentes.
        # Esto es una simplificación. Una API más robusta tendría endpoints dedicados para añadir/eliminar imágenes.
        if 'imagenes' in datos and isinstance(datos['imagenes'], list):
            # 1. Eliminar imágenes antiguas
            cursor.execute("DELETE FROM propiedad_imagenes WHERE propiedad_id = ?", (propiedad_id,))
            # 2. Insertar imágenes nuevas
            for i, url_imagen in enumerate(datos['imagenes']):
                 if isinstance(url_imagen, str):
                    cursor.execute(
                        "INSERT INTO propiedad_imagenes (propiedad_id, url_imagen, orden) VALUES (?, ?, ?)",
                        (propiedad_id, url_imagen, i)
                    )

        conn.commit()
        conn.close()

        # Devolver la propiedad actualizada (se podría hacer una nueva consulta)
        return jsonify({"mensaje": "Propiedad actualizada exitosamente", "id": propiedad_id}), 200
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
            conn.close()
        return jsonify({"error": f"Error en la base de datos al actualizar propiedad: {str(e)}"}), 500


@app.route('/propiedades/<int:propiedad_id>', methods=['DELETE'])
def eliminar_propiedad(propiedad_id):
    """
    Elimina una propiedad (y sus imágenes asociadas gracias a ON DELETE CASCADE).
    Requiere header 'X-Agente-ID'. Solo el agente dueño puede eliminar.
    """
    # Autenticación básica simulada
    agente_id_auth = request.headers.get('X-Agente-ID')
    if not agente_id_auth:
        return jsonify({"error": "Autenticación requerida: Falta header X-Agente-ID"}), 401
    try:
        agente_id_auth = int(agente_id_auth)
    except ValueError:
        return jsonify({"error": "Header X-Agente-ID inválido: debe ser un número entero."}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Verificar si la propiedad existe y obtener su agente_id original
        cursor.execute("SELECT id, agente_id FROM propiedades WHERE id = ?", (propiedad_id,))
        propiedad_actual = cursor.fetchone()
        if not propiedad_actual:
            conn.close()
            return jsonify({"error": "Propiedad no encontrada"}), 404

        # Autorización: Verificar si el agente autenticado es el dueño de la propiedad
        if propiedad_actual['agente_id'] != agente_id_auth:
            conn.close()
            return jsonify({"error": "Autorización denegada: No tiene permiso para eliminar esta propiedad."}), 403

        cursor.execute("DELETE FROM propiedades WHERE id = ?", (propiedad_id,))
        # Las imágenes se eliminan automáticamente por la FK `ON DELETE CASCADE` en `propiedad_imagenes`
        conn.commit()

        if cursor.rowcount > 0: # rowcount será 1 si la eliminación fue exitosa
            conn.close()
            return jsonify({"mensaje": "Propiedad eliminada exitosamente"}), 200
        else:
            # Esto teóricamente no debería alcanzarse si la propiedad existía y la autorización pasó,
            # a menos que haya una condición de carrera muy improbable o un error en la lógica.
            conn.close()
            return jsonify({"error": "Error al eliminar la propiedad o propiedad ya no existe."}), 500 # O 404 si se prefiere

    except sqlite3.Error as e:
        if conn:
            conn.rollback()
            conn.close()
        return jsonify({"error": f"Error en la base de datos al eliminar propiedad: {str(e)}"}), 500

# --- Rutas para servir las páginas HTML del Frontend ---

@app.route('/')
def index():
    """Sirve la página principal que lista propiedades."""
    return render_template('index.html')

@app.route('/formulario-propiedad')
def vista_formulario_propiedad():
    """Sirve la página con el formulario para crear/editar propiedades."""
    # El ID para editar se pasará como query param ?editar_id=X
    return render_template('formulario_propiedad.html')

@app.route('/admin-sectores-agentes')
def vista_admin_sectores_agentes():
    """Sirve la página para administrar sectores y agentes."""
    return render_template('admin_sectores_agentes.html')


if __name__ == '__main__':
    # Se recomienda no usar app.run() en producción directamente así.
    # Usar un servidor WSGI como Gunicorn o Waitress.
    app.run(debug=True, port=5000)
