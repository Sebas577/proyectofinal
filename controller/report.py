from config.app import *
import pandas as pd

def GenerateReportVentas(app: App):
    conn = app.bd.getConection()
    query = """
        SELECT 
            p.pais,
            v.product_id,
            pr.name AS product_name,
            SUM(v.quantity) AS total_vendido
        FROM 
            VENTAS v
        JOIN 
            POSTALCODE p ON v.postal_code = p.code
        JOIN 
            PRODUCTOS pr ON v.product_id = pr.product_id
        GROUP BY 
            p.pais, v.product_id, pr.name
        ORDER BY 
            total_vendido DESC;
    """
    df = pd.read_sql_query(query, conn)
    
    fecha = "08-02"
    path = f"/workspaces/proyectofinal/files/reporte-productos-{fecha}.csv"
    df.to_csv(path, index=False)
    
    top_product = df.iloc[0] if not df.empty else None
    product_id = top_product["product_id"] if top_product is not None else "N/A"
    product_venta = top_product["total_vendido"] if top_product is not None else 0
    
    
    subject = f"Reporte de Ventas - Producto: {product_id} (Ventas: {product_venta})"
    
    sendMail(app, path, subject)


def sendMail(app: App, data, subject):
    app.mail.send_email('from@example.com', subject, 'Reporte de ventas adjuntado', data)
