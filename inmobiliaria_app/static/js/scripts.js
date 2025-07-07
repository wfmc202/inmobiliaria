const API_BASE_URL = ''; // Como el frontend y backend están en el mismo origen por ahora

// --- Utilidades ---
function mostrarMensaje(elementoId, mensaje, esError = false) {
    const el = document.getElementById(elementoId);
    if (el) {
        el.textContent = mensaje;
        el.style.display = 'block';
        el.className = esError ? 'error-message' : 'success-message';
        setTimeout(() => el.style.display = 'none', 5000);
    }
}

// --- Funciones para Sectores (en admin_sectores_agentes.html) ---
async function cargarSectoresAdmin() {
    const listaSectores = document.getElementById('lista-sectores');
    if (!listaSectores) return;

    try {
        const response = await fetch(`${API_BASE_URL}/sectores`);
        if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
        const sectores = await response.json();

        listaSectores.innerHTML = ''; // Limpiar
        if (sectores.length === 0) {
            listaSectores.innerHTML = '<p>No hay sectores registrados.</p>';
            return;
        }
        sectores.forEach(sector => {
            const li = document.createElement('li');
            li.textContent = `${sector.nombre_sector} (${sector.ciudad}) ${sector.descripcion ? '- ' + sector.descripcion : ''}`;
            // Aquí se podrían añadir botones de editar/eliminar si se implementa esa funcionalidad
            listaSectores.appendChild(li);
        });
    } catch (error) {
        listaSectores.innerHTML = '<p>Error al cargar sectores.</p>';
        mostrarMensaje('error-admin', `Error cargando sectores: ${error.message}`, true);
        console.error('Error cargando sectores:', error);
    }
}

