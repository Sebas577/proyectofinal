from config import app
from config.app import *
from modelos.model import *
import pandas as pd
from datetime import datetime
from rich.console import Console
from rich.table import Table
import sqlite3

def IngestDataProducts(app:App):
    bd=app.bd
    conn=bd.getConection()
    dataPais=GetDataSourcePais()
    CreateTablesPais(conn)
    InsertDataPais(bd,dataPais)
    dataPostalCode=GetDatoSourcePostalCode()
    CreateTablePostalCode(conn)
    InsertDataPostalCode(bd,dataPostalCode)
    dataCategories=GetDataSourceCategories()
    createTableCategories(conn)
    InsertManyCategories(bd,dataCategories)
    dataProducts=GetDataSourceProductos(conn)
    createTableProducts(conn)
    InsertManyProducts(bd,dataProducts)
    dataVentas=GetDatasourceOrders(conn)
    createTableVentas(conn)
    insertManyVentas(bd,dataVentas)
    generarIndicadores(bd,dataCategories)
    GenerateCustomReport(bd,dataProducts)
    Gestionpostal(bd,dataPostalCode)
    



def generarIndicadores(app:App):
    bd=app.bd
    conn=bd.getConection()
    query="Select * from ventas"
    df=pd.read_sql_query(query,conn)
    print(df.head())    


def IngestDataProducts(app:App):   
    try:
        file_path = "/workspaces/proyectofinal/files/datafuente.xls"

        df_data_fuente = pd.read_excel(file_path)

        print("\n📊 [INFO] Datos del archivo Excel cargados correctamente:")
        print(df_data_fuente.head())

    except Exception as e:
        print(f"❌ [ERROR] Ocurrió un problema al cargar los datos: {e}")


def GenerateCustomReport(app:App):
    console = Console() 
    path_ = "/workspaces/proyectofinal/files/datafuente.xls"
    
    try:
        df_excel = pd.read_excel(path_, usecols=['Product ID', 'Region','Sub-Category','Quantity','Discount'])
        
        if df_excel.empty:
            console.print("[yellow]No se encontraron registros en el archivo Excel.[/yellow]")
            return

        console.print("[green]Datos cargados correctamente desde el archivo Excel.[/green]")
        console.print(df_excel.head())
    
    except Exception as e:
        console.print(f"[red]Error al leer el archivo Excel: {e}[/red]")


console = Console()
def Gestionpostal(app):
    try:
        console.rule("[bold cyan]🔍 Iniciando proceso de Gestión de Códigos Postales")

        excel_path = "/workspaces/proyectofinal/files/datafuente.xls"
        df = pd.read_excel(excel_path, sheet_name="Orders")
        console.print(f"📂 [green]Datos cargados desde:[/green] {excel_path} [yellow]({df.shape[0]} filas, {df.shape[1]} columnas)[/yellow]")
        required_columns = ['Country', 'Postal Code']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            console.print(f"❌ [red]Columnas faltantes:[/red] {missing_columns}")
            return None
        df_subset = df[required_columns].dropna().copy()
        console.print(f"📊 [blue]Datos filtrados y limpiados:[/blue] {df_subset.shape[0]} registros")
        table = Table(title="Vista Previa de los Datos a Insertar")
        table.add_column("Country", style="cyan")
        table.add_column("Postal Code", style="magenta")

        for _, row in df_subset.head().iterrows():
            table.add_row(str(row["Country"]), str(row["Postal Code"]))

        console.print(table)

        db_path = "/workspaces/proyectofinal/datux.db"
        conn = sqlite3.connect(db_path)

        with conn:
            cursor = conn.cursor()
            cursor.executemany("INSERT INTO POSTALCODE (pais, codigo_postal) VALUES (?, ?)", df_subset.values.tolist())
            conn.commit()

        console.print("✅ [green]Datos insertados correctamente en la tabla POSTALCODE.[/green]")
        return df_subset.head()

    except FileNotFoundError:
        console.print(f"❌ [red]Error: No se encontró el archivo {excel_path}[/red]")
    except (TypeError, KeyError, sqlite3.Error) as e:
        console.print(f"❌ [red]Error:[/red] {e}")
    except Exception as e:
        console.print(f"❌ [red]Error inesperado:[/red] {e}")

