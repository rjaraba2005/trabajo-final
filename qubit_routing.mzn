include "globals.mzn";

% Parametros de entrada
int: n_nodos;    
int: n_qubits;   
int: t_max;      
int: n_parejas;  

% Datos 
array[1..n_nodos, 1..n_nodos] of bool: adj;
array[1..n_parejas, 1..2] of 1..n_qubits: circuito;
array[1..n_qubits] of 1..n_nodos: pos_inicial;

% Variables de decision
array[1..n_qubits, 1..t_max] of var 1..n_nodos: x;
array[1..n_nodos, 1..t_max] of var 0..n_qubits: z;
array[1..n_nodos, 1..n_nodos, 1..t_max-1] of var bool: s;
var 1..t_max: makespan;

% Consistencia entre matrices y entre posiciones
constraint 
    forall(t in 1..t_max)(
        % Nos aseguramos de que no haya dos qubits en el mismo nodo a la vez
        alldifferent([ x[q, t] | q in 1..n_qubits ])
        /\
        forall(q in 1..n_qubits)(
            % Colocamos el valor elegido en la otra matriz
            z[x[q, t], t] == q
        )
        /\
        forall(u in 1..n_nodos)(
            % Utilizamos bool2itn para transformar V a 1 y F a 0, siendo 1 que esta el
            % qubit en esa posición y 0 que no
            % Buscamos el 1 en la matriz x y lo multiplicamos por el numero de qubit que es
            % El resto seran 0 asi que para recorrer la lista usamos sum
            z[u, t] == sum(q in 1..n_qubits)(bool2int(x[q, t] == u) * q)
        )
    );

% Regla para el SWAP
constraint
    forall(t in 1..t_max-1)(
        forall(u, v in 1..n_nodos)(
            % Obligamos a que ambos nodos hagan swap
            (s[u,v,t] == s[v,u,t])
            /\ 
            % Si no existe el cable no podemos hacer el swap
            (not adj[u,v] -> s[u,v,t] == false)
            /\ 
            % Un qubit no puede hacer SWAP consigo mismo
            (u == v -> s[u,v,t] == false)
            /\
            % El nodo u al hacer SWAP tendra lo que tenia el nodo v el siguiente instante
            (s[u,v,t] -> (z[u, t+1] == z[v, t]))
        )
        /\
        forall(u in 1..n_nodos)(
            % Un nodo solo puede hacer SWAP como maximo una vez
            (sum(v in 1..n_nodos)(bool2int(s[u,v,t])) <= 1)
            /\
            % Si no ha habiado SWAP no cambia nada
            (sum(v in 1..n_nodos)(bool2int(s[u,v,t])) == 0) -> (z[u, t+1] == z[u, t])
        )
    )
    
    /\
    % Evitar bucles infinitos con dos qubits haciendo SWAP infinitamente
    forall(u, v in 1..n_nodos, t in 1..t_max-2)(
        not (s[u,v,t] /\ s[u,v,t+1])
    );
    
% Inicializacion
constraint
    % Posiciones de los qubits iniciales
    forall(q in 1..n_qubits)(
        x[q, 1] == pos_inicial[q]
    );

% Ejecucion
constraint
    forall(p in 1..n_parejas)(
        adj[x[circuito[p, 1], makespan], x[circuito[p, 2], makespan]] == true
    );

solve minimize makespan;