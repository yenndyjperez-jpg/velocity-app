import os
import random
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox

# Importamos el backend de tu archivo moto.py
import moto

# Estilos de Interfaz (Modo Oscuro)
BG_NEGRO_ABS = "#0A0A0B"
BG_TARJETA = "#141416"
AZUL_NEON = "#00E5FF"
TEXTO_PRINCIPAL = "#F4F4F7"
TEXTO_MUTED = "#72767D"
BORDE_SUAVE = "#232428"

def crear_campo_entrada(parent, label_text):
    """Crea campos de texto estilizados usando tkinter nativo."""
    tk.Label(parent, text=label_text.upper(), font=("Segoe UI", 8, "bold"), bg=BG_TARJETA, fg=TEXTO_MUTED).pack(anchor="w", pady=(8, 3))
    borde_custom = tk.Frame(parent, bg=BORDE_SUAVE, bd=1, padx=6, pady=5)
    borde_custom.pack(fill="x", pady=(0, 4))
    entry = tk.Entry(borde_custom, font=("Segoe UI", 10), bg=BG_TARJETA, fg=TEXTO_PRINCIPAL, bd=0, highlightthickness=0, insertbackground=AZUL_NEON)
    entry.pack(fill="x")
    return entry

# ==================== REGISTRO DE PASAJERO ====================
def abrir_registro_usuario():
    v_user = tk.Toplevel(ventana_principal)
    v_user.title("Registro Pasajero - VeloCity")
    v_user.geometry("380x380")
    v_user.config(bg=BG_NEGRO_ABS)
    v_user.resizable(False, False)

    card = tk.Frame(v_user, bg=BG_TARJETA, padx=20, pady=15)
    card.pack(fill="both", expand=True, padx=20, pady=20)

    tk.Label(card, text="REGISTRO DE PASAJERO", font=("Segoe UI Semibold", 13), bg=BG_TARJETA, fg=TEXTO_PRINCIPAL).pack(anchor="w")

    entry_nom = crear_campo_entrada(card, "Nombre Completo")
    entry_tel = crear_campo_entrada(card, "Teléfono / Móvil")
    entry_cor = crear_campo_entrada(card, "Correo Electrónico")

    def guardar_usuario():
        nom = entry_nom.get().strip()
        tel = entry_tel.get().strip()
        cor = entry_cor.get().strip()

        if not nom or not tel:
            messagebox.showerror("Error", "El nombre y el teléfono son obligatorios.")
            return

        exito, msg = moto.registrar_usuario(nom, tel, cor)
        if exito:
            messagebox.showinfo("Éxito", "Usuario registrado correctamente.")
            v_user.destroy()
        else:
            messagebox.showerror("Error", msg)

    btn = tk.Button(card, text="REGISTRARSE", bg=AZUL_NEON, fg=BG_NEGRO_ABS, font=("Segoe UI", 9, "bold"), bd=0, height=2, cursor="hand2", command=guardar_usuario)
    btn.pack(fill="x", pady=(15, 0))

