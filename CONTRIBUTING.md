# Contribuir a CloudPath ES

## Checklist para cambios cross-layer

Cuando modifiques un endpoint, modelo o tipo que cruza la frontera backend ↔ frontend, verifica cada punto antes de abrir PR:

1. **Schema backend** — ¿Cambiaste el modelo Pydantic? Actualiza `src/types/exam.ts` o regenera con `npm run gen:types`.
2. **Rutas nuevas** — ¿Añadiste un endpoint? Agrega el wrapper correspondiente en `frontend/src/api/client.ts`.
3. **Renombrado de campo** — ¿Renombraste un campo JSON? Busca todos los usos en frontend con `grep -r "campo_viejo" src/`.
4. **Multi-respuesta** — ¿Tocaste lógica de `correct_indices`? Verifica `ExplanationPanel`, `QuestionCard` y los tres modos (Exam, Study, Review).
5. **ChromaDB metadata** — ¿Añadiste un campo a la metadata de ChromaDB? Borra `data/chroma/` para forzar re-indexado.
6. **SQLite schema** — ¿Cambiaste `schema.sql`? Elimina `data/cloudpath.db` en dev para aplicar la migración.
7. **Tests de integración** — ¿Rompiste algún test en `backend/tests/test_integration.py`? Corrígelo antes de hacer merge.
8. **domain_progress** — ¿Agregaste un nuevo modo de respuesta? Llama a `update_domain_progress()` desde `exam.session`.
9. **Tutor context** — ¿Añadiste una página nueva? Publica el contexto con `setTutorContext({ page: '...' })` en un `useEffect`.
10. **Guardrails** — ¿El tutor puede recibir texto de usuario libre en ese flujo? Revisa `backend/tutor/guardrails.py`.
