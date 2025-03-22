import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import xml.etree.ElementTree as ET
import json
import os

# Clase que representa un estado en un autómata
class State:
    def __init__(self, name, is_initial=False, is_final=False):
        self.name = name  # Nombre del estado
        self.is_initial = is_initial  # Indica si es un estado inicial
        self.is_final = is_final  # Indica si es un estado final

    def __str__(self):
        return self.name  # Representación en cadena del estado

    def __repr__(self):
        return self.name  # Representación oficial para depuración

# Clase que implementa un Autómata Finito Determinista (AFD)
class AFD:
    def __init__(self):
        self.states = []  # Lista de estados
        self.alphabet = set()  # Alfabeto del autómata
        self.initial_state = None  # Estado inicial
        self.final_states = []  # Lista de estados finales
        self.transitions = {}  # Diccionario de transiciones: {(estado, símbolo): estado_destino}

    # Añade un nuevo estado al autómata
    def add_state(self, state, is_initial=False, is_final=False):
        new_state = State(state, is_initial, is_final)
        self.states.append(new_state)
        if is_initial:
            self.initial_state = new_state  # Establece como estado inicial
        if is_final:
            self.final_states.append(new_state)  # Añade a la lista de estados finales
        return new_state

    # Añade una transición al autómata
    def add_transition(self, from_state, symbol, to_state):
        if symbol not in self.alphabet and symbol != '':
            self.alphabet.add(symbol)  # Añade el símbolo al alfabeto
        self.transitions[(from_state, symbol)] = to_state  # Añade la transición

    # Busca un estado por su nombre
    def get_state_by_name(self, name):
        for state in self.states:
            if state.name == name:
                return state
        return None

    # Valida si una cadena es aceptada por el autómata
    def validate_string(self, input_string):
        if not self.initial_state:
            return False, []  # Si no hay estado inicial, la cadena es rechazada

        current_state = self.initial_state
        steps = [(current_state, 0, input_string)]  # Pasos de la simulación

        for i, symbol in enumerate(input_string):
            if (current_state, symbol) not in self.transitions:
                return False, steps + [(None, i+1, input_string[i+1:])]  # Si no hay transición, rechaza

            current_state = self.transitions[(current_state, symbol)]  # Siguiente estado
            steps.append((current_state, i+1, input_string[i+1:]))  # Añade el paso a la lista

        return current_state in self.final_states, steps  # Acepta si el estado final es de aceptación

    # Convierte el AFD a un formato de diccionario para serialización
    def to_afd_format(self):
        data = {
            "alphabet": list(self.alphabet),
            "states": [state.name for state in self.states],
            "initial_state": self.initial_state.name if self.initial_state else "",
            "final_states": [state.name for state in self.final_states],
            "transitions": {
                f"{from_state.name},{symbol}": to_state.name 
                for (from_state, symbol), to_state in self.transitions.items()
            }
        }
        return data

    # Crea un AFD a partir de un diccionario con el formato específico
    @classmethod
    def from_afd_format(cls, data):
        afd = cls()
        for state_name in data["states"]:
            is_initial = state_name == data["initial_state"]
            is_final = state_name in data["final_states"]
            afd.add_state(state_name, is_initial, is_final)  # Añade estados

        for transition_key, to_state_name in data["transitions"].items():
            from_state_name, symbol = transition_key.split(",")
            from_state = afd.get_state_by_name(from_state_name)
            to_state = afd.get_state_by_name(to_state_name)
            if from_state and to_state:
                afd.add_transition(from_state, symbol, to_state)  # Añade transiciones

        return afd

    # Crea un AFD a partir de un archivo en formato JFF (JFLAP)
    @classmethod
    def from_jff_format(cls, jff_content):
        afd = cls()
        root = ET.fromstring(jff_content)
        state_elements = root.findall(".//state")
        id_to_name = {}
        id_to_state = {}

        for state_elem in state_elements:
            state_id = state_elem.get("id")
            state_name = state_elem.get("name", state_id)
            id_to_name[state_id] = state_name
            is_initial = state_elem.find("initial") is not None
            is_final = state_elem.find("final") is not None
            state = afd.add_state(state_name, is_initial, is_final)  # Añade estados
            id_to_state[state_id] = state

        transition_elements = root.findall(".//transition")
        for trans_elem in transition_elements:
            from_id = trans_elem.find("from").text
            to_id = trans_elem.find("to").text
            read_elem = trans_elem.find("read")
            symbol = read_elem.text if read_elem is not None and read_elem.text else ""
            from_state = id_to_state[from_id]
            to_state = id_to_state[to_id]
            afd.add_transition(from_state, symbol, to_state)  # Añade transiciones

        return afd

