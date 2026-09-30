from pathlib import Path
import json
P=Path(__file__).parent
DARK='#0A0A0B'; WHITE='#F7F7F8'; RED='#F04452'; DEEP='#C62838'; GRAY='#A1A1AA'
def svg(body,w=32,h=32,title='Dot Panel'):
 return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{title}">\n  <title>{title}</title>\n{body}\n</svg>\n'
def mark(red=RED,ink=WHITE):
 return f'''  <rect x="3" y="3" width="26" height="26" rx="6" fill="none" stroke="{red}" stroke-width="2.5"/>
  <circle cx="11" cy="16" r="3" fill="{red}"/>
  <path d="M18 12.5h5M18 19.5h5" fill="none" stroke="{ink}" stroke-width="2.5" stroke-linecap="round"/>'''
def letters(ink):
 # Original monoline letterforms. No fonts or external resources.
 return f'''  <g fill="none" stroke="{ink}" stroke-width="2.25" stroke-linecap="round" stroke-linejoin="round">
    <path d="M44 8h4.5C59 8 59 24 48.5 24H44Z"/>
    <rect x="64" y="8" width="12" height="16" rx="6"/>
    <path d="M83 8h13m-6.5 0v16M111 24V8h6a4.5 4.5 0 0 1 0 9h-6M131 24l6-16 6 16m-10-5h8M151 24V8l12 16V8M183 8h-12v16h12m-12-8h10M191 8v16h12"/>
  </g>'''
for mode,red,ink in [('dark',RED,WHITE),('light',DEEP,DARK)]:
 (P/f'mark-{mode}.svg').write_text(svg(mark(red,ink)))
 (P/f'wordmark-{mode}.svg').write_text(svg(mark(red,ink)+'\n'+letters(ink),208,32))
 (P/f'wordmark-editable-{mode}.svg').write_text(svg(mark(red,ink)+f'\n  <text x="43" y="23" fill="{ink}" font-family="system-ui, sans-serif" font-size="22" font-weight="650" letter-spacing="-0.6">Dot Panel</text>',160,32))
(P/'mark-mono.svg').write_text(svg(mark('currentColor','currentColor')))
(P/'favicon.svg').write_text(svg(f'  <rect width="32" height="32" rx="8" fill="{DARK}"/>\n'+mark()))
(P/'tokens.css').write_text(''':root {
  --dp-bg: #0A0A0B;
  --dp-surface: #161619;
  --dp-surface-raised: #222226;
  --dp-border: #35353C;
  --dp-text: #F7F7F8;
  --dp-muted: #A1A1AA;
  --dp-accent: #F04452;
  --dp-on-accent: #0A0A0B;
  --dp-accent-deep: #C62838;
  --dp-on-accent-deep: #F7F7F8;
  --dp-radius-control: 14px;
  --dp-radius-panel: 22px;
  --dp-touch-min: 48px;
  --dp-font: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
''')
def lum(h):
 c=[int(h[i:i+2],16)/255 for i in (1,3,5)]
 return sum(w*(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4) for w,v in zip((.2126,.7152,.0722),c))
def contrast(a,b):
 l=sorted([lum(a),lum(b)]);return round((l[1]+.05)/(l[0]+.05),2)
pairs=[('Primary text',WHITE,DARK),('Muted text',GRAY,DARK),('Red action with dark text',DARK,RED),('Deep-red action with light text',WHITE,DEEP),('Accent against raised surface',RED,'#222226'),('Muted against raised surface',GRAY,'#222226')]
(P/'contrast.json').write_text(json.dumps([dict(usage=n,foreground=a,background=b,ratio=contrast(a,b)) for n,a,b in pairs],indent=2)+'\n')
print((P/'contrast.json').read_text())
