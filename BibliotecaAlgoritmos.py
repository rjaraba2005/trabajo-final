class BibliotecaAlgoritmos:
    @staticmethod
    def obtener_circuito(nombre_algoritmo, n_nodos):
        qubits = []
        parejas = []
        
        if nombre_algoritmo == "Estado de Bell":
            # Colocamos dos Qubits alejados
            qubits = [1, n_nodos] 
            parejas = [(1, 2)] 
            
        elif nombre_algoritmo == "Sumador Cuántico":
            # Colocamos 3 Qubits dispersos por la placa
            qubits = [1, n_nodos // 2, n_nodos]
            # La suma requiere interactuar Q1 con Q2, y luego Q1 con Q3 para guardar los acarreos
            parejas = [(1, 2), (1, 3)]

        elif nombre_algoritmo == "Corrección Errores":
            # Colocamos nodos en el tablero con un guardian, el del nodo 5
            qubits = [5, 2, 4, 6, 1] 
            # Siempre uno de los dos nodos tiene que confirmar con el guardian si todo es correcto
            parejas = [(2, 3),(1, 2),(1,4),(4,5)]
            
        return qubits, parejas
    