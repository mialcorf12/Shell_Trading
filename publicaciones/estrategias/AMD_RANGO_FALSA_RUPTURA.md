# AMD_RANGO_FALSA_RUPTURA: Modelo Acumulación-Manipulación-Distribución con Falsa Ruptura de Rango en NQ/MNQ

## 1. Hipótesis Operativa
El modelo AMD describe tres fases de un movimiento de precio dentro de una sesión:

1. **Acumulación:** el precio queda encerrado en un rango lateral. Se acumulan órdenes stop por encima del máximo y por debajo del mínimo del rango.
2. **Manipulación (falsa ruptura):** el precio sale del rango, barre esa liquidez y falla: vuelve a entrar al rango. Los stops de los operadores de ruptura quedan llenados por el otro lado.
3. **Distribución (expansión):** tras la manipulación, el precio se mueve con fuerza en la dirección contraria a la falsa ruptura, hacia el lado opuesto del rango.

La hipótesis es que una falsa ruptura confirmada por reentrada al rango anticipa una expansión en sentido contrario, con un stop razonable (por encima o debajo de la mecha de manipulación) y un objetivo en el lado opuesto del rango.

---

## 2. Parámetros de Mercado e Instrumentos
- **Contratos:** MNQ ($2.00/punto, $0.50/tick) para ejecución; NQ ($20.00/punto) solo con riesgo acotado al colchón de drawdown.
- **Sesión:** RTH (09:30–16:00 ET). Ventana preferida: 09:45–11:30 ET.
- **Temporalidades:**
  - Rango de acumulación: 15 o 30 minutos (una sola definición, fijada antes del backtest).
  - Confirmación de manipulación y gatillo: 1 o 3 minutos.
- **Definición medible de rango:** máximo y mínimo de las velas de acumulación. Se valida que el rango tenga entre 25 y 90 puntos NQ, y que el precio haya pasado al menos 3 velas dentro de él.

---

## 3. Definiciones Medibles (eliminar la ambigüedad del video)
- **Falsa ruptura alcista (manipulación):** una vela de 1 o 3 min cierra por encima del máximo del rango, y en las siguientes 3 velas el precio cierra de nuevo dentro del rango. Una ruptura de solo mecha no cuenta como ruptura.
- **Reentrada válida:** cierre de vela de 1 min dentro del rango, con el precio a menos de 3 puntos de la línea del rango (no se exige cierre en el punto exacto).
- **Expansión confirmada:** una vela de 3 min con cuerpo ≥ 60% de su rango cierra en dirección opuesta a la manipulación, por fuera del punto medio del rango.

El término "barrido de liquidez" del video no tiene definición cuantitativa; se opera con la falsa ruptura definida arriba.

---

## 4. Reglas de Entrada

### Configuración Corta (falsa ruptura alcista):
1. **Acumulación:** rango de 15 min definido. Máximo y mínimo fijados.
2. **Manipulación:** falsa ruptura por encima del máximo (sección 3).
3. **Reentrada:** el precio vuelve al rango. Se marca el máximo de la mecha de manipulación (`ManipHigh`).
4. **Gatillo:** una vela de 3 min cierra con cuerpo bajista por debajo del punto medio del rango, confirmando la expansión.
5. **Entrada:** venta a mercado al cierre de esa vela, o limit en el máximo del cuerpo de la vela de reentrada en un retesteo.

### Configuración Larga (falsa ruptura bajista):
- Espejo: ruptura por debajo del mínimo del rango, reentrada, vela alcista de 3 min con cuerpo por encima del punto medio, compra.

---

## 5. Gestión de Riesgo y Salida

- **Hard Stop Loss:** por encima de `ManipHigh` (corto) o por debajo de `ManipLow` (largo), con 2 ticks de margen.
  - Distancia máxima de stop: 30 puntos NQ ($60 en MNQ). Si la mecha de manipulación exige más, la operación se descarta.
- **Take Profit:**
  - TP1 (50%): en el punto medio del rango, o a 1.0 R, lo que ocurra primero.
  - TP2 (50%): en el lado opuesto del rango (mínimo del rango en corto). Ratio mínimo 1:2 sobre el stop; si el lado opuesto está a menos de 2 R, no operar.
- **Break Even:** al llenarse TP1, stop del resto a +2 ticks.
- **Invalidación:** un cierre de vela de 3 min por encima de `ManipHigh` (corto) antes de TP1 indica que la falsa ruptura era ruptura real: salida inmediata a mercado.

---

## 6. Reglas de Cuenta Fondeada (Prop Firm Compliance)
- **Riesgo por operación:** máximo 0.75% del trailing drawdown real. Ejemplo: $2,000 de DD → $150 de riesgo → con stop de 25 puntos en MNQ ($50/contrato), 3 contratos.
- **Máximo 2 operaciones por sesión**; tras una pérdida, no reentrar en el mismo rango.
- **Sin promediar ni ampliar stop.**
- **Cierre forzoso:** flat antes de las 15:55 ET.

---

## 7. Validación Pendiente
- El material fuente (infografía promocional de otra cuenta) no muestra precios, rango de tamaño ni estadística. La hipótesis no está probada.
- El claim de "80% de efectividad" no tiene sustento y se descarta como evidencia.
- Backtest con costos reales y slippage. Walk-forward para validar el umbral de amplitud (25–90 pts) y la definición de reentrada (3 pts).
- Muestra mínima: ≥ 100 operaciones. Reportar distribución por día para evitar que un solo día concentre la utilidad.

---

## 8. Arquitectura NinjaTrader 8 (NinjaScript)
- Series: 15 min (rango), 3 min (confirmación), 1 min (manipulación y reentrada).
- Máquina de estados: `Acumulacion → Rango_Definido → Manipulacion_Detectada → Reentrada → Expansion_Confirmada → EnPosicion → Cerrado`.
- Órdenes con `SetStopLoss` y `SetProfitTarget` por precio tras la entrada.

---

## Referencias
- Ideas: [[AMD_RANGO_FALSA_RUPTURA_01]]
- Fuentes y research:
  - Publicación de origen (@alanmiqueas.tt): modelo AMD en NQ (contenido promocional; sin estadística verificable).
  - jira/trading_agent_persona.md: Hipótesis antes que código, validación fuera de muestra y trailing drawdown.
