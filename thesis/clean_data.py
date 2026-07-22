
import pandas as pd
import re
import os

def clean_vehicular_flow_data(input_csv_path, output_excel_path):
    """
    Cleans and consolidates vehicular flow data.

    Args:
        input_csv_path (str): Path to the raw CSV file.
        output_excel_path (str): Path to save the cleaned Excel file.

    Returns:
        pd.DataFrame: The cleaned and consolidated DataFrame.
    """
    print(f"📖 Leyendo el archivo CSV original desde: {input_csv_path}")
    df = pd.read_csv(input_csv_path, sep=None, engine='python', encoding='latin1')

    # Limpieza 1: Eliminar filas vacías
    df_clean = df.dropna(subset=['ALIAS', 'CRUCE']).copy()

    # Limpieza 2: Extraer la fecha limpia
    df_clean['FECHA_LIMPIA'] = pd.to_datetime(df_clean['ALIAS'].str[:10], dayfirst=True)

    # Limpieza 3: Extraer la parte del sensor y remover sufijos
    df_clean['SENSOR_PART'] = df_clean['ALIAS'].str[10:]
    def limpiar_sufijo(sensor_id):
        cleaned = re.sub(r'([A-Za-z]+)$', '', str(sensor_id).strip())
        return cleaned.rstrip('_- ')

    df_clean['CODIGO_SENSOR'] = df_clean['SENSOR_PART'].apply(limpiar_sufijo)

    # Limpieza 4: Asegurar valores numéricos en las horas y rellenar vacíos con 0
    horas_cols = [f"{i:02d}" for i in range(24)]
    for col in horas_cols:
        df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce').fillna(0)

    # Limpieza 5: Consolidar agrupando por sensor físico y tomando el valor máximo
    print("🔄 Consolidando flujos redundantes por valor máximo hora por hora...")
    df_consolidado = df_clean.groupby(
        ['FECHA_LIMPIA', 'CODIGO_SENSOR', 'CRUCE', 'SENTIDO']
    )[horas_cols].max().reset_index()

    # Nueva Limpieza: Eliminar filas donde todos los valores de las horas son 0
    print("🗑️ Eliminando filas con todos los registros de horas en cero...")
    df_consolidado = df_consolidado[df_consolidado[horas_cols].sum(axis=1) > 0].reset_index(drop=True)

    # Ordenar los datos cronológica y espacialmente
    df_consolidado = df_consolidado.sort_values(by=['FECHA_LIMPIA', 'CODIGO_SENSOR']).reset_index(drop=True)

    # --- EXPORTAR --- (Opcional, puede ser manejado externamente o en el bloque main)
    if output_excel_path:
        print(f"💾 Guardando archivo limpio en formato EXCEL en: {output_excel_path}")
        df_consolidado.to_excel(output_excel_path, index=False)

    print("🎉 ¡Proceso de limpieza completado con éxito!")

    return df_consolidado

if __name__ == '__main__':
    # Este bloque solo se ejecuta si el script se corre directamente
    # No se ejecutará si se importa como módulo
    
    # Ajusta estas rutas si usas este script fuera de Colab o con un repositorio diferente
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_csv = os.path.join(repo_root, "data", "FCONTEO POR HORAS ENERO 2025-2.csv") # Ajusta el nombre de tu archivo CSV si es diferente
    output_excel = os.path.join(repo_root, "data", "flujo_vehicular_quito_consolidado.xlsx")
    
    print("Ejecutando clean_data.py como script principal...")
    # Asegúrate de que el archivo de entrada exista antes de intentar limpiarlo
    if not os.path.exists(input_csv):
        print(f"Error: El archivo de entrada '{input_csv}' no se encontró. Asegúrate de que esté en la ubicación correcta.")
    else:
        cleaned_df = clean_vehicular_flow_data(input_csv, output_excel)
        print("DataFrame consolidado resultante (primeras 5 filas):")
        print(cleaned_df.head())
