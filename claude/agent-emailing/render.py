"""Gabarit LSPA (dérivé du template validé VSkTTd) + police mobile agrandie (corps 17px <600px)."""
import html
from emails import TILES, U
P = "font-family:'Poppins',Arial,sans-serif;"
def link(url, camp, key):
    """URL statique : UTM insérés. URL dynamique Klaviyo : laissée telle quelle (UTM ajoutés par add_tracking_params)."""
    return url.format(c=camp, k=key) if "{c}" in url else url
def fr(t):
    """Typo française : espace insécable avant ? : ! (hors balises Klaviyo, qui n'ont pas d'espace avant ces signes)."""
    for p in "?:!":
        t = t.replace(" " + p, "&nbsp;" + p)
    return t
def button(label, href):
    return (f'<table role="presentation" cellpadding="0" cellspacing="0" width="100%"><tr><td align="center" style="padding:8px 0 4px 0;">'
            f'<a href="{href}" target="_blank" style="display:inline-block;background:#E83F4E;color:#FFFFFF;{P}font-size:16px;font-weight:700;'
            f'text-decoration:none;padding:16px 34px;border-radius:999px;">{label}</a></td></tr></table>')
def tiles(camp):
    cells = "".join(
        f'<td class="stack stack-pad" width="33%" valign="top" style="padding:0 6px;"><a href="{u}" target="_blank" style="text-decoration:none;">'
        f'<img src="{img}" alt="{t}" width="170" style="width:100%;height:auto;display:block;border-radius:10px;"/>'
        f'<p class="body" style="margin:10px 0 0 0;{P}font-size:14px;font-weight:700;color:#222222;">{t}</p></a></td>'
        for i, (t, u, img) in enumerate(TILES, 1))
    return f'<tr><td class="px" style="padding:0 26px 24px 26px;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>{cells}</tr></table></td></tr>'
def render(e):
    c = e["camp"]
    body = "".join(f'<p class="body" style="margin:0 0 16px 0;{P}font-size:16px;line-height:1.6;color:#444444;">{fr(p)}</p>' for p in e["corps"])
    img = (f'<tr><td class="px" style="padding:28px 32px 0 32px;font-size:0;"><a href="{link(e["cta"][1],c,"image")}" target="_blank">'
           f'<img src="{e["image"]}" alt="" width="536" style="width:100%;height:auto;display:block;border-radius:14px;"/></a></td></tr>') if e.get("image") else ""
    ps = ""
    if e.get("ps"):
        pl = e.get("ps_link")
        ps = (f'<tr><td class="px" style="padding:0 32px 28px 32px;"><p class="body" style="margin:0;{P}font-size:14px;line-height:1.6;color:#6c6c6c;">'
              f'<strong style="color:#222222;">P.-S.</strong> {fr(e["ps"])}'
              + (f' <a href="{link(pl[1],c,"ps")}" style="color:#E83F4E;font-weight:700;">{pl[0]}</a>' if pl else "") + '</p></td></tr>')
    return f'''<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;700&display=swap" rel="stylesheet">
<style>@media only screen and (max-width:600px){{.container{{width:100%!important}}.px{{padding-left:20px!important;padding-right:20px!important}}
.stack{{display:block!important;width:100%!important}}.stack-pad{{padding:0 0 16px 0!important}}.h1{{font-size:30px!important;line-height:1.2!important}}
.body{{font-size:17px!important;line-height:1.65!important}}.cta a{{font-size:17px!important}}}}</style></head>
<body style="margin:0;padding:0;background:#FBF6F2;">
<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;font-size:1px;line-height:1px;color:#FBF6F2;opacity:0;">{e["preheader"]} &#847; &#847; &#847; &#847; &#847; &#847;</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#FBF6F2;"><tr><td align="center" style="padding:24px 12px;">
<table role="presentation" class="container" width="600" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;background:#FFFFFF;border:1px solid #EBE5E0;border-radius:14px;overflow:hidden;">
<tr><td class="px" style="padding:22px 32px;border-bottom:3px solid #E83F4E;"><table role="presentation" width="100%"><tr>
<td align="left"><a href="https://lovenspa.fr/" target="_blank"><img src="https://host.lovenspa.fr/email/lovenspa-logo.png" alt="Love'nSpa" width="140" style="width:140px;height:auto;"/></a></td>
<td align="right" style="{P}font-size:11px;font-weight:700;letter-spacing:0.22em;text-transform:uppercase;color:#E83F4E;">{e["kicker"]}</td></tr></table></td></tr>
{img}
<tr><td class="px" style="padding:32px 32px 8px 32px;"><h1 class="h1" style="margin:0 0 18px 0;{P}font-size:34px;line-height:1.15;font-weight:700;color:#222222;">{fr(e["titre"])}</h1>
{body}<div class="cta">{button(e["cta"][0], link(e["cta"][1], c, "cta"))}</div></td></tr>
{tiles(c) if e.get("tiles") else ""}
{ps}
<tr><td class="px" style="padding:22px 32px;background:#FBF6F2;border-top:1px solid #EBE5E0;"><p style="margin:0;{P}font-size:12px;line-height:1.6;color:#6c6c6c;text-align:center;">
Love'nSpa · love rooms avec spa privatif en France et en Belgique<br>
Vous recevez cet email car vous êtes client ou inscrit à nos idées d'escapades. <a href="{{% unsubscribe_link %}}" style="color:#6c6c6c;">Se désinscrire</a></p></td></tr>
</table></td></tr></table></body></html>'''
