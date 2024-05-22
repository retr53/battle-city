from PIL import Image
image_name = 'steel.png'
# Загрузка изображения
image = Image.open(image_name)

# Определение размеров каждой части
width, height = image.size
part_width = width // 4
part_height = height // 4

# Создание и сохранение каждой части
for i in range(4):
    for j in range(4):
        # Определение области вырезки
        left = i * part_width
        top = j * part_height
        right = (i + 1) * part_width
        bottom = (j + 1) * part_height
        box = (left, top, right, bottom)

        # Вырезание и сохранение части
        part = image.crop(box)
        part.save(f'{image_name[:-4]}_{i}_{j}.png')