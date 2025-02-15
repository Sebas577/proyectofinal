from controller.menu import menu
from config.app import App

def main():
    try:
        app = App('/workspaces/proyectofinal/datux.db')
        menu(app)
    except Exception as e:
        print(f"[ERROR] Ocurrió un problema: {e}")
    finally:
        print("Aplicación finalizada correctamente.")

if __name__ == "__main__":
    main()
