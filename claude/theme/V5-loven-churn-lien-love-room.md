# V5 — lien churn vers /collections/love-room (action A2)

Thème : lovenspa 4.1 (MAIN, gid://shopify/OnlineStoreTheme/188545007952)
Fichier : `sections/loven-churn.liquid` (md5 avant modification : 6d0a9ef7f67399bd338d36cc90b29596, 9 460 octets)
Raison : Shopify bloque l'écriture par API sur le thème publié, collage manuel dans l'éditeur de code.

## 1. Insérer après la fermeture du `<p class="lvn-churn__lead">…</p>` (dans `.lvn-churn__head`)

```liquid
      {%- assign lr = collections['love-room'] -%}
      {%- if lr != blank and lr.products_count > 0 -%}
        <p class="lvn-churn__more">
          Retrouvez toute notre sélection <a href="{{ lr.url }}" data-loven-link="churn-love-room">love room</a> en France, adresse par adresse.
        </p>
      {%- endif -%}
```

## 2. Ajouter dans le bloc `<style>`, après la règle `.lvn-churn__lead`

```css
  #lvn-churn .lvn-churn__more{margin:12px 0 0;font-size:15px;line-height:1.6;color:#444444}
  #lvn-churn .lvn-churn__more a{color:#E83F4E;font-weight:700;text-decoration:underline}
```

## Contrôle après collage (agent)

- Une fiche L6 renvoie 200, contient exactement un `<a href="/collections/love-room"` avec l'ancre « love room ».
- Aucune régression : grille, CTA et JSON-LD ItemList toujours présents.
- md5 du fichier relevé et noté au journal.
