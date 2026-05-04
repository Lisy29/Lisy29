import argparse
import requests
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

def textsize(text, font):
    im = Image.new(mode="P", size=(0, 0))
    draw = ImageDraw.Draw(im)
    _, _, width, height = draw.textbbox((0, 0), text=text, font=font)
    return width, height

def get_github_contributions(username, year):
    url = f'https://github-contributions-api.jogruber.de/v4/{username}?y={year}'
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data from GitHub: {response.status_code}")

    body = response.json()

    return [(contribution['date'], contribution['count']) for contribution in body['contributions']]

def draw_grid(draw, grid, cell_size, colors):
    for week in range(len(grid)):
        for day in range(len(grid[0])):
            color = colors[grid[week][day]]
            x0, y0 = week * cell_size + 40, day * cell_size + 20
            x1, y1 = x0 + cell_size, y0 + cell_size
            # Shadow
            draw.rectangle([x0 + 3, y0 + 3, x1 + 3, y1 + 3], fill=(0, 0, 0, 100))
            # Block
            draw.rectangle([x0, y0, x1, y1], fill=color, outline=(255, 255, 255))

def draw_legend(draw, cell_size, image_width, image_height, username, year):
    days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    for i, day in enumerate(days):
        y = i * cell_size + 20
        draw.text((5, y), day, fill=(255, 255, 255))

    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    month_positions = {1: 0, 2: 4, 3: 8, 4: 12, 5: 16, 6: 20, 7: 24, 8: 28, 9: 32, 10: 36, 11: 40, 12: 44}
    for month, week in month_positions.items():
        x = week * cell_size + 40
        draw.text((x, 5), months[month - 1], fill=(255, 255, 255))

    text = f"{year}"
    draw.text((5, 5), text, fill=(255, 255, 255))

    legend_width = 40
    bar_height = 20
    bar_y = image_height - bar_height
    draw.rectangle([legend_width, bar_y, image_width, image_height], fill=(0, 0, 0))

    credits_text = f"@{username} - Credits: DEBBAWEB"
    font = ImageFont.load_default()
    text_width, text_height = textsize(credits_text, font=font)
    text_x = image_width - text_width - 5
    text_y = bar_y + (bar_height - text_height) // 2
    draw.text((text_x, text_y), credits_text, fill=(255, 255, 255), font=font)

def create_tetris_gif(username, year, contributions, output_path):
    width = 53
    height = 7
    cell_size = 20
    legend_width = 40
    image_width = width * cell_size + legend_width
    image_height = height * cell_size + 40

    colors = ['#ebedf0', '#ff69b4', '#fffd00', '#00ff00', '#0000ff']
    background_color = '#0e0e0e'

    frames = []
    grid = [[0] * height for _ in range(width)]

    for i, (date, count) in enumerate(contributions):
        week = i // 7
        day = i % 7
        value = min(count, 4)

        for step in range(day + 1):
            if step % 2 == 0:
                img = Image.new('RGB', (image_width, image_height), background_color)
                draw = ImageDraw.Draw(img)
                draw_legend(draw, cell_size, image_width, image_height, username, year)
                draw_grid(draw, grid, cell_size, colors)

                x0, y0 = week * cell_size + legend_width, step * cell_size + 20
                x1, y1 = x0 + cell_size, y0 + cell_size
                draw.rectangle(
                    [x0, y0, x1, y1],
                    fill=colors[value],
                    outline=(255, 255, 255)
                )

                frames.append(img)

        grid[week][day] = value

        for alpha in range(0, 256, 50):
            img = Image.new('RGB', (image_width, image_height), background_color)
            draw = ImageDraw.Draw(img)
            draw_legend(draw, cell_size, image_width, image_height, username, year)
            draw_grid(draw, grid, cell_size, colors)

            x0, y0 = week * cell_size + legend_width, day * cell_size + 20
            x1, y1 = x0 + cell_size, y0 + cell_size
            draw.rectangle(
                [x0, y0, x1, y1],
                fill=colors[value],
                outline=(255, 255, 255, alpha)
            )

            frames.append(img)

    frames[0].save(output_path, save_all=True, append_images=frames[1:], optimize=False, duration=20, loop=0)

def generate_readme_section(username, years):
    """Generate the Tetris contributions section for the README."""
    lines = ["### 🎮 Mi patrón de tetris en contribuciones"]
    for year in years:
        lines.append(f"![Tetris GitHub {year}](https://raw.githubusercontent.com/{username}/{username}/main/images/tetris_github_{year}.gif)")
    return "\n".join(lines)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate GitHub contributions Tetris GIFs for the last 3 years.')
    parser.add_argument('-u', '--username', type=str, required=True, help='GitHub username')
    parser.add_argument('-n', '--num-years', type=int, default=3, help='Number of recent years to generate (default: 3)')

    args = parser.parse_args()

    current_year = datetime.now().year
    years = list(range(current_year, current_year - args.num_years, -1))

    import os
    os.makedirs('images', exist_ok=True)

    for year in years:
        try:
            print(f"Generating Tetris GIF for {year}...")
            contributions = get_github_contributions(args.username, year)
            create_tetris_gif(args.username, year, contributions, f'images/tetris_github_{year}.gif')
            print(f"   {year} done!")
        except Exception as e:
            print(f"   {year} failed: {e}")

    print("\n--- README section (copy this into your README.md) ---\n")
    print(generate_readme_section(args.username, years))