# Clase que implementa un Autómata Finito No Determinista (NFA)
class NFA:
    def __init__(self):
        self.states = []  # Lista de estados
        self.alphabet = set()  # Alfabeto del autómata
        self.initial_state = None  # Estado inicial
        self.final_states = []  # Lista de estados finales
        self.transitions = {}  # Diccionario de transiciones: {(estado, símbolo): [estados_destino]}

    # Añade un nuevo estado al autómata
    def add_state(self, state, is_initial=False, is_final=False):
        new_state = State(state, is_initial, is_final)
        self.states.append(new_state)
        if is_initial:
            self.initial_state = new_state  # Establece como estado inicial
        if is_final:
            self.final_states.append(new_state)  # Añade a la lista de estados finales
        return new_state

    # Añade una transición al autómata
    def add_transition(self, from_state, symbol, to_state):
        if symbol not in self.alphabet and symbol != '':
            self.alphabet.add(symbol)  # Añade el símbolo al alfabeto
        key = (from_state, symbol)
        if key not in self.transitions:
            self.transitions[key] = []  # Inicializa la lista de estados destino
        self.transitions[key].append(to_state)  # Añade el estado destino

    # Calcula la clausura lambda de un conjunto de estados
    def lambda_closure(self, states):
        closure = set(states)  # Inicializa la clausura con los estados dados
        stack = list(states)  # Usa una pila para procesar los estados

        while stack:
            state = stack.pop()  # Toma un estado de la pila
            key = (state, '')  # Busca transiciones lambda (símbolo vacío)
            if key in self.transitions:
                for next_state in self.transitions[key]:
                    if next_state not in closure:
                        closure.add(next_state)  # Añade el estado a la clausura
                        stack.append(next_state)  # Añade el estado a la pila para seguir explorando

        return closure  # Devuelve la clausura lambda

    # Valida si una cadena es aceptada por el autómata
    def validate_string(self, input_string):
        current_states = self.lambda_closure({self.initial_state})  # Estados activos iniciales
        steps = [(current_states, 0, input_string)]  # Pasos de la simulación

        for i, symbol in enumerate(input_string):
            next_states = set()  # Estados activos en el siguiente paso
            for state in current_states:
                key = (state, symbol)
                if key in self.transitions:
                    next_states.update(self.transitions[key])  # Añade los estados destino
            current_states = self.lambda_closure(next_states)  # Calcula la clausura lambda
            steps.append((current_states, i+1, input_string[i+1:]))  # Añade el paso a la lista

        return any(state in self.final_states for state in current_states), steps  # Acepta si algún estado es final

    # Convierte un NFA a un DFA usando el algoritmo de subconjuntos
    def to_dfa(self):
        dfa = AFD()  # Crea un nuevo DFA
        initial_closure = self.lambda_closure({self.initial_state})  # Clausura lambda del estado inicial
        dfa_state_map = {frozenset(initial_closure): dfa.add_state('q0', is_initial=True)}  # Mapa de estados
        stack = [initial_closure]  # Pila para procesar los estados

        while stack:
            current_states = stack.pop()  # Toma un conjunto de estados de la pila
            current_dfa_state = dfa_state_map[frozenset(current_states)]  # Estado correspondiente en el DFA

            for symbol in self.alphabet:
                next_states = set()  # Estados destino para el símbolo actual
                for state in current_states:
                    key = (state, symbol)
                    if key in self.transitions:
                        next_states.update(self.transitions[key])  # Añade los estados destino
                next_closure = self.lambda_closure(next_states)  # Calcula la clausura lambda

                if not next_closure:
                    continue  # Si no hay estados destino, continúa

                if frozenset(next_closure) not in dfa_state_map:
                    new_state_name = f'q{len(dfa_state_map)}'  # Nombre del nuevo estado
                    is_final = any(state in self.final_states for state in next_closure)  # Es estado final?
                    dfa_state_map[frozenset(next_closure)] = dfa.add_state(new_state_name, is_final=is_final)  # Añade el estado
                    stack.append(next_closure)  # Añade el conjunto de estados a la pila

                dfa.add_transition(current_dfa_state, symbol, dfa_state_map[frozenset(next_closure)])  # Añade la transición

        return dfa  # Devuelve el DFA resultante

    # Crea un NFA a partir de un archivo en formato JFF (JFLAP)
    @classmethod
    def from_jff_format(cls, jff_content):
        nfa = cls()
        root = ET.fromstring(jff_content)
        state_elements = root.findall(".//state")
        id_to_name = {}
        id_to_state = {}

        for state_elem in state_elements:
            state_id = state_elem.get("id")
            state_name = state_elem.get("name", state_id)
            id_to_name[state_id] = state_name
            is_initial = state_elem.find("initial") is not None
            is_final = state_elem.find("final") is not None
            state = nfa.add_state(state_name, is_initial, is_final)  # Añade estados
            id_to_state[state_id] = state

        transition_elements = root.findall(".//transition")
        for trans_elem in transition_elements:
            from_id = trans_elem.find("from").text
            to_id = trans_elem.find("to").text
            read_elem = trans_elem.find("read")
            symbol = read_elem.text if read_elem is not None and read_elem.text else ""
            from_state = id_to_state[from_id]
            to_state = id_to_state[to_id]
            nfa.add_transition(from_state, symbol, to_state)  # Añade transiciones

        return nfa

