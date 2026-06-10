import tkinter as tk
from tkinter import messagebox, ttk
import math
import subprocess
import os
from BibliotecaAlgoritmos import BibliotecaAlgoritmos

class QuantumStudio:
    # Inicio de la interfaz gráfica
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Estudio Cuántico - Diseños Industriales")
        self.ventana.geometry("1200x850")
        self.ventana.configure(bg="#0B111E")

        # Variables de estado
        self.filas, self.columnas = 3, 3
        self.n_nodos = 16
        self.aristas = set()
        self.qubits = []
        self.parejas = []
        self.nodo_elegido = None
        self.primera_pareja = None

        # Opciones de control 
        # Creamos un marco a la izquierda de la ventana
        marco_control = tk.Frame(ventana, bg="#131B27", width=300)
        marco_control.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Opciones para seleccionar una placa base por defecto
        
        tk.Label(marco_control, text="PRESETS INDUSTRIALES", fg="#D39F19", bg="#101620", font=("Arial", 11, "bold")).pack(pady=15)
        # Creamos el menu usando StringVar para guardar el texto
        self.var_preset = tk.StringVar()
        self.menu_desplegable = ttk.Combobox(marco_control, textvariable=self.var_preset, state="readonly")
        # Guardamos los nombres principales de las empresas de las placas
        self.menu_desplegable['values'] = ("IBM Vigo", "IBM Yorktown", "Heavy-Hex", "Google Sycamore")
        self.menu_desplegable.pack(pady=5, padx=10, fill=tk.X)
        
        # Creamos el boton de iniciar guardar la arquitectura
        tk.Button(marco_control, text="Cargar Arquitectura", command=self.cargar_preset, bg="#B86505", fg="white").pack(pady=5, fill=tk.X, padx=20)

        # Separamos de las otras secciones con una linea horizontal
        ttk.Separator(marco_control, orient='horizontal').pack(fill='x', pady=20)


        # Opciones personalizadas del usuario
        
        tk.Label(marco_control, text="PERSONALIZAR", fg="#33B3E9", bg="#0F141D", font=("Arial", 11, "bold")).pack(pady=10)
        
        dimensiones_marco = tk.Frame(marco_control, bg="#151D29")
        dimensiones_marco.pack()
        
        # Utilizamos la dimensión que marque el usuario y por defecto 4x4
        self.dimension_filas = tk.Entry(dimensiones_marco, width=3)
        self.dimension_filas.insert(0, "3")
        self.dimension_filas.pack(side=tk.LEFT, padx=2)
        
        tk.Label(dimensiones_marco, text="x", fg="white", bg="#141C28").pack(side=tk.LEFT)
        
        self.dimension_columnas = tk.Entry(dimensiones_marco, width=3)
        self.dimension_columnas.insert(0, "3")
        self.dimension_columnas.pack(side=tk.LEFT, padx=2)
        
        tk.Button(marco_control, text="Generar Cuadrícula", command=self.generar_cuadricula, bg="#505D6F", fg="white").pack(pady=5, fill=tk.X, padx=20)

        
        # Añadimos un apartado para la seleccion de algoritmos 
        ttk.Separator(marco_control, orient='horizontal').pack(fill='x', pady=10)
        tk.Label(marco_control, text="ALGORITMOS CUÁNTICOS", fg="#1AD496", bg="#182438", font=("Arial", 11, "bold")).pack(pady=10)
        
        self.var_algoritmo = tk.StringVar()
        self.menu_algoritmo = ttk.Combobox(marco_control, textvariable=self.var_algoritmo, state="readonly")
        self.menu_algoritmo['values'] = ("Manual", "Estado de Bell", "Sumador Cuántico", "Corrección Errores")
         # Por defecto lo dejamos en manual
        self.menu_algoritmo.current(0)
        self.menu_algoritmo.pack(pady=5, padx=10, fill=tk.X)
        
        tk.Button(marco_control, text="Cargar Algoritmo", command=self.cargar_algoritmo, bg="#059669", fg="white").pack(pady=5, fill=tk.X, padx=20)
        
        ttk.Separator(marco_control, orient='horizontal').pack(fill='x', pady=20)
        
        
        # Botones para personalizar la cuadricula
        tk.Label(marco_control, text="HERRAMIENTAS", fg="#38BDF8", bg="#1E293B", font=("Arial", 11, "bold")).pack(pady=15)
        self.modo = tk.StringVar(value="qubit")
        tk.Radiobutton(marco_control, text="Situar Qubits", variable=self.modo, value="qubit", bg="#1E293B", fg="white", selectcolor="#0F172A").pack(anchor="w", padx=30)
        tk.Radiobutton(marco_control, text="Dibujar Cables", variable=self.modo, value="arista", bg="#1E293B", fg="white", selectcolor="#0F172A").pack(anchor="w", padx=30)
        tk.Radiobutton(marco_control, text="Definir Parejas", variable=self.modo, value="pareja", bg="#1E293B", fg="white", selectcolor="#0F172A").pack(anchor="w", padx=30)

        # Eliminar todos los cambios sobre la cuadricula
        tk.Button(marco_control, text="Limpiar Todo", command=self.limpiar_todo, bg="#991B1B", fg="white").pack(pady=20, fill=tk.X, padx=20)

        # boton para ejecutar 
        btn_run = tk.Button(marco_control, text="GUARDAR Y SIMULAR", command=self.ejecutar_simulacion, bg="#10B981", fg="white", font=("Arial", 12, "bold"), pady=15)
        btn_run.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=20)

        # Creamos la parte visual del lienzo
        self.lienzo = tk.Canvas(ventana, bg="#0F172A", highlightthickness=0)
        self.lienzo.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        # Param marcar los clicks sobre el lienzo de la derecha
        self.lienzo.bind("<Button-1>", self.click_en_lienzo)
        
        # Para evitar errores al principio obligamos a que vuelva a hacer los calculos
        self.ventana.update()
        
        # Creamos la cuadricula por defecto
        self.generar_cuadricula()

    def cargar_preset(self):
        # Guardamos la placa base que elige el usuario
        eleccion = self.var_preset.get()
        # Borramos la anterior
        self.aristas.clear()
        self.qubits.clear()
        self.parejas.clear()
        
        # Cargamos la placa base elegida
        if eleccion == "IBM Vigo":
            self.filas, self.columnas, self.n_nodos = 3, 3, 5
            self.aristas = {(1,2), (2,3), (2,4), (4,5)}
        elif eleccion == "IBM Yorktown":
            self.filas, self.columnas, self.n_nodos = 3, 3, 5
            self.aristas = {(1,2), (1,3), (2,3), (3,4), (3,5), (4,5)}
        elif eleccion == "Heavy-Hex":
            self.filas, self.columnas, self.n_nodos = 4, 4, 16
            self.aristas = {(1,2),(2,3),(3,4),(1,5),(4,8),(5,6),(6,7),(7,8),(5,9),(8,12),
                            (9,10),(10,11),(11,12),(9,13),(12,16),(13,14),(14,15),(15,16)}
        elif eleccion == "Google Sycamore":
            # Es la que usamos por defecto
            self.generar_cuadricula() 
            return
            
        self.dibujar_lienzo()

    # Borrar una cuadricula entera
    def limpiar_todo(self):
        self.aristas.clear()
        self.qubits.clear() 
        self.parejas.clear()
        self.dibujar_lienzo()
        
    # Generar la cuadricula por defecto 4x4
    def generar_cuadricula(self):
        try:
            self.filas, self.columnas = int(self.dimension_filas.get()), int(self.dimension_columnas.get())
            self.n_nodos = self.filas * self.columnas
            self.aristas.clear()
            self.qubits.clear()
            self.parejas.clear()
            for r in range(self.filas):
                for c in range(self.columnas):
                    # Calculamos la posicion del nodo
                    n = r * self.columnas + c + 1
                    # Los nodos crean la arista con el nodo que tienen a la derecha
                    if c < self.columnas - 1: self.aristas.add((n, n+1))
                    # Crean la arista con el que tienen debajo
                    if r < self.filas - 1: self.aristas.add((n, n+self.columnas))
            self.dibujar_lienzo()
        except: 
            messagebox.showerror("Error", "Introduce números enteros mayores que 0")

    def get_coord_nodo(self, id_nodo):
        # Obtenemos las dimensiones del programa y si da 0 porque esta iniciando o por error
        # utilizamos 800
        ancho, alto = self.lienzo.winfo_width() or 800, self.lienzo.winfo_height() or 800
        
        # Calculamos los pixeles de separación entre cada nodo
        mx, my = ancho / (self.columnas + 1), alto / (self.filas + 1)
        # Calculamos la fila y la columna en funcion del numero del nodo
        f, c = (id_nodo-1)//self.columnas, (id_nodo-1)%self.columnas
        return mx + c*mx, my + f*my

    def dibujar_lienzo(self):
        # Borramos lo que habia
        self.lienzo.delete("all")
        # Creamos los nodos con radio 22 pixeles
        rad = 22
        # Para cada dos nodos conectados creamos una arista gris que los une 
        for (n1, n2) in self.aristas:
            x1, y1 = self.get_coord_nodo(n1)
            x2, y2 = self.get_coord_nodo(n2)
            self.lienzo.create_line(x1, y1, x2, y2, fill="#334155", width=3)
            
        # Creamos las lineas discontinuas por los qubits compartidos 
        colores = ["#C08114", "#06A671", "#3B4BF6", "#DF3E8F", "#7C51E2", "#099383"]
        grupos = []
        
        for q1, q2 in self.parejas:
            # Nos guardamos todas las parejas que tienen nodos en comun para que tengan 
            # el mismo color
            grupos_coincidentes = [g for g in grupos if q1 in g or q2 in g]
            # Si no estaba guardad la pareja la guardamos
            if not grupos_coincidentes:
                grupos.append({q1, q2})
            # Si no lo añadimos
            elif len(grupos_coincidentes) == 1:
                grupos_coincidentes[0].update([q1, q2])
            else:
                nuevo_grupo = {q1, q2}
                for g in grupos_coincidentes:
                    nuevo_grupo.update(g)
                    grupos.remove(g)
                grupos.append(nuevo_grupo)

        for (q1, q2) in self.parejas:
            x1, y1 = self.get_coord_nodo(self.qubits[q1-1])
            x2, y2 = self.get_coord_nodo(self.qubits[q2-1])
            
            # Por defecto usamos el amarillo
            color_pareja = "#BA7D13"
            for i, grupo in enumerate(grupos):
                # Si hay mas elementos usamos otro color
                if q1 in grupo and q2 in grupo:
                    color_pareja = colores[i % len(colores)]
                    break
                
            self.lienzo.create_line(x1, y1, x2, y2, fill=color_pareja, width=2, dash=(4,4))

        # Pintamos los nodos
        for i in range(1, self.n_nodos + 1):
            # Obtenemos las coordenadas
            x, y = self.get_coord_nodo(i)
            # Si en el nodo hay un qubit
            if i in self.qubits:
                idx = self.qubits.index(i) + 1
                # Si es un qubit seleccionado se pinta de azul y sino de rojo
                c = "#32A9DC" if self.primera_pareja == idx else "#DF3636"
                # Creamos el circulo del qubit
                self.lienzo.create_oval(x-rad, y-rad, x+rad, y+rad, fill=c, outline="white")
                # Le ponemos su nombre
                self.lienzo.create_text(x, y, text=f"Q{idx}", fill="white", font=("Arial", 10, "bold"))
            else:
                # Si no hay qubit creamos el circulo y lo pintamos de gris 
                self.lienzo.create_oval(x-rad, y-rad, x+rad, y+rad, fill="#101620", outline="#374251")
                self.lienzo.create_text(x, y, text=str(i), fill="#394658")

    def click_en_lienzo(self, evento):
        clicked = None
        # Buscamos sobre que nodo se ha hecho click
        for i in range(1, self.n_nodos + 1):
            x, y = self.get_coord_nodo(i)
            if math.hypot(evento.x - x, evento.y - y) < 25: 
                clicked = i
                break
        # Si no se ha hecho click nos salimos
        if not clicked: 
            return
        # obtenemos que valor estamos cambiando
        m = self.modo.get()
        
        # Si estamos en el modo qubit
        if m == "qubit":
            # Si ya lo teniamos seleccionado lo borramos
            if clicked in self.qubits: 
                idx = self.qubits.index(clicked)+1
                self.parejas = [g for g in self.parejas if g[0]!=idx and g[1]!=idx]
                self.qubits.remove(clicked)
            # Si no lo habiamos seleccionado lo marcamos
            else: self.qubits.append(clicked)
            
        # Modo arista
        elif m == "arista":
            # El primero que pinchamos se guarda
            if not self.nodo_elegido: self.nodo_elegido = clicked
            # Cuando hacemos click sobre el segundo se realiza la accion
            else:
                # Creamos la arista de izquierda a derecha como hicimmos al crear todas
                p = (min(self.nodo_elegido, clicked), max(self.nodo_elegido, clicked))
                # Si la arista ya existia la borramos
                if p in self.aristas: self.aristas.remove(p)
                # Si no existia la guardamos
                else: self.aristas.add(p)
                # Reiniciamos todo
                self.nodo_elegido = None
        # Modo pareja
        elif m == "pareja":
            # Nos aseguramos de que se ha seleccionado un qubit y no un nodo vacio
            if clicked in self.qubits:
                # Igual que con las aristas primero nos guardamos el primer click
                q = self.qubits.index(clicked)+1
                if self.primera_pareja is None: 
                    self.primera_pareja = q
                # En el segundo click realizamos la accion
                else:
                    # Nos aseguramos que no hemos pinchado dos veces el mismo nodo
                    if self.primera_pareja != q:
                        # Guardamos la pareja con el nodo menor primero 
                        pareja = (min(self.primera_pareja, q), max(self.primera_pareja, q))
                        
                        # Si la pareja ya existia la borramos
                        if pareja in self.parejas:
                            self.parejas.remove(pareja)
                        # Si no existía, la creamos
                        else:
                            self.parejas.append(pareja)
                    # Reiniciamos la primera pareja
                    self.primera_pareja = None
        self.dibujar_lienzo()
        
    def cargar_algoritmo(self):
        eleccion = self.var_algoritmo.get()
        
        # Si lo elije el usuario no hacemos nada mas
        if eleccion == "Manual":
            return 
            
        # Borramos lo que hubiera antes
        self.qubits.clear()
        self.parejas.clear()
        
        # Llamamos a la clase para que realice la peticion del usuario
        self.qubits, self.parejas = BibliotecaAlgoritmos.obtener_circuito(eleccion, self.n_nodos)
            
        self.dibujar_lienzo()

    def ejecutar_simulacion(self):
        # Nos aseguramos de que exista alguna pareja
        if not self.parejas:
            messagebox.showwarning("Error", "Define al menos una pareja antes de simular.")
            return
        
        # Fijamos un tiempo maximo a partir del numero de parejas que tenemos
        tiempo_max = len(self.parejas)*3 + 4
        
        # Traducimos todo para poder enviarlo en el archivo minizinc 
        # Ponemos un comentario al principio indicando el numero de filas y columnas para luego
        # poder utilizarlo en el visualizador
        dzn = f"% {self.filas},{self.columnas}\n"
        dzn += f"n_nodos = {self.n_nodos};\nn_qubits = {len(self.qubits)};\nn_parejas = {len(self.parejas)};\nt_max = {tiempo_max};\n\nadj = [|\n"
        
        # Creamos la matriz de T/F para el minizinc
        filas_matriz = []
        for i in range(1, self.n_nodos + 1):
            filas = ["true" if (min(i,j), max(i,j)) in self.aristas else "false" for j in range(1, self.n_nodos+1)]
            filas_matriz.append(", ".join(filas))
            
        # Añadimos la posicion de los qubits
        dzn += "  " + " |\n  ".join(filas_matriz) + "\n|];\n\n"
        dzn += "pos_inicial = " + str(self.qubits) + ";\n\ncircuito = [|\n"
        
        # Añadimos las parejas
        filas_parejas = [f"{g[0]}, {g[1]}" for g in self.parejas]
        dzn += "  " + " |\n  ".join(filas_parejas) + "\n|];\n"
        
        # Guardamos la informacion en test.dzn
        with open("test.dzn", "w", encoding="utf-8") as f: 
            f.write(dzn)
        
        # Lanzamos el comando para ejecutar el programa para visualizar el resultado visualizador_pro
        comando = ["uv", "run", "--with", "minizinc", "--with", "networkx", "--with", "matplotlib", "--with", "scipy", "visualizador_pro.py"]
        
        try:
            subprocess.Popen(comando, shell=True)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo lanzar el simulador:\n{e}")

# Cuando runeamos el programa realiza estas acciones
if __name__ == "__main__":
    ventana = tk.Tk()
    app = QuantumStudio(ventana)
    ventana.after(100, app.dibujar_lienzo)
    ventana.mainloop()