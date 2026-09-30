"""Optional renders: python -m pip install CairoSVG Pillow; python render.py"""
from pathlib import Path
import cairosvg
from PIL import Image
p=Path(__file__).parent
for mode,bg in [('dark','#0A0A0B'),('light','#F7F7F8')]:
    cairosvg.svg2png(url=str(p/f'wordmark-{mode}.svg'),write_to=str(p/f'preview-{mode}.png'),output_width=832,output_height=128,background_color=bg)
for size in (16,32,180,512):
    cairosvg.svg2png(url=str(p/'favicon.svg'),write_to=str(p/f'favicon-{size}.png'),output_width=size,output_height=size)
Image.open(p/'favicon-512.png').save(p/'favicon.ico',sizes=[(16,16),(32,32),(48,48)])
sheet=Image.new('RGB',(960,360),'#0A0A0B')
sheet.paste(Image.open(p/'preview-dark.png'),(64,40))
sheet.paste(Image.open(p/'preview-light.png'),(64,200))
sheet.save(p/'brand-preview.png')
sheet=Image.new('RGB',(360,128),'#222226')
for x,size in [(16,16),(64,32),(128,16),(224,32)]:
    source=Image.open(p/f'favicon-{size}.png')
    if x>=100: source=source.resize((96,96),Image.Resampling.NEAREST)
    sheet.paste(source,(x,16),source)
sheet.save(p/'favicon-preview.png')
