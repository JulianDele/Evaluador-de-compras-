# Archivos de datos de ejemplo

Esta carpeta contiene archivos de muestra para probar la funcionalidad de importación.

## Archivos disponibles

| Archivo | Formato | Descripción |
|---------|---------|-------------|
| `compras_ejemplo.csv` | CSV | 8 compras de ejemplo con encabezados en español |

## Cómo usar

1. Inicia sesión como **admin** en la aplicación
2. En la pantalla principal, haz clic en **"Importar datos"**
3. Arrastra o selecciona el archivo `compras_ejemplo.csv`
4. Verifica el mapeo de columnas (deberían detectarse automáticamente)
5. Revisa la vista previa y confirma la importación

## Formato esperado para importación

El sistema acepta archivos con las siguientes columnas (los nombres pueden variar,
el sistema intenta detectarlos automáticamente):

| Campo requerido | Nombres aceptados |
|----------------|-------------------|
| Nombre         | nombre, name, cliente, usuario |
| Producto       | producto, product, item, articulo |
| Cantidad       | cantidad, quantity, qty, cant |
| Fecha          | fecha, date, purchase_date |
| Precio         | precio, price, monto, importe |

| Campo opcional | Nombres aceptados |
|----------------|-------------------|
| Hora           | hora, time, purchase_time |
| Método de pago | metodo_pago, payment_method, pago |

## Crear tu propio archivo de prueba

Para crear un archivo Excel (.xlsx) de prueba, puedes usar este script Python:

```python
import pandas as pd

data = {
    'Nombre':           ['Usuario Ejemplo', 'Usuario Ejemplo'],
    'Producto':         ['Producto A',      'Producto B'],
    'Cantidad':         [2,                 3],
    'Fecha':            ['2024-01-15',      '2024-01-16'],
    'Hora':             ['10:00',           '14:30'],
    'Precio':           [50.00,             75.00],
    'Método de Pago':   ['Efectivo',        'Tarjeta'],
}

df = pd.DataFrame(data)
df.to_excel('mi_archivo.xlsx', index=False)
print("Archivo creado: mi_archivo.xlsx")
```
