def get_next_course(current_course_name):
    """
    Dado el nombre del curso actual, retorna el siguiente curso en la secuencia.
    La secuencia es: Pre-Jardin -> Jardin -> Transición -> Primero -> Segundo -> Tercero -> 
    Cuarto -> Quinto -> Sexto -> Séptimo -> Octavo -> Noveno -> Décimo -> Once.
    Si el curso actual es "Once", retorna "Once" (curso final).
    
    :param current_course_name: Nombre del curso actual.
    :return: Nombre del siguiente curso.
    """
    progression = {
        "pre-jardin": "jardin",
        "jardin": "transicion",
        "transicion": "primero",
        "primero": "segundo",
        "segundo": "tercero",
        "tercero": "cuarto",
        "cuarto": "quinto",
        "quinto": "sexto",
        "sexto": "septimo",
        "septimo": "octavo",
        "octavo": "noveno",
        "noveno": "decimo",
        "decimo": "once",
        "once": "once"  # Último curso, no hay promoción después de esto
    }
    return progression.get(current_course_name.lower(), current_course_name)