def GetDataSourcePais():
    pathData="/workspaces/proyectofinal/files/datafuente.xls"
    df=pd.read_excel(pathData,sheet_name="Orders")
    print(df.shape)
    print(df.keys())
    df_country=df['Country'].unique()
    print(df_country.shape)
    country_tuples = [(country,) for country in df_country] 
    return country_tuples

def CreateTablesPais(conn:Connection):
    pais=Pais()
    pais.create_table(conn)
    
def InsertDataPais(bd:Database,data):
    bd.insert_many('PAIS',['name'],data)

def GetDatoSourcePostalCode():
    pathData="/workspaces/proyectofinal/files/datafuente.xls"
    df=pd.read_excel(pathData,sheet_name="Orders")
    df['Postal Code'] = df['Postal Code'].astype(str)
    df_postalCode=df[['Postal Code','Country','State']]
    df_postalCode=df_postalCode.dropna()
    df_postalCode=df_postalCode.drop_duplicates()

    print(df_postalCode.head())
    postal_code_tuples=[tuple(x) for x in df_postalCode.to_records(index=False)]
    return postal_code_tuples

def CreateTablePostalCode(conn:Connection):
    postalCode=PostalCode()
    postalCode.create_table(conn)

def InsertDataPostalCode(bd:Database,data):
    bd.insert_many('POSTALCODE',['code','pais','state'],data)

def GetDataSourceCategories():
    pathData="/workspaces/proyectofinal/files/datafuente.xls"
    df=pd.read_excel(pathData,sheet_name="Orders")
    df_categories=df[['Category','Sub-Category']].dropna().drop_duplicates()
    categories_tuples=[tuple(x) for x in df_categories.to_records(index=False)]
    return categories_tuples

def createTableCategories(conn:Connection):
    categories=Categorias()
    categories.create_table(conn)

def InsertManyCategories(bd:Database,data):
    bd.insert_many('CATEGORIAS',['name','subcategory'],data)

def GetDataSourceProductos(app):
    try:
        bd = app.bd
        conn = bd.getConection()

        if conn is None:
            print("Error: No se pudo establecer conexión con la base de datos.")
            return None
        query = "SELECT * FROM PRODUCTOS"
        df = pd.read_sql_query(query, conn)
        conn.close()
        if df.empty:
            print("Advertencia: No se encontraron productos en la base de datos.")
            return None
        
        print(f"📊 Datos obtenidos: {df.shape[0]} registros encontrados.")
        print(df.head())

        return df

    except sqlite3.Error as e:
        print(f"Error de base de datos: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado: {e}")
        return None

 


def createTableProducts(conn:Connection):
    productos=Productos()
    productos.create_table(conn)

def InsertManyProducts(bd:Database,data):
    bd.insert_many('PRODUCTOS',['product_id','name','category_id'],data)

def GetDatasourceOrders(conn):
    pathData="/workspaces/proyectofinal/files/datafuente.xls"
    df=pd.read_excel(pathData,sheet_name="Orders")
    df_products=pd.read_sql_query("SELECT id,name,product_id FROM PRODUCTOS",conn)
    df_orders=df[['Order ID','Postal Code','Product ID','Sales','Quantity','Discount','Profit','Shipping Cost','Order Priority']].dropna().drop_duplicates()
    df_orders['Postal Code'] = df_orders['Postal Code'].astype(str)
    print('shape orders',df_orders.shape)
    df_newOrders=df_orders.merge(df_products,how="left",left_on="Product ID",right_on="product_id")
    df_newOrders=df_newOrders.drop_duplicates()
    print('shape orders 1',df_newOrders.shape)
    df_newOrders=df_newOrders[['Order ID','Postal Code','id','Sales','Quantity','Discount','Profit','Shipping Cost','Order Priority']]
    list_tuples=[tuple(x) for x in df_newOrders.to_records(index=False)]
    return list_tuples

def createTableVentas(conn):
    ventas=Ventas()
    ventas.create_table(conn)

def insertManyVentas(bd:Database,data):
    bd.insert_many('VENTAS',['order_id','postal_code','product_id','sales_amount','quantity','discount','profit','shipping_cost','order_priority'],data)                                   









    