# Clase principal de la aplicación con interfaz gráfica
class AFDSimulator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulador de Autómatas Finitos Deterministas")
        self.geometry("1000x700")
        self.current_afd = AFD()  # AFD actual
        self.current_nfa = None  # NFA actual
        self.simulation_steps = []  # Pasos de la simulación
        self.current_step = 0  # Paso actual en la simulación
        self.setup_ui()  # Configura la interfaz de usuario

    # Configura la interfaz de usuario
    def setup_ui(self):
        self.notebook = ttk.Notebook(self)  # Crea un sistema de pestañas
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.definition_tab = ttk.Frame(self.notebook)  # Pestaña de definición
        self.simulation_tab = ttk.Frame(self.notebook)  # Pestaña de simulación
        self.tools_tab = ttk.Frame(self.notebook)  # Pestaña de herramientas
        self.notebook.add(self.definition_tab, text="Definición de AFD")
        self.notebook.add(self.simulation_tab, text="Simulación")
        self.notebook.add(self.tools_tab, text="Herramientas")
        self.setup_definition_tab()  # Configura la pestaña de definición
        self.setup_simulation_tab()  # Configura la pestaña de simulación
        self.setup_tools_tab()  # Configura la pestaña de herramientas

    # Configura la pestaña de definición del AFD
    def setup_definition_tab(self):
        state_frame = ttk.LabelFrame(self.definition_tab, text="Definición de Estados")
        state_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(state_frame, text="Nombre del estado:").grid(row=0, column=0, padx=5, pady=5)
        self.state_name_var = tk.StringVar()  # Variable para el nombre del estado
        ttk.Entry(state_frame, textvariable=self.state_name_var, width=20).grid(row=0, column=1, padx=5, pady=5)
        self.is_initial_var = tk.BooleanVar()  # Variable para estado inicial
        ttk.Checkbutton(state_frame, text="Estado inicial", variable=self.is_initial_var).grid(row=0, column=2, padx=5, pady=5)
        self.is_final_var = tk.BooleanVar()  # Variable para estado final
        ttk.Checkbutton(state_frame, text="Estado de aceptación", variable=self.is_final_var).grid(row=0, column=3, padx=5, pady=5)
        ttk.Button(state_frame, text="Agregar Estado", command=self.add_state).grid(row=0, column=4, padx=5, pady=5)  # Botón para agregar estado

        transition_frame = ttk.LabelFrame(self.definition_tab, text="Definición de Transiciones")
        transition_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(transition_frame, text="Estado origen:").grid(row=0, column=0, padx=5, pady=5)
        self.from_state_var = tk.StringVar()  # Variable para el estado origen
        self.from_state_combobox = ttk.Combobox(transition_frame, textvariable=self.from_state_var, state="readonly", width=15)
        self.from_state_combobox.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(transition_frame, text="Símbolo:").grid(row=0, column=2, padx=5, pady=5)
        self.symbol_var = tk.StringVar()  # Variable para el símbolo
        ttk.Entry(transition_frame, textvariable=self.symbol_var, width=5).grid(row=0, column=3, padx=5, pady=5)
        ttk.Label(transition_frame, text="Estado destino:").grid(row=0, column=4, padx=5, pady=5)
        self.to_state_var = tk.StringVar()  # Variable para el estado destino
        self.to_state_combobox = ttk.Combobox(transition_frame, textvariable=self.to_state_var, state="readonly", width=15)
        self.to_state_combobox.grid(row=0, column=5, padx=5, pady=5)
        ttk.Button(transition_frame, text="Agregar Transición", command=self.add_transition).grid(row=0, column=6, padx=5, pady=5)  # Botón para agregar transición

        table_frame = ttk.LabelFrame(self.definition_tab, text="Tabla de Transiciones")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.transitions_tree = ttk.Treeview(table_frame)  # Tabla para mostrar las transiciones
        self.transitions_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        x_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.transitions_tree.xview)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        y_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.transitions_tree.yview)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.transitions_tree.configure(xscrollcommand=x_scrollbar.set, yscrollcommand=y_scrollbar.set)

        buttons_frame = ttk.Frame(self.definition_tab)
        buttons_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(buttons_frame, text="Cargar Autómata", command=self.load_afd).pack(side=tk.LEFT, padx=5, pady=5)  # Botón para cargar autómata
        ttk.Button(buttons_frame, text="Guardar Autómata", command=self.save_afd).pack(side=tk.LEFT, padx=5, pady=5)  # Botón para guardar autómata
        ttk.Button(buttons_frame, text="Reiniciar Autómata", command=self.reset_afd).pack(side=tk.LEFT, padx=5, pady=5)  # Botón para reiniciar autómata
        ttk.Button(buttons_frame, text="Convertir NFA a DFA", command=self.convert_nfa_to_dfa).pack(side=tk.LEFT, padx=5, pady=5)  # Botón para convertir NFA a DFA

    # Configura la pestaña de simulación
    def setup_simulation_tab(self):
        input_frame = ttk.Frame(self.simulation_tab)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(input_frame, text="Cadena a validar:").pack(side=tk.LEFT, padx=5, pady=5)
        self.input_string_var = tk.StringVar()  # Variable para la cadena de entrada
        ttk.Entry(input_frame, textvariable=self.input_string_var, width=30).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(input_frame, text="Validar", command=self.validate_string).pack(side=tk.LEFT, padx=5, pady=5)  # Botón para validar cadena

        result_frame = ttk.Frame(self.simulation_tab)
        result_frame.pack(fill=tk.X, padx=10, pady=5)
        self.validation_result_var = tk.StringVar()  # Variable para el resultado de la validación
        self.validation_result_label = ttk.Label(result_frame, textvariable=self.validation_result_var, font=("Arial", 12))
        self.validation_result_label.pack(padx=5, pady=5)

        sim_frame = ttk.LabelFrame(self.simulation_tab, text="Simulación paso a paso")
        sim_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.current_position_var = tk.StringVar()  # Variable para la posición actual
        ttk.Label(sim_frame, textvariable=self.current_position_var, font=("Arial", 10)).pack(padx=5, pady=5, anchor=tk.W)
        self.simulation_text = scrolledtext.ScrolledText(sim_frame, width=80, height=15)  # Área de texto para la simulación
        self.simulation_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        control_frame = ttk.Frame(sim_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(control_frame, text="Paso anterior", command=self.prev_step).pack(side=tk.LEFT, padx=5, pady=5)  # Botón para paso anterior
        ttk.Button(control_frame, text="Siguiente paso", command=self.next_step).pack(side=tk.LEFT, padx=5, pady=5)  # Botón para siguiente paso
        ttk.Button(control_frame, text="Reiniciar simulación", command=self.reset_simulation).pack(side=tk.LEFT, padx=5, pady=5)  # Botón para reiniciar simulación

    # Configura la pestaña de herramientas
    def setup_tools_tab(self):
        substrings_frame = ttk.LabelFrame(self.tools_tab, text="Subcadenas, Prefijos y Sufijos")
        substrings_frame.pack(fill=tk.X, padx=10, pady=5)
        input_frame = ttk.Frame(substrings_frame)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(input_frame, text="Cadena para analizar:").pack(side=tk.LEFT, padx=5, pady=5)
        self.substring_input_var = tk.StringVar()  # Variable para la cadena de entrada
        ttk.Entry(input_frame, textvariable=self.substring_input_var, width=30).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(input_frame, text="Calcular", command=self.calculate_substrings).pack(side=tk.LEFT, padx=5, pady=5)  # Botón para calcular subcadenas

        results_frame = ttk.Frame(substrings_frame)
        results_frame.pack(fill=tk.X, padx=5, pady=5)
        self.substrings_text = scrolledtext.ScrolledText(results_frame, width=80, height=10)  # Área de texto para resultados
        self.substrings_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        kleene_frame = ttk.LabelFrame(self.tools_tab, text="Cerradura de Kleene y Positiva")
        kleene_frame.pack(fill=tk.X, padx=10, pady=5)
        kleene_input_frame = ttk.Frame(kleene_frame)
        kleene_input_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(kleene_input_frame, text="Alfabeto (ej: ab):").pack(side=tk.LEFT, padx=5, pady=5)
        self.kleene_alphabet_var = tk.StringVar()  # Variable para el alfabeto
        ttk.Entry(kleene_input_frame, textvariable=self.kleene_alphabet_var, width=15).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Label(kleene_input_frame, text="Longitud máxima:").pack(side=tk.LEFT, padx=5, pady=5)
        self.kleene_length_var = tk.StringVar(value="3")  # Variable para la longitud máxima
        ttk.Entry(kleene_input_frame, textvariable=self.kleene_length_var, width=5).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(kleene_input_frame, text="Calcular", command=self.calculate_kleene).pack(side=tk.LEFT, padx=5, pady=5)  # Botón para calcular cerradura

        kleene_results_frame = ttk.Frame(kleene_frame)
        kleene_results_frame.pack(fill=tk.X, padx=5, pady=5)
        self.kleene_text = scrolledtext.ScrolledText(kleene_results_frame, width=80, height=10)  # Área de texto para resultados
        self.kleene_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # Añade un nuevo estado al autómata
    def add_state(self):
        state_name = self.state_name_var.get().strip()
        is_initial = self.is_initial_var.get()
        is_final = self.is_final_var.get()
        if not state_name:
            messagebox.showerror("Error", "El nombre del estado no puede estar vacío")
            return
        if self.current_afd.get_state_by_name(state_name):
            messagebox.showerror("Error", f"El estado {state_name} ya existe")
            return
        self.current_afd.add_state(state_name, is_initial, is_final)
        self.state_name_var.set("")
        self.is_initial_var.set(False)
        self.is_final_var.set(False)
        self.update_state_dropdowns()
        self.update_transitions_table()

    # Añade una nueva transición al autómata
    def add_transition(self):
        from_state_name = self.from_state_var.get()
        symbol = self.symbol_var.get().strip()
        to_state_name = self.to_state_var.get()
        if not from_state_name or not to_state_name:
            messagebox.showerror("Error", "Debe seleccionar los estados origen y destino")
            return
        if not symbol and symbol != '':
            messagebox.showerror("Error", "Debe ingresar un símbolo")
            return
        from_state = self.current_afd.get_state_by_name(from_state_name)
        to_state = self.current_afd.get_state_by_name(to_state_name)
        if (from_state, symbol) in self.current_afd.transitions:
            messagebox.showerror("Error", f"Ya existe una transición desde {from_state_name} con el símbolo {symbol}")
            return
        self.current_afd.add_transition(from_state, symbol, to_state)
        self.symbol_var.set("...")
        self.update_transitions_table()

    # Valida si una cadena es aceptada por el autómata
    def validate_string(self):
        input_string = self.input_string_var.get()
        if input_string is None:
            return
        if self.current_nfa:
            is_accepted, steps = self.current_nfa.validate_string(input_string)
        else:
            is_accepted, steps = self.current_afd.validate_string(input_string)
        self.simulation_steps = steps
        self.current_step = 0
        if is_accepted:
            self.validation_result_var.set(f"La cadena '{input_string}' es ACEPTADA por el autómata")
            self.validation_result_label.configure(foreground="green")
        else:
            self.validation_result_var.set(f"La cadena '{input_string}' es RECHAZADA por el autómata")
            self.validation_result_label.configure(foreground="red")
        self.update_simulation_view()

    # Avanza al siguiente paso en la simulación
    def next_step(self):
        if self.simulation_steps and self.current_step < len(self.simulation_steps) - 1:
            self.current_step += 1
            self.update_simulation_view()

    # Retrocede al paso anterior en la simulación
    def prev_step(self):
        if self.simulation_steps and self.current_step > 0:
            self.current_step -= 1
            self.update_simulation_view()

    # Reinicia la simulación al paso inicial
    def reset_simulation(self):
        self.update_simulation_view()

    # Carga un autómata desde un archivo
    def load_afd(self):
        file_types = [("AFD Files", "*.afd"), ("JFLAP Files", "*.jff"), ("All Files", "*.*")]
        file_path = filedialog.askopenfilename(filetypes=file_types)
        if not file_path:
            return
        try:
            if file_path.endswith('.afd'):
                with open(file_path, 'r') as f:
                    afd_data = json.load(f)
                self.current_afd = AFD.from_afd_format(afd_data)
            elif file_path.endswith('.jff'):
                with open(file_path, 'r') as f:
                    jff_content = f.read()
                self.current_nfa = NFA.from_jff_format(jff_content)
                self.current_afd = self.current_nfa.to_dfa()
            self.update_state_dropdowns()
            self.update_transitions_table()
            messagebox.showinfo("Éxito", f"Autómata cargado desde {file_path}")
        except Exception as ex:
            messagebox.showerror("Error", f"Error al cargar el archivo: {str(ex)}")

    # Guarda el autómata actual en un archivo
    def save_afd(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".afd", filetypes=[("AFD Files", "*.afd"), ("All Files", "*.*")])
        if not file_path:
            return
        try:
            afd_data = self.current_afd.to_afd_format()
            with open(file_path, 'w') as f:
                json.dump(afd_data, f, indent=2)
            messagebox.showinfo("Éxito", f"AFD guardado en {file_path}")
        except Exception as ex:
            messagebox.showerror("Error", f"Error al guardar: {str(ex)}")

    # Reinicia el autómata actual
    def reset_afd(self):
        self.current_afd = AFD()
        self.current_nfa = None
        self.simulation_steps = []
        self.current_step = 0
        self.update_state_dropdowns()
        self.update_transitions_table()
        self.validation_result_var.set("")
        self.simulation_text.delete(1.0, tk.END)
        self.current_position_var.set("")

    # Calcula todas las subcadenas, prefijos y sufijos de una cadena
    def calculate_substrings(self):
        input_string = self.substring_input_var.get()
        if not input_string:
            return
        substrings = []
        for i in range(len(input_string)):
            for j in range(i + 1, len(input_string) + 1):
                substrings.append(input_string[i:j])
        prefixes = [input_string[:i] for i in range(len(input_string) + 1)]
        suffixes = [input_string[i:] for i in range(len(input_string) + 1)]
        self.substrings_text.delete(1.0, tk.END)
        self.substrings_text.insert(tk.END, f"Subcadenas ({len(substrings)}):\n")
        self.substrings_text.insert(tk.END, ", ".join(substrings) + "\n\n")
        self.substrings_text.insert(tk.END, f"Prefijos ({len(prefixes)}):\n")
        self.substrings_text.insert(tk.END, ", ".join(prefixes) + "\n\n")
        self.substrings_text.insert(tk.END, f"Sufijos ({len(suffixes)}):\n")
        self.substrings_text.insert(tk.END, ", ".join(suffixes))

    # Calcula la cerradura de Kleene y positiva de un alfabeto
    def calculate_kleene(self):
        alphabet_input = self.kleene_alphabet_var.get()
        max_length_str = self.kleene_length_var.get()
        try:
            max_length = int(max_length_str)
        except ValueError:
            messagebox.showerror("Error", "La longitud máxima debe ser un número entero")
            return
        alphabet = []
        for char in alphabet_input:
            if char not in alphabet and not char.isspace():
                alphabet.append(char)
        if not alphabet:
            messagebox.showerror("Error", "El alfabeto no puede estar vacío")
            return
        kleene_star = [""]
        for length in range(1, max_length + 1):
            self.generate_strings(alphabet, "", length, kleene_star)
        kleene_plus = [s for s in kleene_star if s]
        self.kleene_text.delete(1.0, tk.END)
        self.kleene_text.insert(tk.END, f"Cerradura de Kleene (Σ*) - {len(kleene_star)} cadenas:\n")
        self.kleene_text.insert(tk.END, ", ".join(kleene_star) + "\n\n")
        self.kleene_text.insert(tk.END, f"Cerradura positiva (Σ+) - {len(kleene_plus)} cadenas:\n")
        self.kleene_text.insert(tk.END, ", ".join(kleene_plus))

    # Actualiza los menús desplegables de estados
    def update_state_dropdowns(self):
        state_names = [state.name for state in self.current_afd.states]
        self.from_state_combobox['values'] = state_names
        self.to_state_combobox['values'] = state_names

    # Actualiza la tabla de transiciones 
    def update_transitions_table(self):
        for item in self.transitions_tree.get_children():
            self.transitions_tree.delete(item)
        self.transitions_tree['columns'] = ['state'] + sorted(list(self.current_afd.alphabet))
        self.transitions_tree.column('#0', width=0, stretch=tk.NO)
        self.transitions_tree.column('state', anchor=tk.W, width=150)
        self.transitions_tree.heading('#0', text='', anchor=tk.CENTER)
        self.transitions_tree.heading('state', text='Estado', anchor=tk.CENTER)
        for symbol in sorted(self.current_afd.alphabet):
            self.transitions_tree.column(symbol, anchor=tk.CENTER, width=80)
            self.transitions_tree.heading(symbol, text=symbol, anchor=tk.CENTER)
        for state in self.current_afd.states:
            state_label = f"{state.name}{' (I)' if state.is_initial else ''}{' (F)' if state in self.current_afd.final_states else ''}"
            row_values = {'state': state_label}
            for symbol in sorted(self.current_afd.alphabet):
                next_state = self.current_afd.transitions.get((state, symbol), None)
                row_values[symbol] = next_state.name if next_state else "-"
            self.transitions_tree.insert('', tk.END, values=[row_values.get(col, '') for col in ['state'] + sorted(list(self.current_afd.alphabet))])

    # Actualiza la vista de simulación
    def update_simulation_view(self):
        self.simulation_text.delete(1.0, tk.END)
        if not self.simulation_steps:
            return
        for i, (state, pos, remaining) in enumerate(self.simulation_steps):
            if i > self.current_step:
                break
            if i == self.current_step:
                state_text = f"→ Estado: {state.name if state else 'Error'}"
            else:
                state_text = f"Estado: {state.name if state else 'Error'}"
            self.simulation_text.insert(tk.END, f"Paso {i}: {state_text}\n")
        if self.simulation_steps and self.current_step < len(self.simulation_steps):
            current_state, pos, remaining = self.simulation_steps[self.current_step]
            input_string = self.input_string_var.get()
            if input_string:
                highlighted_string = ""
                for i, char in enumerate(input_string):
                    if i < pos:
                        highlighted_string += char
                    elif i == pos and self.current_step < len(self.simulation_steps) - 1:
                        highlighted_string += f"[{char}]"
                    else:
                        highlighted_string += char
                self.current_position_var.set(f"Posición actual: {highlighted_string}")

    # Genera todas las cadenas posibles de una longitud determinada
    def generate_strings(self, alphabet, current, length, result):
        if length == 0:
            result.append(current)
            return
        for symbol in alphabet:
            self.generate_strings(alphabet, current + symbol, length - 1, result)

    # Convierte un NFA a un DFA
    def convert_nfa_to_dfa(self):
        if self.current_nfa:
            self.current_afd = self.current_nfa.to_dfa()
            self.update_state_dropdowns()
            self.update_transitions_table()
            messagebox.showinfo("Éxito", "NFA convertido a DFA exitosamente")
        else:
            messagebox.showerror("Error", "No hay un NFA cargado para convertir")

    # Carga un NFA desde un archivo JFF
    def load_nfa_from_jff(self):
        file_types = [("JFLAP Files", "*.jff"), ("All Files", "*.*")]
        file_path = filedialog.askopenfilename(filetypes=file_types)
        if not file_path:
            return
        try:
            with open(file_path, 'r') as f:
                jff_content = f.read()
            self.current_nfa = NFA.from_jff_format(jff_content)
            self.update_state_dropdowns()
            self.update_transitions_table()
            messagebox.showinfo("Éxito", "NFA cargado desde JFF exitosamente")
        except Exception as ex:
            messagebox.showerror("Error", f"Error al cargar el archivo: {str(ex)}")

    # Valida múltiples cadenas desde un archivo
    def validate_multiple_strings(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if not file_path:
            return
        try:
            with open(file_path, 'r') as f:
                strings = f.read().splitlines()
            results = []
            for s in strings:
                if self.current_nfa:
                    is_accepted, _ = self.current_nfa.validate_string(s)
                else:
                    is_accepted, _ = self.current_afd.validate_string(s)
                results.append(f"{s}: {'Aceptada' if is_accepted else 'Rechazada'}")
            result_text = "\n".join(results)
            messagebox.showinfo("Resultados", result_text)
        except Exception as ex:
            messagebox.showerror("Error", f"Error al validar cadenas: {str(ex)}")

# Punto de entrada principal del programa
if __name__ == "__main__":
    app = AFDSimulator()  # Crea una instancia del simulador
    app.mainloop()  # Ejecuta la aplicación