# Pasos

## 1. Zona horaria: en NT8, andá a Tools → Options → General y revisá la zona horaria. Usá la misma que quieras para el backtest, por ejemplo Eastern Time. Las horas del CSV salen en esa zona.
 
## 2. Carpeta: creá C:\ShellTrading\data\. El exportador no crea la carpeta.
 
## 3. Despliegue de Estrategias en NinjaTrader 8

- 1. Copiar las clases C# a la carpeta de NinjaTrader: (Ninjatrader cerrado)
   ```cmd
   copy C:\ShellTrading\data\ExportBars.cs "C:\Users\Administrator\Documents\NinjaTrader 8\bin\Custom\Strategies\"
   ```

- 2. En NinjaTrader 8:
   - Abrir NinjaTrader 8 Desktop.
   - Ir a **Tools** > **NinjaScript Editor** (F5 para compilar).
   - Verificar que compile con cero errores.

## 4. Abrir el gráfico: abrí NQ en 1 minuto. Para el contrato, usá el continuo o back-adjusted, para que el salto entre vencimientos no distorsione los precios.
 
## 5. Cargar historial: en las propiedades del gráfico (Data Series), subí Days to load al máximo que te permita tu proveedor, por ejemplo 365.

## 6. Agregar el indicador: en el gráfico, Indicators → ExportBars. Revisá que Ruta del CSV sea C:\ShellTrading\data\nq_1m.csv.

## 7. Esperar la carga: el archivo se escribe mientras NT8 recorre el historial. Cuando termine, podés cerrar el gráfico o el indicador para que se cierre el archivo.

- Cómo verificar: abrí el CSV. La primera línea debe ser datetime,open,high,low,close,volume, y después una vela por línea.

## guarda el archivo en mac