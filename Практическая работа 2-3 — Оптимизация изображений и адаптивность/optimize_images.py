# -*- coding: utf-8 -*-
"""ЛР №1 (Рыбаков): оптимизация изображений.

Берём реальный скриншот, готовим «исходное» изображение ~2 МБ в JPEG, затем
сжимаем его до <200 кБ с сохранением геометрических размеров. Дополнительно —
вариант в WebP (задание для самостоятельной работы: «для других форматов»).
Печатает реальные размеры, качество и долю сжатия.
"""
import io
import json
import os
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
OUT = HERE / 'images'
OUT.mkdir(exist_ok=True)
SRC = Path(r'C:\Windows\Web\Wallpaper\Windows\img0.jpg')   # реальное фото 3840x2400

print('исходник:', SRC.name, SRC.stat().st_size, 'байт')

base = Image.open(SRC).convert('RGB')
print('размеры исходника:', base.size)

# --- «входное» изображение ~2 МБ в JPEG (как в примере задания) --------------
target_bytes = 2 * 1024 * 1024
q = 100
src_jpg = OUT / 'image.jpg'
while True:
    base.save(src_jpg, 'JPEG', quality=q, optimize=False, progressive=False)
    size = src_jpg.stat().st_size
    if size <= target_bytes or q <= 60:
        break
    q -= 5
print('исходное изображение: %s — %d байт (%.2f МБ), quality=%d, %dx%d'
      % (src_jpg.name, size, size / 1048576, q, base.size[0], base.size[1]))

# --- сжатие до <200 кБ с сохранением размеров ---------------------------------
def save_under(path, fmt, limit, **kw):
    qq = 95
    while qq >= 5:
        if fmt == 'JPEG':
            base.save(path, 'JPEG', quality=qq, optimize=True, progressive=True, **kw)
        else:
            base.save(path, 'WEBP', quality=qq, method=6, **kw)
        s = path.stat().st_size
        if s <= limit:
            return qq, s
        qq -= 2
    return qq, path.stat().st_size


q2, s2 = save_under(OUT / 'image_optimized.jpg', 'JPEG', 200 * 1024)
print('оптимизированное:     %s — %d байт (%.1f кБ), quality=%d, %dx%d'
      % ('image_optimized.jpg', s2, s2 / 1024, q2, base.size[0], base.size[1]))

q3, s3 = save_under(OUT / 'image_optimized.webp', 'WEBP', 200 * 1024)
print('оптимизированное:     %s — %d байт (%.1f кБ), quality=%d, %dx%d'
      % ('image_optimized.webp', s3, s3 / 1024, q3, base.size[0], base.size[1]))

# иконка/миниатюра для шага 3 второй лабораторной (иконочный шрифт/изображение
# высокого разрешения): retina-версия 2x
icon = base.resize((64, 64), Image.LANCZOS)
icon2x = base.resize((128, 128), Image.LANCZOS)
icon.save(OUT / 'icon_64.png')
icon2x.save(OUT / 'icon_128.png')
print('иконки: icon_64.png %d байт, icon_128.png %d байт (retina 2x)'
      % ((OUT / 'icon_64.png').stat().st_size, (OUT / 'icon_128.png').stat().st_size))

facts = {
    'src_name': SRC.name,
    'width': base.size[0], 'height': base.size[1],
    'original_bytes': size, 'original_mb': round(size / 1048576, 2),
    'optimized_bytes': s2, 'optimized_kb': round(s2 / 1024, 1),
    'quality_original': q, 'quality_optimized': q2,
    'webp_bytes': s3, 'webp_kb': round(s3 / 1024, 1),
    'saved_bytes': size - s2,
    'saved_percent': round((size - s2) / size * 100, 1),
    'ratio': round(size / s2, 1),
}
(HERE / 'raw' / 'image_facts.json').write_text(
    json.dumps(facts, ensure_ascii=False, indent=2), encoding='utf-8')
print()
print('экономия: %d байт (%.1f %%), в %.1f раз; WebP: %.1f кБ'
      % (facts['saved_bytes'], facts['saved_percent'], facts['ratio'], facts['webp_kb']))