async function handleSubmitSector(event) {
    event.preventDefault();
    const form = event.target;
    const data = {
        nombre_sector: form.nombre_sector.value,
        ciudad: form.ciudad.value,
        descripcion: form.descripcion.value
    };

    try {
        const response = await fetch(`${API_BASE_URL}/sectores`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        if (!response.ok) throw new Error(result.error || `Error HTTP: ${response.status}`);

        mostrarMensaje('mensaje-admin', `Sector "${result.nombre_sector}" creado con ID: ${result.id}`);
        form.reset();
        cargarSectoresAdmin(); // Recargar lista
        cargarSectoresParaFormulario(); // Recargar en formulario de propiedades si existe
        cargarSectoresFiltro(); // Recargar en filtros si existe
    } catch (error) {
        mostrarMensaje('error-admin', `Error creando sector: ${error.message}`, true);
        console.error('Error creando sector:', error);
    }
}

// --- Funciones para Agentes (en admin_sectores_agentes.html) ---
async function cargarAgentesAdmin() {
    const listaAgentes = document.getElementById('lista-agentes');
    if (!listaAgentes) return;

    try {
        const response = await fetch(`${API_BASE_URL}/agentes`);
        if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
        const agentes = await response.json();

        listaAgentes.innerHTML = ''; // Limpiar
        if (agentes.length === 0) {
            listaAgentes.innerHTML = '<p>No hay agentes registrados.</p>';
            return;
        }
        agentes.forEach(agente => {
            const li = document.createElement('li');
            li.textContent = `${agente.nombre} - ${agente.email} ${agente.telefono ? '(' + agente.telefono + ')' : ''}`;
            listaAgentes.appendChild(li);
        });
    } catch (error) {
        listaAgentes.innerHTML = '<p>Error al cargar agentes.</p>';
        mostrarMensaje('error-admin', `Error cargando agentes: ${error.message}`, true);
        console.error('Error cargando agentes:', error);
    }
}

async function handleSubmitAgente(event) {
    event.preventDefault();
    const form = event.target;
    const data = {
        nombre: form.nombre.value,
        email: form.email.value,
        telefono: form.telefono.value
    };

    try {
        const response = await fetch(`${API_BASE_URL}/agentes`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        if (!response.ok) throw new Error(result.error || `Error HTTP: ${response.status}`);

        mostrarMensaje('mensaje-admin', `Agente "${result.nombre}" registrado con ID: ${result.id}`);
        form.reset();
        cargarAgentesAdmin(); // Recargar lista
        cargarAgentesParaFormulario(); // Recargar en formulario de propiedades si existe
    } catch (error) {
        mostrarMensaje('error-admin', `Error registrando agente: ${error.message}`, true);
        console.error('Error registrando agente:', error);
    }
}


// --- Funciones para el Formulario de Propiedades (formulario_propiedad.html) ---
async function cargarSectoresParaFormulario() {
    const selectSector = document.getElementById('sector');
    if (!selectSector) return;
    try {
        const response = await fetch(`${API_BASE_URL}/sectores`);
        const sectores = await response.json();
        selectSector.innerHTML = '<option value="">Seleccione un sector</option>'; // Opción por defecto
        sectores.forEach(sector => {
            const option = document.createElement('option');
            option.value = sector.id;
            option.textContent = `${sector.nombre_sector} (${sector.ciudad})`;
            selectSector.appendChild(option);
        });
    } catch (error) {
        console.error('Error cargando sectores para el formulario:', error);
        selectSector.innerHTML = '<option value="">Error al cargar sectores</option>';
    }
}

async function cargarAgentesParaFormulario() {
    const selectAgente = document.getElementById('agente');
    if (!selectAgente) return;
    try {
        const response = await fetch(`${API_BASE_URL}/agentes`);
        const agentes = await response.json();
        selectAgente.innerHTML = '<option value="">Seleccione un agente</option>'; // Opción por defecto
        agentes.forEach(agente => {
            const option = document.createElement('option');
            option.value = agente.id;
            option.textContent = `${agente.nombre} (${agente.email})`;
            selectAgente.appendChild(option);
        });
    } catch (error) {
        console.error('Error cargando agentes para el formulario:', error);
        selectAgente.innerHTML = '<option value="">Error al cargar agentes</option>';
    }
}

async function handleSubmitPropiedad(event) {
    event.preventDefault();
    const form = document.getElementById('propiedadForm');
    const propiedadId = form.propiedadId.value;

    // Convertir URLs de imágenes de string a array
    const imagenesInput = form.imagenes.value.trim();
    const imagenesArray = imagenesInput ? imagenesInput.split(',').map(url => url.trim()).filter(url => url) : [];

    const data = {
        titulo: form.titulo.value,
        descripcion: form.descripcion.value,
        precio: parseFloat(form.precio.value),
        tipo: form.tipo.value,
        sector_id: parseInt(form.sector_id.value),
        agente_id: parseInt(form.agente_id.value),
        habitaciones: form.habitaciones.value ? parseInt(form.habitaciones.value) : null,
        banos: form.banos.value ? parseInt(form.banos.value) : null,
        superficie: form.superficie.value ? parseFloat(form.superficie.value) : null,
        direccion_completa: form.direccion_completa.value,
        imagenes: imagenesArray
    };

    // Validaciones básicas
    if (!data.titulo || !data.precio || !data.tipo || !data.sector_id || !data.agente_id) {
        mostrarMensaje('error-respuesta', 'Por favor, complete todos los campos obligatorios.', true);
        return;
    }

    const url = propiedadId ? `${API_BASE_URL}/propiedades/${propiedadId}` : `${API_BASE_URL}/propiedades`;
    const method = propiedadId ? 'PUT' : 'POST';

    try {
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await response.json();

        if (!response.ok) throw new Error(result.error || `Error HTTP: ${response.status}`);

        const actionText = propiedadId ? 'actualizada' : 'creada';
        mostrarMensaje('mensaje-respuesta', `Propiedad ${actionText} exitosamente. ID: ${result.id || propiedadId}`);
        if (!propiedadId) { // Si es creación, limpiar. Si es edición, no.
            form.reset();
            document.getElementById('imagenes').value = ''; // Asegurar que el campo de texto de imágenes se limpia
        } else {
            // Podríamos recargar los datos del formulario si fuera necesario o redirigir
        }
        // Considerar redirigir al index o limpiar el form y cambiar título si es edición
        if(propiedadId) {
            document.getElementById('form-title').textContent = `Editar Propiedad (ID: ${propiedadId})`;
        } else {
             document.getElementById('form-title').textContent = 'Publicar Nueva Propiedad';
        }

    } catch (error) {
        mostrarMensaje('error-respuesta', `Error al guardar propiedad: ${error.message}`, true);
        console.error('Error guardando propiedad:', error);
    }
}

async function cargarDatosPropiedadParaEdicion(propiedadId) {
    const form = document.getElementById('propiedadForm');
    document.getElementById('form-title').textContent = `Editando Propiedad ID: ${propiedadId}`;
    form.propiedadId.value = propiedadId;

    try {
        const response = await fetch(`${API_BASE_URL}/propiedades/${propiedadId}`);
        if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
        const propiedad = await response.json();

        form.titulo.value = propiedad.titulo || '';
        form.descripcion.value = propiedad.descripcion || '';
        form.precio.value = propiedad.precio || '';
        form.tipo.value = propiedad.tipo || 'venta';
        // Esperar a que se carguen los selects para setearlos
        await cargarSectoresParaFormulario();
        form.sector_id.value = propiedad.sector_id || '';
        await cargarAgentesParaFormulario();
        form.agente_id.value = propiedad.agente_id || '';

        form.habitaciones.value = propiedad.habitaciones || '';
        form.banos.value = propiedad.banos || '';
        form.superficie.value = propiedad.superficie || '';
        form.direccion_completa.value = propiedad.direccion_completa || '';
        form.imagenes.value = propiedad.imagenes ? propiedad.imagenes.map(img => img.url).join(', ') : '';

    } catch (error) {
        mostrarMensaje('error-respuesta', `Error cargando datos de la propiedad para editar: ${error.message}`, true);
        console.error('Error cargando propiedad para edición:', error);
        // Redirigir o limpiar si falla la carga
        limpiarFormulario();
    }
}

function limpiarFormulario() {
    const form = document.getElementById('propiedadForm');
    form.reset();
    form.propiedadId.value = '';
    document.getElementById('imagenes').value = '';
    document.getElementById('form-title').textContent = 'Publicar Nueva Propiedad';
    mostrarMensaje('mensaje-respuesta', 'Formulario limpiado.', false);
    // Quitar el query param de la URL si existe
    if (window.history.pushState) {
        const newURL = window.location.pathname; // Solo la ruta, sin query params
        window.history.pushState({path:newURL}, '', newURL);
    }
}


// --- Funciones para el Listado de Propiedades (index.html) ---
async function cargarSectoresFiltro() {
    const selectSector = document.getElementById('filtro-sector');
    if (!selectSector) return;
    try {
        const response = await fetch(`${API_BASE_URL}/sectores`);
        const sectores = await response.json();
        selectSector.innerHTML = '<option value="">Todos</option>'; // Opción por defecto
        sectores.forEach(sector => {
            const option = document.createElement('option');
            option.value = sector.id;
            option.textContent = `${sector.nombre_sector} (${sector.ciudad})`;
            selectSector.appendChild(option);
        });
    } catch (error) {
        console.error('Error cargando sectores para filtro:', error);
        selectSector.innerHTML = '<option value="">Error al cargar</option>';
    }
}

async function cargarPropiedades() {
    const listaPropiedades = document.getElementById('lista-propiedades');
    if (!listaPropiedades) return;
    listaPropiedades.innerHTML = '<p>Cargando propiedades...</p>';

    // Construir URL con filtros
    let url = new URL(`${window.location.origin}/propiedades`);
    const filtroSector = document.getElementById('filtro-sector').value;
    const filtroTipo = document.getElementById('filtro-tipo').value;
    const filtroPrecioMin = document.getElementById('filtro-precio-min').value;
    const filtroPrecioMax = document.getElementById('filtro-precio-max').value;
    const filtroKeyword = document.getElementById('filtro-keyword').value;

    if (filtroSector) url.searchParams.append('sector_id', filtroSector);
    if (filtroTipo) url.searchParams.append('tipo', filtroTipo);
    if (filtroPrecioMin) url.searchParams.append('precio_min', filtroPrecioMin);
    if (filtroPrecioMax) url.searchParams.append('precio_max', filtroPrecioMax);
    if (filtroKeyword) url.searchParams.append('keyword', filtroKeyword);

    try {
        const response = await fetch(url.toString());
        if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
        const propiedades = await response.json();

        listaPropiedades.innerHTML = ''; // Limpiar antes de añadir nuevas
        if (propiedades.length === 0) {
            listaPropiedades.innerHTML = '<p>No se encontraron propiedades con los filtros aplicados.</p>';
            return;
        }

        propiedades.forEach(prop => {
            const card = document.createElement('div');
            card.className = 'propiedad-card';

            let imagenesHTML = '<p>Sin imágenes.</p>';
            if (prop.imagenes && prop.imagenes.length > 0) {
                imagenesHTML = prop.imagenes.map(img => `<img src="${img.url}" alt="${prop.titulo}" style="max-width:150px; margin-right:5px;">`).join('');
            }

            card.innerHTML = `
                <h3>${prop.titulo} (${prop.tipo})</h3>
                <p><strong>Precio:</strong> $${prop.precio.toLocaleString()}</p>
                <p><strong>Sector:</strong> ${prop.nombre_sector} (${prop.sector_ciudad})</p>
                <p><strong>Agente:</strong> ${prop.agente_nombre} (${prop.agente_email || 'Email no disponible'})</p>
                <p>${prop.descripcion || 'Sin descripción.'}</p>
                <p><strong>Habitaciones:</strong> ${prop.habitaciones || 'N/A'} | <strong>Baños:</strong> ${prop.banos || 'N/A'} | <strong>Superficie:</strong> ${prop.superficie || 'N/A'} m²</p>
                <p><strong>Dirección:</strong> ${prop.direccion_completa || 'No especificada'}</p>
                <div>${imagenesHTML}</div>
                <button onclick="mostrarDetallesPropiedad(${prop.id})">Ver Detalles</button>
                <a href="/formulario-propiedad?editar_id=${prop.id}" style="margin-left:10px;">Editar</a>
                <button onclick="eliminarPropiedad(${prop.id})" style="margin-left:10px; background-color:#d9534f;">Eliminar</button>
            `;
            listaPropiedades.appendChild(card);
        });

    } catch (error) {
        listaPropiedades.innerHTML = `<p>Error al cargar propiedades: ${error.message}</p>`;
        console.error('Error cargando propiedades:', error);
    }
}

async function mostrarDetallesPropiedad(propiedadId) {
    const modal = document.getElementById('propiedadModal');
    const contenidoModal = document.getElementById('detallesPropiedadContenido');
    contenidoModal.innerHTML = '<p>Cargando detalles...</p>';
    modal.style.display = "block";

    try {
        const response = await fetch(`${API_BASE_URL}/propiedades/${propiedadId}`);
        if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
        const prop = await response.json(); // Esta respuesta ya debería tener la info de sector y agente

        let imagenesHTML = '<p>Sin imágenes.</p>';
        if (prop.imagenes && prop.imagenes.length > 0) {
            imagenesHTML = prop.imagenes.map(img => `<img src="${img.url}" alt="${prop.titulo}" style="max-width:200px; margin:5px;">`).join('');
        }

        // Usar los campos directos si existen (del JOIN), o los IDs como fallback.
        const nombreSector = prop.nombre_sector ? `${prop.nombre_sector} (${prop.sector_ciudad})` : `Sector ID: ${prop.sector_id}`;
        const nombreAgente = prop.agente_nombre ? `${prop.agente_nombre} (${prop.agente_email || 'N/A'})` : `Agente ID: ${prop.agente_id}`;

        contenidoModal.innerHTML = `
            <h2>${prop.titulo}</h2>
            <p><strong>Tipo:</strong> ${prop.tipo}</p>
            <p><strong>Precio:</strong> $${prop.precio.toLocaleString()}</p>
            <p><strong>Descripción:</strong> ${prop.descripcion || 'N/A'}</p>
            <p><strong>Sector:</strong> ${nombreSector}</p>
            <p><strong>Agente:</strong> ${nombreAgente}</p>
            <p><strong>Habitaciones:</strong> ${prop.habitaciones || 'N/A'}</p>
            <p><strong>Baños:</strong> ${prop.banos || 'N/A'}</p>
            <p><strong>Superficie:</strong> ${prop.superficie || 'N/A'} m²</p>
            <p><strong>Dirección:</strong> ${prop.direccion_completa || 'N/A'}</p>
            <p><strong>Publicado:</strong> ${new Date(prop.fecha_publicacion).toLocaleDateString()}</p>
            <p><strong>Última Actualización:</strong> ${new Date(prop.fecha_actualizacion).toLocaleDateString()}</p>
            <div><strong>Imágenes:</strong><br>${imagenesHTML}</div>
        `;
    } catch (error) {
        contenidoModal.innerHTML = `<p>Error al cargar detalles de la propiedad: ${error.message}</p>`;
        console.error('Error mostrando detalles:', error);
    }
}

function cerrarModalDetalles() {
    const modal = document.getElementById('propiedadModal');
    modal.style.display = "none";
}

// Cerrar modal si se hace clic fuera del contenido
window.onclick = function(event) {
    const modal = document.getElementById('propiedadModal');
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

async function eliminarPropiedad(propiedadId) {
    if (!confirm(`¿Está seguro de que desea eliminar la propiedad ID ${propiedadId}? Esta acción no se puede deshacer.`)) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/propiedades/${propiedadId}`, {
            method: 'DELETE'
        });
        const result = await response.json(); // Flask devuelve JSON incluso en DELETE exitoso

        if (!response.ok) {
            throw new Error(result.error || `Error HTTP: ${response.status}`);
        }

        alert(result.mensaje || 'Propiedad eliminada exitosamente.');
        cargarPropiedades(); // Recargar la lista de propiedades
    } catch (error) {
        alert(`Error al eliminar la propiedad: ${error.message}`);
        console.error('Error mostrando detalles:', error);
    }
}

function cerrarModalDetalles() {
    const modal = document.getElementById('propiedadModal');
    modal.style.display = "none";
}

// Cerrar modal si se hace clic fuera del contenido
window.onclick = function(event) {
    const modal = document.getElementById('propiedadModal');
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

async function eliminarPropiedad(propiedadId) {
    if (!confirm(`¿Está seguro de que desea eliminar la propiedad ID ${propiedadId}? Esta acción no se puede deshacer.`)) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/propiedades/${propiedadId}`, {
            method: 'DELETE'
        });
        const result = await response.json(); // Flask devuelve JSON incluso en DELETE exitoso

        if (!response.ok) {
            throw new Error(result.error || `Error HTTP: ${response.status}`);
        }

        alert(result.mensaje || 'Propiedad eliminada exitosamente.');
        cargarPropiedades(); // Recargar la lista de propiedades
    } catch (error) {
        alert(`Error al eliminar la propiedad: ${error.message}`);
        console.error('Error eliminando propiedad:', error);
    }
}

// --- Inicialización específica por página (ya se maneja en los bloques <script> de cada HTML) ---
// Ejemplo:
// if (document.getElementById('lista-propiedades')) {
//     window.onload = () => {
//        cargarSectoresFiltro();
//        cargarPropiedades();
//     };
// }
// (Esta lógica ya está en los HTML, lo cual es bueno para este nivel de simplicidad)
console.log("scripts.js cargado.");