# ==================== REGISTRO DE CONDUCTOR ====================
def abrir_registro_conductor():
    ventana_cond = tk.Toplevel(ventana_principal)
    ventana_cond.title("Registro Conductor - VeloCity")
    ventana_cond.geometry("460x720")
    ventana_cond.config(bg=BG_NEGRO_ABS)
    ventana_cond.resizable(False, False)
    
    main_frame = tk.Frame(ventana_cond, bg=BG_NEGRO_ABS, padx=25, pady=15)
    main_frame.pack(fill="both", expand=True)

    tk.Label(main_frame, text="REGISTRO Y VERIFICACIÓN", font=("Segoe UI Semibold", 14), bg=BG_NEGRO_ABS, fg=TEXTO_PRINCIPAL).pack(anchor="w")
    
    rutas_fotos = {'perfil': None, 'ext': None, 'int': None, 'licencia': None, 'docs': None}

    entry_nombre = crear_campo_entrada(main_frame, "Nombre Completo")
    entry_cedula = crear_campo_entrada(main_frame, "Cédula de Identidad")
    entry_licencia = crear_campo_entrada(main_frame, "Nro. Licencia")
    entry_placa = crear_campo_entrada(main_frame, "Placa del Vehículo")
    entry_localidad = crear_campo_entrada(main_frame, "Zona/Localidad")

    tk.Label(main_frame, text="TIPO DE VEHÍCULO", font=("Segoe UI", 8, "bold"), bg=BG_NEGRO_ABS, fg=TEXTO_MUTED).pack(anchor="w", pady=(10, 2))
    var_tipo = tk.StringVar(value="Moto")
    
    frame_tipo = tk.Frame(main_frame, bg=BG_NEGRO_ABS)
    frame_tipo.pack(fill="x", pady=2)
    tk.Radiobutton(frame_tipo, text="Moto 🏍️", variable=var_tipo, value="Moto", bg=BG_NEGRO_ABS, fg=TEXTO_PRINCIPAL, selectcolor=BG_TARJETA, font=("Segoe UI", 9)).pack(side="left", padx=(0, 20))
    tk.Radiobutton(frame_tipo, text="Carro 🚗", variable=var_tipo, value="Carro", bg=BG_NEGRO_ABS, fg=TEXTO_PRINCIPAL, selectcolor=BG_TARJETA, font=("Segoe UI", 9)).pack(side="left")

    tk.Label(main_frame, text="DOCUMENTACIÓN Y FOTOS (5)", font=("Segoe UI", 8, "bold"), bg=BG_NEGRO_ABS, fg=AZUL_NEON).pack(anchor="w", pady=(12, 4))

    def seleccionar_foto(clave, boton_widget):
        archivo = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[("Imágenes", "*.jpg *.jpeg *.png")]
        )
        if archivo:
            rutas_fotos[clave] = archivo
            nombre_corto = os.path.basename(archivo)[:15] + "..."
            boton_widget.config(text=f"✓ {nombre_corto}", fg="#00FF66")

    def crear_boton_foto(texto_label, clave):
        frame = tk.Frame(main_frame, bg=BG_TARJETA, padx=8, pady=3)
        frame.pack(fill="x", pady=2)
        tk.Label(frame, text=texto_label, font=("Segoe UI", 8), bg=BG_TARJETA, fg=TEXTO_PRINCIPAL).pack(side="left")
        
        btn = tk.Button(frame, text="Subir 📷", bg=BORDE_SUAVE, fg=TEXTO_PRINCIPAL, font=("Segoe UI", 8, "bold"), bd=0, padx=8, pady=2, cursor="hand2")
        btn.config(command=lambda b=btn: seleccionar_foto(clave, b))
        btn.pack(side="right")

    crear_boton_foto("1. Foto de Perfil", 'perfil')
    crear_boton_foto("2. Exterior del Vehículo", 'ext')
    crear_boton_foto("3. Interior del Vehículo", 'int')
    crear_boton_foto("4. Licencia de Conducir", 'licencia')
    crear_boton_foto("5. Documentos / Título", 'docs')

    def procesar_registro():
        if not entry_nombre.get() or not entry_cedula.get() or not entry_placa.get():
            messagebox.showerror("Error", "Completa todos los datos obligatorios.")
            return

        if None in rutas_fotos.values():
            messagebox.showwarning("Fotos Faltantes", "Debes adjuntar las 5 imágenes solicitadas.")
            return

        exito, msg = moto.registrar_conductor_completo(
            entry_nombre.get().strip(),
            entry_cedula.get().strip(),
            entry_licencia.get().strip(),
            entry_placa.get().strip(),
            var_tipo.get(),
            entry_localidad.get().strip(),
            rutas_fotos
        )

        if exito:
            messagebox.showinfo("Éxito", f"Unidad ({var_tipo.get()}) registrada correctamente.")
            ventana_cond.destroy()
        else:
            messagebox.showerror("Error", msg)

    btn_guardar = tk.Button(main_frame, text="ENVIAR VERIFICACIÓN", bg=AZUL_NEON, fg=BG_NEGRO_ABS, font=("Segoe UI", 10, "bold"), bd=0, height=2, cursor="hand2", command=procesar_registro)
    btn_guardar.pack(fill="x", pady=(15, 0))

