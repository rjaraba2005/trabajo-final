import matplotlib.pyplot as plt
import matplotlib.animation as animation
import networkx as nx
from minizinc import Instance, Model, Solver
import math

ARCHIVO_MODELO = "qubit_routing.mzn"
ARCHIVO_DATOS = "test.dzn"
ARCHIVO_FONDO = "placa_base.jpg" 

# Abrimos el archivo con la prueba que queremos realizar
with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
    dzn_content = f.read()

# Buscamos los nodos usando recortes de texto
n_nodos_str = dzn_content.split("n_nodos = ")[1].split(";")[0]
n_nodos = int(n_nodos_str)

# Extraemos la matriz con las aristas cortando por los corchetes
adyacencia_str = dzn_content.split("adj = [|")[1].split("|]")[0]
adyacencia_limpia = adyacencia_str.replace('|', ',').replace('\n', '')

# Combertimos los T/F de texto a valores de T/F de Python
lista_adyacencia = [True if 'true' in x.lower() else False for x in adyacencia_limpia.split(',') if x.strip()]
matriz_adyacencia = [lista_adyacencia[i*n_nodos:(i+1)*n_nodos] for i in range(n_nodos)]

# Hacemos los calculos
print("Iniciando los cálculos")
modelo = Model(ARCHIVO_MODELO)
modelo.add_file(ARCHIVO_DATOS)
# Usamos chuffed en vez de cualquier otro porque es mucho más eficiente ya que descarta caminos
# imposibles y utliza lazy evaluation
solver = Solver.lookup("chuffed")
instancia = Instance(solver, modelo)

# Esperamos a que minizinc resuelva el problema
soluciones = instancia.solve()

# Como nos puede devolver una lista de soluciones nos quedamos solo con la ultima, la mas optima
if isinstance(soluciones.solution, list):
    res = soluciones.solution[-1]
# Si solo hay una cogemos esa
else:
    res = soluciones
    
