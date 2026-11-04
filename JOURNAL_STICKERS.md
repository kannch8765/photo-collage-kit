# Pastel Journal Sticker Doodles 🐾

Seven **original**, reusable scrapbook motifs made with Pillow, no AI image generation and no bundled personal photos.

Available names: \`heart\`, \`sparkle\`, \`bow\`, \`sakura\`, \`paw\`, \`cat\`, \`torii\`.

Run:

\`\`\`bash
python -m examples.sticker_sheet --output-dir demo_outputs/stickers
\`\`\`

This exports seven transparent PNGs and a synthetic preview sheet. In code:

\`\`\`python
from PIL import Image
from design_scripts.core.sticker_doodles import render_doodle, paste_doodle

render_doodle("sakura", size=256).save("sakura.png")
photo = Image.open("my_own_photo.jpg")
decorated = paste_doodle(photo, "bow", center=(200, 150), size=80, rotation=12)
decorated.save("decorated.png")
\`\`\`

The original photo is never stored in this repo. Drawings are authored as reusable geometry and can be recolored with a palette dictionary (keys: \`ink\`, \`cream\`, \`pink\`, \`mint\`, \`blue\`, \`gold\`). To trace an **actual object silhouette**, use the existing mask-aware outline module; these stickers are separate overlays, not segmentation masks.