# ==================== SOLICITUD DE VIAJE ====================
def abrir_solicitud_viaje():
    ventana_cliente = tk.Toplevel(ventana_principal)
    ventana_cliente.title("Solicitud - VeloCity")
    ventana_cliente.geometry("420x510")
    ventana_cliente.config(bg=BG_NEGRO_ABS)
    ventana_cliente.resizable(False, False)
    
    tk.Label(ventana_cliente, text="NUEVO VIAJE", font=("Segoe UI Semibold", 15), bg=BG_NEGRO_ABS, fg=TEXTO_PRINCIPAL).pack(pady=(20, 5))
    card = tk.Frame(ventana_cliente, bg=BG_TARJETA, padx=25, pady=15)
    card.pack(fill="both", expand=True, padx=25, pady=(5, 20))
    
    entry_nombre = crear_campo_entrada(card, "Tu Nombre")
    
    # Campo de Ubicación con Botón GPS
    tk.Label(card, text="UBICACIÓN / ORIGEN", font=("Segoe UI", 8, "bold"), bg=BG_TARJETA, fg=TEXTO_MUTED).pack(anchor="w", pady=(8, 3))
    
    frame_ubi = tk.Frame(card, bg=BG_TARJETA)
    frame_ubi.pack(fill="x", pady=(0, 4))

    borde_custom = tk.Frame(frame_ubi, bg=BORDE_SUAVE, bd=1, padx=6, pady=5)
    borde_custom.pack(side="left", fill="x", expand=True, padx=(0, 5))
    
    entry_ubicacion = tk.Entry(borde_custom, font=("Segoe UI", 10), bg=BG_TARJETA, fg=TEXTO_PRINCIPAL, bd=0, highlightthickness=0, insertbackground=AZUL_NEON)
    entry_ubicacion.pack(fill="x")

    def obtener_gps():
        btn_gps.config(text="Obteniendo...", state="disabled")
        ventana_cliente.update_idletasks()
        
        # Simulación de lectura GPS / Coordenadas
        time.sleep(0.8)
        lat = round(10.13 + random.uniform(-0.02, 0.02), 5)
        lon = round(-64.69 + random.uniform(-0.02, 0.02), 5)
        
        entry_ubicacion.delete(0, tk.END)
        entry_ubicacion.insert(0, f"GPS ({lat}, {lon})")
        btn_gps.config(text="📍 GPS", state="normal")

    btn_gps = tk.Button(frame_ubi, text="📍 GPS", bg=BORDE_SUAVE, fg=AZUL_NEON, font=("Segoe UI", 8, "bold"), bd=0, padx=8, pady=5, cursor="hand2", command=obtener_gps)
    btn_gps.pack(side="right")

    tk.Label(card, text="TIPO DE TRANSPORTE", font=("Segoe UI", 8, "bold"), bg=BG_TARJETA, fg=TEXTO_MUTED).pack(anchor="w", pady=(10, 4))
    
    var_preferencia = tk.StringVar(value="Moto")
    tk.Radiobutton(card, text="Moto Rapid 🏍️", variable=var_preferencia, value="Moto", bg=BG_TARJETA, fg=TEXTO_PRINCIPAL, selectcolor=BG_NEGRO_ABS, font=("Segoe UI", 9)).pack(anchor="w", pady=2)
    tk.Radiobutton(card, text="Carro Confort 🚗", variable=var_preferencia, value="Carro", bg=BG_TARJETA, fg=TEXTO_PRINCIPAL, selectcolor=BG_NEGRO_ABS, font=("Segoe UI", 9)).pack(anchor="w", pady=2)

    def solicitar_servicio():
        nombre = entry_nombre.get().strip()
        ubicacion = entry_ubicacion.get().strip()
        tipo = var_preferencia.get()
        
        if not nombre or not ubicacion:
            messagebox.showerror("Error", "Indica tu nombre y ubicación.")
            return
        
        viaje_id = moto.crear_solicitud_viaje(nombre, ubicacion, tipo)
        cond_nombre = moto.buscar_conductor_disponible(viaje_id, tipo)

        if cond_nombre:
            messagebox.showinfo("¡Match Encontrado!", f"Se te ha asignado al conductor: {cond_nombre}")
            ventana_cliente.destroy()
        else:
            messagebox.showwarning("Sin Unidades", f"No hay unidades disponibles de tipo '{tipo}' por ahora.")

    btn_acc = tk.Button(card, text="CONFIRMAR Y SOLICITAR", bg=AZUL_NEON, fg=BG_NEGRO_ABS, font=("Segoe UI", 10, "bold"), bd=0, height=2, cursor="hand2", command=solicitar_servicio)
    btn_acc.pack(fill="x", pady=(15, 0))

# ==================== VENTANA PRINCIPAL ====================
moto.inicializar_base_datos()

ventana_principal = tk.Tk()
ventana_principal.title("VeloCity Central")
ventana_principal.geometry("400x450")
ventana_principal.config(bg=BG_NEGRO_ABS)
ventana_principal.resizable(False, False)

tk.Label(ventana_principal, text="VELOCITY", font=("Segoe UI Black", 24), bg=BG_NEGRO_ABS, fg=AZUL_NEON).pack(pady=(30, 2))
tk.Label(ventana_principal, text="Plataforma de Movilidad Urbana", font=("Segoe UI", 9), bg=BG_NEGRO_ABS, fg=TEXTO_MUTED).pack(pady=(0, 15))

frame_botones = tk.Frame(ventana_principal, bg=BG_NEGRO_ABS)
frame_botones.pack(fill="x", padx=45, pady=5)

btn_solicitar = tk.Button(frame_botones, text="SOLICITAR UN VIAJE", bg=AZUL_NEON, fg=BG_NEGRO_ABS, font=("Segoe UI", 10, "bold"), height=2, bd=0, cursor="hand2", command=abrir_solicitud_viaje)
btn_solicitar.pack(fill="x", pady=6)

btn_reg_user = tk.Button(frame_botones, text="REGISTRARSE COMO PASAJERO", bg=BG_TARJETA, fg=TEXTO_PRINCIPAL, font=("Segoe UI", 9, "bold"), height=2, bd=0, cursor="hand2", command=abrir_registro_usuario)
btn_reg_user.pack(fill="x", pady=6)

btn_conductor = tk.Button(frame_botones, text="REGISTRAR VEHÍCULO / CONDUCTOR", bg=BG_TARJETA, fg=AZUL_NEON, font=("Segoe UI", 9, "bold"), height=2, bd=0, cursor="hand2", command=abrir_registro_conductor)
btn_conductor.pack(fill="x", pady=6)

ventana_principal.mainloop()