import os
import subprocess
from datetime import datetime, timedelta

# Configuración
repo_path = os.path.join(os.getcwd(), 'github-contributions-game')
file_name = 'commit.txt'

# Patrón Pac-Man (cada fila es una semana y cada columna es un día de la semana)
# 0 = sin commit, 1 = bolita comida, 2 = Pac-Man (comiendo)
pacman_pattern = [
    [0, 0, 0, 1, 1, 1, 1],  # Pac-Man empieza a comer
    [0, 0, 1, 1, 1, 1, 1],  # Pac-Man sigue comiendo
    [0, 1, 1, 1, 1, 1, 1],  # Pac-Man sigue comiendo más
    [1, 1, 1, 1, 1, 1, 1],  # Pac-Man está lleno
    [1, 1, 1, 1, 1, 1, 1],  # Pac-Man sigue comiendo más
    [0, 1, 1, 1, 1, 1, 1],  # Pac-Man sigue comiendo
    [0, 0, 1, 1, 1, 1, 1],  # Pac-Man sigue comiendo
    [0, 0, 0, 1, 1, 1, 1],  # Pac-Man está terminando
]

# Crear repositorio si no existe
if not os.path.exists(repo_path):
    os.makedirs(repo_path, exist_ok=True)
    os.chdir(repo_path)
    subprocess.run(['git', 'init'])
else:
    os.chdir(repo_path)

# Función para obtener una fecha específica en el pasado
def get_date_string(weeks_ago, day_of_week):
    today = datetime.today()
    days_ago = weeks_ago * 7 + day_of_week
    target_date = today - timedelta(days=days_ago)
    return target_date.strftime('%Y-%m-%d')

# Realizar commits según el patrón de Pac-Man
for week in range(len(pacman_pattern)):
    for day in range(7):
        intensity = pacman_pattern[week][day]
        if intensity == 0:
            continue
        
        date = get_date_string(len(pacman_pattern) - week, day)

        # Realizar un commit por cada "intensidad" de Pac-Man
        for i in range(intensity):
            with open(os.path.join(repo_path, file_name), 'w') as f:
                f.write(f'Commit {i+1} para el patrón de Pac-Man en {date}')
            subprocess.run(['git', 'add', file_name])
            subprocess.run(['git', 'commit', '--date', date, '-m', f'Commit {i+1} para el día {date}'])

print("¡Completado! Ahora tus contribuciones deberían mostrar a Pac-Man en tu perfil de GitHub.")
