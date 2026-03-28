Auto-persistència de memòria a OpenClaw (proposta per a Joel)

Objectiu:
- Garantir que totes les converses i preferències quedin enregistrades i accessibles després de reinicis de l’ordinador.

Abast:
- Sessions actuals i futures
- Preferències d’usuari (idioma, zona horària, format de data, preferències de sortida)
- Decisions clau, resums de tasques i resultats

Mecanismes proposats:
- Emmagatzematge a la memòria persistent: MEMORY.md (accés global a llarg termini)
- Per cada sessió, crear memory/YYYY-MM-DD-session-summary.md amb:
  - sessionKey i sessionId
  - resums de la sessió (temes principals, decisions, properes accions)
  - enllaços a sources i a notes relacionades
  - estat de persistència
- Sincronització entre la memòria persistent i les sessions actuals; revisió periòdica de consistència

Consideracions:
- Aquestes accions requeriran confirmació per donar permisos i per la creació de fitxers addicionals.
- Mantenir les dades amb un nivell de privacitat adequat i evitar l’exfiltració de dades sensibles.

Comprovar/Activar:
- Si estàs d’acord, puc activar aquesta guia implícita i començar a generar resums i documents de sessió automàtics a mesura que avancem. Esperaré la teva aprovació per a automatitzar completament el flux.