# Si habia solucion
if res.solution:
    # Obtenemos la matriz con la solucion
    x_pos = res["x"]
    makespan = res["makespan"]
    n_qubits = len(x_pos)
    
    print(f"Solución encontrada en {makespan} pasos")

    # Utilizamos nx para mostrar los grafos
    G = nx.Graph()
    G.add_nodes_from(range(1, n_nodos + 1))
    
    # Añadimos las aristas que habia en la matriz de adyacencia
    for i in range(n_nodos):
        for j in range(i + 1, n_nodos):
            if matriz_adyacencia[i][j]:
                G.add_edge(i + 1, j + 1)
    
    # Buscamos las parejas
    texto_circuito = dzn_content.split("circuito = [|")[1].split("|]")[0]
    # Las separamos por barras |
    parejas_texto = texto_circuito.strip().split('|')

    parejas_logicas = []
    for p in parejas_texto:
        if p.strip():
            # Conviertimos el texto con dos numeros separados por coma en un pareja de numeros 
            valores = [int(x) for x in p.split(',') if x.strip()]
            if len(valores) == 2:
                parejas_logicas.append((valores[0], valores[1]))
    
    # Generamos la cuadricula
    # Miramos el numero de filas y columnas del comentario de la primera linea y lo separamos
    comentario_str = dzn_content.split("% ")[1].split("\n")[0]
    filas = int(comentario_str.split(",")[0])
    columnas = int(comentario_str.split(",")[1])

    pos = {}
    for i in range(n_nodos):
        fila = i // columnas
        columna = i % columnas
        pos[i + 1] = (columna, filas - 1 - fila)

    # Creamos la ventana para ver graficamente la resolucion del problema
    fig, ax = plt.subplots(figsize=(9, 7))
    ax.patch.set_alpha(0.0)

    # Añadimos una imagen al fondo de la ventana 
    try:
        img = plt.imread(ARCHIVO_FONDO)
        ax_bg = fig.add_axes([0, 0, 1, 1], zorder=-1) 
        ax_bg.imshow(img, aspect='auto') 
        ax_bg.axis('off') 
    # Si no hay imagen de fondo ponemos el fondo gris
    except FileNotFoundError:
        fig.patch.set_facecolor('#1E1E1E')

    # Seleccionamos los colores de los qubits
    colores_base = ["#EB3E3E", "#2F84E4", "#2BBD54", "#E0A12B", "#8C44C8", "#EA960F"]
    mapa_colores = {}
    
    # Agrupamos los qubits que están conectados entre sí 
    G_conexiones = nx.Graph()
    G_conexiones.add_nodes_from(range(1, n_qubits + 1))
    G_conexiones.add_edges_from(parejas_logicas)
    
    # Agrupamos todas las conexiones
    grupos = list(nx.connected_components(G_conexiones))
    
    for i, grupo in enumerate(grupos):
        # Si un qubit está solo (es un grupo de tamaño 1), le ponemos gris
        if len(grupo) == 1:
            mapa_colores[list(grupo)[0]] = "gray"
        else:
            # Si están conectados, asignamos el color del grupo
            color = colores_base[i % len(colores_base)]
            for q in grupo:
                mapa_colores[q] = color
    
    

    # Definimos cuántos micropasos damos entre un nodo y otro para que sea fluido
    pasos_intermedios = 15 
    # Calculamos el total de fotogramas sumando todos los micropasos de la animacion
    total_fotogramas = (makespan - 1) * pasos_intermedios + 1

    def actualizacion(frame):
        # Borramos el fotograma anterior
        ax.clear()
        
        # Calculamos en qué instante de tiempo estamos y el porcentaje de completo que estamos
        t = frame // pasos_intermedios
        progreso = (frame % pasos_intermedios) / pasos_intermedios
        
        # Si llegamos al final de la ejecucion, nos aseguramos de que no de error y se quede quieto
        if t >= makespan - 1:
            t = makespan - 1
            progreso = 0.0

        # Añadimos el titulo y el instante en el que estamos
        ax.set_title(f"Simulador Cuántico - Instante t={t+1} / {makespan}", 
                     fontsize=15, fontweight='bold', color='white', 
                     bbox=dict(facecolor='black', alpha=0.6))
        ax.axis('off') 
        
        # Pintamos las aristas
        nx.draw_networkx_edges(G, pos, ax=ax, edge_color="#E1E1E1", width=3, alpha=0.9)
        
        # Pintamos los nodos 
        nx.draw_networkx_nodes(G, pos, ax=ax, node_color='none', 
                               edgecolors="#EFEEEE", node_size=1100, linewidths=2)
        nx.draw_networkx_labels(G, pos, ax=ax, font_weight='bold', font_size=13, font_color='white')

        # Qubits
        for q in range(n_qubits):
            # Buscamos en que nodo esta actualmente
            nodo_actual = x_pos[q][t]
            # Buscamos a que nodo va 
            nodo_siguiente = x_pos[q][t + 1] if t + 1 < makespan else nodo_actual

            # Obtenemos las coordenadas reales de origen y destino en el lienzo
            x_actual, y_actual = pos[nodo_actual]
            x_siguiente, y_siguiente = pos[nodo_siguiente]

            # Calculamos la posicion exacta del qubit sumando el trocito que ha avanzado
            x_mov = x_actual + (x_siguiente - x_actual) * progreso
            y_mov = y_actual + (y_siguiente - y_actual) * progreso

            # Los qubits empiezan en 1 y q en 0
            numero_qubit = q + 1 
            # Buscamos su color de pareja
            color = mapa_colores[numero_qubit] 
            
            # Creamos un diccionario con la nueva posicion temporal flotante 
            pos_temporal = {numero_qubit: (x_mov, y_mov)}
            
            # Pintamos los qubits en la posicion intermedia
            nx.draw_networkx_nodes(G, pos_temporal, nodelist=[numero_qubit], ax=ax, 
                                   node_color=color, node_size=900, edgecolors='black')
            
            # Dibujamos el nombre de los qubits persiguiendo al circulo
            ax.text(x_mov, y_mov+0.25, f"Q{numero_qubit}", 
                    fontweight='bold', ha='center', color=color, fontsize=14, 
                    bbox=dict(facecolor='black', alpha=0.8, boxstyle='round,pad=0.2', edgecolor='none'))

    # Ajustamos los margenes a la ventana
    plt.subplots_adjust(left=0.2, right=0.8, top=0.8, bottom=0.2)
    
    # runeamos el programa bajando el tiempo entre fotogramas a 50ms para que vaya fluido
    # Ponemos 3 segundos de retardo para que de tiempo a ver la solucion
    fig.ani = animation.FuncAnimation(fig, actualizacion, frames=total_fotogramas, repeat=True, interval=50, repeat_delay=3000)
    plt.show()
else:
    print("El solver no pudo encontrar ninguna solución válida.")