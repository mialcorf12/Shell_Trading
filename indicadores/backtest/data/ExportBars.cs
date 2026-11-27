#region Using declarations
using System;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using System.Globalization;
using System.IO;
using System.Windows;
using System.Windows.Media;
using NinjaTrader.Cbi;
using NinjaTrader.Gui;
using NinjaTrader.NinjaScript;
#endregion

// Exporta las velas cerradas del gráfico a un CSV: datetime,open,high,low,close,volume
// Uso: agregar a un gráfico de NQ (1 minuto) con suficiente historial cargado.
namespace NinjaTrader.NinjaScript.Indicators
{
    public class ExportBars : Indicator
    {
        private StreamWriter writer;
        private int written;

        [NinjaScriptProperty]
        [Display(Name = "Ruta del CSV", Description = "Carpeta debe existir", Order = 1, GroupName = "Parámetros")]
        public string FilePath { get; set; }

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = "Exporta las velas cerradas a CSV para el backtest de Shell_Trading.";
                Name = "ExportBars";
                Calculate = Calculate.OnBarClose;
                IsOverlay = true;
                DisplayInDataBox = false;
                FilePath = @"C:\ShellTrading\data\nq_1m.csv";
            }
            else if (State == State.DataLoaded)
            {
                writer = new StreamWriter(FilePath, false);
                writer.WriteLine("datetime,open,high,low,close,volume");
                written = 0;
            }
            else if (State == State.Terminated)
            {
                if (writer != null)
                {
                    writer.Flush();
                    writer.Close();
                    writer = null;
                }
            }
        }

        protected override void OnBarUpdate()
        {
            // Solo serie principal. Con Calculate.OnBarClose, al cerrar la vela actual
            // la anterior ya está completa: se escribe Time[1], Open[1], etc.
            if (BarsInProgress != 0 || CurrentBar < 1 || writer == null)
                return;

            writer.WriteLine(string.Format(CultureInfo.InvariantCulture,
                "{0:yyyy-MM-dd HH:mm:ss},{1},{2},{3},{4},{5}",
                Time[1], Open[1], High[1], Low[1], Close[1], Volume[1]));
            written++;
            if (written % 5000 == 0)
                writer.Flush();
        }
    }
}
