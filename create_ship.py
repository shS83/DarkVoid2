from PIL import Image, ImageDraw


def create_spaceship_image(width=640, height=640, lean_angle=0):
    # Create a new image with transparent background
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Define colors
    body_color = (100, 150, 255)  # Futuristic blue
    wing_color = (80, 120, 200)
    engine_color = (255, 100, 100)  # Red glow for engines
    detail_color = (200, 200, 255)

    # Center point
    center_x, center_y = width // 2, height // 2

    # Rotate the drawing context if leaning
    if lean_angle != 0:
        # Create a temporary image to draw on, then rotate
        temp_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_img)

        # Draw the spaceship on temp image
        # Main body (fuselage)
        temp_draw.polygon(
            [
                (center_x - 20, center_y - 50),
                (center_x + 20, center_y - 50),
                (center_x + 15, center_y + 30),
                (center_x - 15, center_y + 30),
            ],
            fill=body_color,
        )

        # Wings
        temp_draw.polygon(
            [
                (center_x - 60, center_y - 20),
                (center_x - 20, center_y - 10),
                (center_x - 20, center_y + 10),
                (center_x - 40, center_y + 5),
            ],
            fill=wing_color,
        )
        temp_draw.polygon(
            [
                (center_x + 60, center_y - 20),
                (center_x + 20, center_y - 10),
                (center_x + 20, center_y + 10),
                (center_x + 40, center_y + 5),
            ],
            fill=wing_color,
        )

        # Engines
        temp_draw.ellipse(
            (center_x - 25, center_y + 25, center_x - 15, center_y + 35),
            fill=engine_color,
        )
        temp_draw.ellipse(
            (center_x + 15, center_y + 25, center_x + 25, center_y + 35),
            fill=engine_color,
        )

        # Cockpit
        temp_draw.ellipse(
            (center_x - 10, center_y - 40, center_x + 10, center_y - 20),
            fill=detail_color,
        )

        # Rotate the temp image
        img = temp_img.rotate(lean_angle, center=(center_x, center_y), expand=False)
    else:
        # Draw directly for neutral
        # Main body (fuselage)
        draw.polygon(
            [
                (center_x - 20, center_y - 50),
                (center_x + 20, center_y - 50),
                (center_x + 15, center_y + 30),
                (center_x - 15, center_y + 30),
            ],
            fill=body_color,
        )

        # Wings
        draw.polygon(
            [
                (center_x - 60, center_y - 20),
                (center_x - 20, center_y - 10),
                (center_x - 20, center_y + 10),
                (center_x - 40, center_y + 5),
            ],
            fill=wing_color,
        )
        draw.polygon(
            [
                (center_x + 60, center_y - 20),
                (center_x + 20, center_y - 10),
                (center_x + 20, center_y + 10),
                (center_x + 40, center_y + 5),
            ],
            fill=wing_color,
        )

        # Engines
        draw.ellipse(
            (center_x - 25, center_y + 25, center_x - 15, center_y + 35),
            fill=engine_color,
        )
        draw.ellipse(
            (center_x + 15, center_y + 25, center_x + 25, center_y + 35),
            fill=engine_color,
        )

        # Cockpit
        draw.ellipse(
            (center_x - 10, center_y - 40, center_x + 10, center_y - 20),
            fill=detail_color,
        )

    return img


# Create the three images
neutral_ship = create_spaceship_image(lean_angle=0)
left_lean_ship = create_spaceship_image(lean_angle=15)  # Lean left (clockwise rotation)
right_lean_ship = create_spaceship_image(
    lean_angle=-15
)  # Lean right (counter-clockwise rotation)

# Save them (you can adjust filenames)
neutral_ship.save("spaceship_neutral.png")
left_lean_ship.save("spaceship_left.png")
right_lean_ship.save("spaceship_right.png")

print("Spaceship images created and saved.")
